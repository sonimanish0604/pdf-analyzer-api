# tests/conftest.py
import fakeredis.aioredis as fakeredis
import pytest

from app.services import redis as redis_service


@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    # Ensure limiter ON for tests but with small numbers to run fast
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("REDIS_NAMESPACE", "t_pdfapi")
    yield


@pytest.fixture
async def fake_redis():
    r = fakeredis.FakeRedis(decode_responses=True)
    try:
        yield r
    finally:
        await r.flushall()
        await r.aclose()


@pytest.fixture(autouse=True)
def patch_redis(fake_redis, monkeypatch):
    # Patch get_redis() to return our fake client
    monkeypatch.setattr(redis_service, "get_redis", lambda: fake_redis)
