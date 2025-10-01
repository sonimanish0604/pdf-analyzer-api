from functools import lru_cache
from redis.asyncio import Redis
from app.core.config import get_settings

@lru_cache
def _client() -> Redis:
    url = get_settings().REDIS_URL or "redis://localhost:6379/0"
    return Redis.from_url(url, encoding="utf-8", decode_responses=True)

def get_redis() -> Redis:
    return _client()