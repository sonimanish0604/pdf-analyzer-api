# tests/test_api_integration.py
import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_open():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/v1/health")
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_analyze_rate_limited_path(fake_redis):
    # Replace `/v1/analyze` with the real protected route you have (e.g., /v1/scan)
    path = "/v1/scan"  # <-- change to your actual route name
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # First call should pass (if route exists)
        r1 = await ac.post(
            path,
            headers={"X-API-Key": "k_free_1"},
            json={"url": "https://example.com/dummy.pdf"},
        )
        # If you don't have this route yet, skip or mark xfail
        assert r1.status_code in (
            200,
            202,
            204,
            400,
            415,
        )  # "handled" is fine; we’re testing limiter path

        # Second/third may hit 429 depending on small defaults
        r2 = await ac.post(
            path,
            headers={"X-API-Key": "k_free_1"},
            json={"url": "https://example.com/dummy.pdf"},
        )
        r3 = await ac.post(
            path,
            headers={"X-API-Key": "k_free_1"},
            json={"url": "https://example.com/dummy.pdf"},
        )
        assert 429 in (r2.status_code, r3.status_code)
