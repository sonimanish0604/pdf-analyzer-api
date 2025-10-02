# deps_db.py
from typing import AsyncGenerator
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session