# app/services/rate_limit_introspect.py
import json
import logging
from typing import Any

from app.services.redis import get_redis  # your existing helper

LOGGER = logging.getLogger("rate_limits")

KEY_PLANS = "rate_limits:plans"  # rps per plan
KEY_BURST = "rate_limits:burst"  # burst capacity per plan
KEY_QUOTA = "rate_limits:quota"  # daily quota per plan


async def fetch_raw_limits() -> dict[str, str | None]:
    r = get_redis()
    plans, burst, quota = await r.mget(KEY_PLANS, KEY_BURST, KEY_QUOTA)
    return {"plans": plans, "burst": burst, "quota": quota}


def _loads_or_empty(s: str | None) -> dict[str, Any]:
    if not s:
        return {}
    try:
        return json.loads(s)
    except Exception:
        return {}


async def effective_limits() -> dict[str, dict[str, int]]:
    """
    Returns a dict like:
      { "free": {"rps":1,"burst":3,"daily":500}, "dev": {...}, "pro": {...} }
    Missing keys default to 0 (unlimited) for clarity.
    """
    raw = await fetch_raw_limits()
    p = _loads_or_empty(raw["plans"])
    b = _loads_or_empty(raw["burst"])
    q = _loads_or_empty(raw["quota"])

    plans = set(p.keys()) | set(b.keys()) | set(q.keys())
    result: dict[str, dict[str, int]] = {}
    for name in sorted(plans):
        result[name] = {
            "rps": int(p.get(name, 0) or 0),
            "burst": int(b.get(name, 0) or 0),
            "daily": int(q.get(name, 0) or 0),
        }
    return result


async def log_limits(context: str) -> None:
    """
    Log current limits to stdout; shows up in Render logs.
    """
    eff = await effective_limits()
    # One concise line (good for grep)
    LOGGER.info("RateLimits[%s] %s", context, json.dumps(eff, separators=(",", ":")))
