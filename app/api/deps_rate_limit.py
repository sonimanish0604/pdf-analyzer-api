# app/services/deps_rate_limit.py
import os
import time
from fastapi import Depends, HTTPException, Request
from app.services.redis import get_redis
from app.services.limits import get_limits_for

NAMESPACE = os.getenv("REDIS_NAMESPACE", "pdfapi")
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"

# --- replace this with your real key lookup if you have one ---
async def load_key_info(request: Request):
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(401, "Missing X-API-Key")

    # If some upstream auth sets request.state.plan, prefer it; else default to 'free'
    plan = getattr(request.state, "plan", None) or "free"

    # Treat api_key as kid for now; adjust when you add DB lookup
    return {"kid": api_key, "plan": plan, "status": "active"}

def _today_str() -> str:
    return time.strftime("%Y%m%d", time.gmtime())

async def enforce_rate_limit(request: Request):
    """Adapter so middleware can reuse the dependency logic."""
    keyinfo = await load_key_info(request)
    await rate_limiter(keyinfo)

async def rate_limiter(keyinfo: dict):
    if not RATE_LIMIT_ENABLED:
        return

    if keyinfo.get("status") != "active":
        raise HTTPException(403, "API key inactive")

    kid  = keyinfo["kid"]
    plan = keyinfo.get("plan", "free")

    # get_limits_for(plan) should read from env (not hardcoded), returning (rps, burst, daily)
    rps, burst, daily = await get_limits_for(plan)

    r = get_redis()

    # 0) optional soft block (keep as-is / off by default)
    if await r.get(f"{NAMESPACE}:block:{kid}"):
        raise HTTPException(429, "Temporarily blocked due to repeated limit violations")

    # 1) Daily quota (fixed window by day)
    day_key = f"{NAMESPACE}:usage:{kid}:{_today_str()}"
    used_today = await r.incr(day_key)
    if used_today == 1:
        # expire next day; 2 days is a safe cushion
        await r.expire(day_key, 172800)
    if daily and used_today > daily:
        raise HTTPException(429, f"Daily quota exceeded ({daily})")

    now = int(time.time())

    # 2) RPS check (fixed one-second window)
    #    This gives a precise "requests per second" signal separate from the burst bucket.
    sec_bucket = now  # current second epoch
    rps_key = f"{NAMESPACE}:rps:{kid}:{sec_bucket}"
    rps_used = await r.incr(rps_key)
    if rps_used == 1:
        await r.expire(rps_key, 2)  # expire just after the window
    if rps and rps_used > rps:
        # Optional: roll back day counter to avoid drift during spikes
        # await r.decr(day_key)
        raise HTTPException(429, f"Requests per second exceeded ({rps})")

    # 3) Burst allowance (token bucket with capacity=burst, refill=rps tokens/sec)
    #    Simple, readable implementation: track last refill second + available tokens.
    tkey = f"{NAMESPACE}:rl:{kid}:tokens"
    lkey = f"{NAMESPACE}:rl:{kid}:last"

    tokens_raw = await r.get(tkey)
    last_raw = await r.get(lkey)

    tokens = int(tokens_raw) if tokens_raw is not None else burst
    last   = int(last_raw)   if last_raw   is not None else now

    # refill based on elapsed full seconds
    elapsed = max(0, now - last)
    if rps and elapsed > 0:
        tokens = min(burst, tokens + elapsed * rps)

    # update last seen second
    await r.set(lkey, now, ex= max(5, 2))  # short TTL is fine; we rewrite each call

    if tokens >= 1:
        tokens -= 1
        # TTL should be at least the time needed to fully refill from empty
        refill_seconds = (burst // rps) + 2 if rps else 5
        await r.set(tkey, tokens, ex=max(5, refill_seconds))
        return  # allowed

    # Optional: enable temporary soft block if repeatedly bursting
    # await r.setex(f"{NAMESPACE}:block:{kid}", 900, "1")
    raise HTTPException(429, f"Burst allowance exceeded (capacity={burst})")