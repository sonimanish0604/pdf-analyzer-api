# tests/conftest.py
import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

# Try async fixtures; fall back gracefully if plugin not installed
ASYNC_FIXTURES = True
try:
    import pytest_asyncio
    import fakeredis.aioredis as fakeredis
except Exception:
    ASYNC_FIXTURES = False

# Only define async redis fixtures if available
if ASYNC_FIXTURES:
    @pytest_asyncio.fixture
    async def fake_redis():
        r = fakeredis.FakeRedis(decode_responses=True)
        try:
            yield r
        finally:
            await r.flushall()
            await r.aclose()

    @pytest.fixture(autouse=True)
    def patch_redis(fake_redis, monkeypatch):
        from app.services import redis as redis_service
        monkeypatch.setattr(redis_service, "get_redis", lambda: fake_redis)
else:
    # No-op fixture so tests don’t break if async plugin isn’t present
    @pytest.fixture(autouse=True)
    def _noop_patch_redis():
        pass