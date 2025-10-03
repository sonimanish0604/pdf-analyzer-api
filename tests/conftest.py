# tests/conftest.py
import os
import sys
from pathlib import Path

# Ensure repo root is importable as a package path (works in CI & local)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
import pytest_asyncio
import fakeredis.aioredis as fakeredis

from app.services import redis as redis_service


@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    # Keep limiter ON during tests; use a separate namespace
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("REDIS_NAMESPACE", "t_pdfapi")
    yield


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
    # Patch get_redis() to return our in-memory fakeredis client
    monkeypatch.setattr(redis_service, "get_redis", lambda: fake_redis)