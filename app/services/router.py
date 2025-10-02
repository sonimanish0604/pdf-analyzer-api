# router.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .deps_db import get_session

router = APIRouter()

@router.get("/users/{uid}")
async def get_user(uid: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(User)
        .options(selectinload(User.roles))
        .where(User.id == uid)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "not found")
    return {"id": user.id, "email": user.email, "roles": [r.name for r in user.roles]}