# app/services/limits.py
import json
import time

from app.core.config import get_settings
from app.services.redis import get_redis

_CACHE: dict[str, dict] = {"plans": None, "burst": None, "quota": None}
_TS: dict[str, float] = {"plans": 0.0, "burst": 0.0, "quota": 0.0}
_TTL = 60  # seconds


async def _load_json(key: str) -> dict:
    now = time.time()
    if _CACHE.get(key) and now - _TS[key] < _TTL:
        return _CACHE[key]
    r = get_redis()
    raw = await r.get(f"rate_limits:{key}")  # e.g., {"free":1,"dev":10,"pro":20}
    data = {}
    if raw:
        try:
            data = json.loads(raw)
        except Exception:
            data = {}
    _CACHE[key] = data
    _TS[key] = now
    return data


async def get_limits_for(plan: str) -> tuple[int, int, int]:
    """
    Returns (rps, burst, daily_quota) for the given plan.
    Priority: Redis JSON -> env defaults -> safe caps.
    """
    s = get_settings()

    plans = await _load_json("plans")  # RPS per plan
    burst = await _load_json("burst")  # Burst capacity per plan
    quota = await _load_json("quota")  # Daily quota per plan

    # Reasonable env defaults if Redis JSON not set
    # Use RATE_LIMIT_RPS as the baseline for the current plan,
    # otherwise fall back to static defaults.
    base_rps = getattr(s, "RATE_LIMIT_RPS", 2)

    env_rps = {"free": 1, "dev": max(2, base_rps), "pro": max(10, base_rps * 5)}
    env_bst = {"free": 3, "dev": 10, "pro": 40}
    env_qta = {"free": 500, "dev": 5000, "pro": 50000}

    rps = int(plans.get(plan) or env_rps.get(plan, base_rps))
    brst = int(burst.get(plan) or env_bst.get(plan, max(3, rps)))
    dquot = int(quota.get(plan) or env_qta.get(plan, 1000))

    # Guardrails
    rps = max(1, min(rps, 1000))
    brst = max(1, min(brst, 5000))
    dquot = max(1, min(dquot, 10_000_000))
    return rps, brst, dquot
