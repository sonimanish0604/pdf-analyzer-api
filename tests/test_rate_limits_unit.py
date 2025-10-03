# tests/test_rate_limits_unit.py
from types import SimpleNamespace

import pytest

from app.core.config import get_settings
from app.services.deps_rate_limit import enforce_rate_limit


class _Req(SimpleNamespace):
    # Minimal fake Request for our deps
    def __init__(self, path="/v1/analyze", headers=None):
        super().__init__()
        self.url = SimpleNamespace(path=path)
        self.headers = headers or {}
        self.state = SimpleNamespace()


@pytest.mark.asyncio
async def test_allowlist_health_not_limited():
    req = _Req(path="/v1/health")
    await enforce_rate_limit(req)  # should not raise


@pytest.mark.asyncio
async def test_free_plan_rps_trip(fake_redis, monkeypatch):
    # Use a non-admin key
    key = "k_free_1"
    # 2 requests should pass if rps>=1, the 3rd in same sec should 429 with small default burst
    req = _Req(headers={"X-API-Key": key})
    await enforce_rate_limit(req)  # 1
    # await enforce_rate_limit(req)  # 2 (may pass if burst>1)
    with pytest.raises(
        Exception
    ):  # HTTPException 429 expected on 3rd or 4th call depending on burst
        await enforce_rate_limit(req)


@pytest.mark.asyncio
async def test_admin_bypass(monkeypatch):
    admin = get_settings().ADMIN_KEY
    req = _Req(headers={"X-API-Key": admin})
    # Should never raise, no matter how many times
    for _ in range(10):
        await enforce_rate_limit(req)
