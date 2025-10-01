import json, time
from typing import Tuple, Dict
from app.core.config import get_settings
from app.services.redis import get_redis

_CACHE: Dict[str, Dict] = {"plans": None, "burst": None, "quota": None}
_TS: Dict[str, float] = {"plans": 0.0, "burst": 0.0, "quota": 0.0}
_TTL = 60  # seconds

async def _load_json(key: str) -> Dict:
    now = time.time()
    if _CACHE.get(key) and now - _TS[key] < _TTL:
        return _CACHE[key]
    r = get_redis()
    raw = await r.get(f"rate_limits:{key}")
    data = {}
    if raw:
        try:
            data = json.loads(raw)
        except Exception:
            data = {}
    _CACHE[key] = data
    _TS[key] = now
    return data

async def get_limits_for(plan: str) -> Tuple[int, int, int]:
    """
    Returns (rps, burst, daily_quota) for the given plan.
    Priority: Redis keys -> ENV -> safe defaults.
    """
    s = get_settings()

    plans = await _load_json("plans")  # {"free":1,"dev":10,"pro":20}
    burst = await _load_json("burst")  # {"free":3,"dev":10,"pro":40}
    quota = await _load_json("quota")  # {"free":500,"dev":5000,"pro":50000}

    # ENV fallbacks
    env_plans = s.plan_limits                            # {"free":2,"dev":10,"pro":20} etc.
    env_burst = {"free": 3, "dev": 10, "pro": 40}
    env_quota = {"free": 500, "dev": 5000, "pro": 50000}

    rps   = int((plans.get(plan) or env_plans.get(plan) or s.RATE_LIMIT_RPS))
    brst  = int((burst.get(plan) or env_burst.get(plan) or max(3, rps)))  # sane default
    dquot = int((quota.get(plan) or env_quota.get(plan) or 1000))

    # Guardrails
    rps   = max(1, min(rps,   1000))
    brst  = max(1, min(brst,  5000))
    dquot = max(1, min(dquot, 10_000_000))
    return rps, brst, dquot