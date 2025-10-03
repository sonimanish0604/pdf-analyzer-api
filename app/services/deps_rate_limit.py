# app/services/deps_rate_limit.py
import os, time
from fastapi import HTTPException, Request
from app.core.config import get_settings
from app.services.redis import get_redis
from app.services.limits import get_limits_for

NAMESPACE = os.getenv("REDIS_NAMESPACE", "pdfapi")
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"

# One allowlist helper used by BOTH auth + limiter
# Handles /health, /v1/health, /api/v1/health, /metrics, /ready
ALLOWLIST_SUFFIXES = ("/health", "/metrics", "/ready")

def is_allowlisted(request: Request) -> bool:
    p = request.url.path.rstrip("/")
    return any(p == suf or p.endswith(suf) for suf in ALLOWLIST_SUFFIXES)

def require_api_key(request: Request):
    # Skip auth for allowlisted endpoints
    if is_allowlisted(request):
        return
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(401, "Missing X-API-Key")
    # cache for limiter
    request.state.api_key = api_key

async def enforce_rate_limit(request: Request):
    # Skip rate limits for allowlisted endpoints or when disabled
    if is_allowlisted(request) or not RATE_LIMIT_ENABLED:
        return

    api_key = getattr(request.state, "api_key", None) or request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(401, "Missing X-API-Key")

    # Option A: bypass limiter entirely when using your ADMIN_KEY
    if api_key == get_settings().ADMIN_KEY:
        return

    # Otherwise, enforce per-plan limits (free/dev/pro)
    keyinfo = {"kid": api_key, "plan": "free", "status": "active"}
    await rate_limiter(keyinfo)

def _today_str() -> str:
    return time.strftime("%Y%m%d", time.gmtime())

async def rate_limiter(keyinfo: dict):
    if not RATE_LIMIT_ENABLED:
        return

    if keyinfo.get("status") != "active":
        raise HTTPException(403, "API key inactive")

    kid  = keyinfo["kid"]
    plan = keyinfo.get("plan", "free")

    # Get per-plan limits (rps, burst, daily)
    rps, burst, daily = await get_limits_for(plan)

    r = get_redis()

    # 0) optional soft block
    if await r.get(f"{NAMESPACE}:block:{kid}"):
        raise HTTPException(429, "Temporarily blocked due to repeated limit violations")

    # 1) Daily quota (fixed daily window)
    day_key = f"{NAMESPACE}:usage:{kid}:{_today_str()}"
    used_today = await r.incr(day_key)
    if used_today == 1:
        await r.expire(day_key, 172800)  # ~2 days safety
    if daily and used_today > daily:
        raise HTTPException(429, f"Daily quota exceeded ({daily})")

    now = int(time.time())

    # 2) RPS (fixed one-second window)
    sec_bucket = now
    rps_key = f"{NAMESPACE}:rps:{kid}:{sec_bucket}"
    rps_used = await r.incr(rps_key)
    if rps_used == 1:
        await r.expire(rps_key, 2)
    if rps and rps_used > rps:
        raise HTTPException(429, f"Requests per second exceeded ({rps})")

    # 3) Burst (token bucket)
    tkey = f"{NAMESPACE}:rl:{kid}:tokens"
    lkey = f"{NAMESPACE}:rl:{kid}:last"

    tokens_raw = await r.get(tkey)
    last_raw = await r.get(lkey)

    tokens = int(tokens_raw) if tokens_raw is not None else burst
    last   = int(last_raw)   if last_raw   is not None else now

    elapsed = max(0, now - last)
    if rps and elapsed > 0:
        tokens = min(burst, tokens + elapsed * rps)

    await r.set(lkey, now, ex=max(5, 2))

    if tokens >= 1:
        tokens -= 1
        refill_seconds = (burst // rps) + 2 if rps else 5
        await r.set(tkey, tokens, ex=max(5, refill_seconds))
        return

    raise HTTPException(429, f"Burst allowance exceeded (capacity={burst})")