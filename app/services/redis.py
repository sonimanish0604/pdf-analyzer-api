from functools import lru_cache
from redis.asyncio import Redis
from app.core.config import get_settings

@lru_cache
def _client() -> Redis:
    s = get_settings()
    # Cast AnyUrl -> str for redis-py
    url_str = str(s.REDIS_URL)
    return Redis.from_url(
        url_str,
        encoding="utf-8",
        decode_responses=True,
    )

def get_redis() -> Redis:
    return _client()