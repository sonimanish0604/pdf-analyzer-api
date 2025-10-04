# deps_db.py
from collections.abc import AsyncGenerator


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
