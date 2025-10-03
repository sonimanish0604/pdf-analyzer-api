import asyncio
import json
import os

from redis.asyncio import Redis


async def seed():
    r = Redis.from_url(os.environ["REDIS_URL"], encoding="utf-8", decode_responses=True)
    await r.set("rate_limits:plans", json.dumps({"free": 1, "dev": 10, "pro": 20}))
    await r.set("rate_limits:burst", json.dumps({"free": 3, "dev": 20, "pro": 40}))
    await r.set(
        "rate_limits:quota", json.dumps({"free": 500, "dev": 5000, "pro": 50000})
    )
    await r.aclose()


asyncio.run(seed())
