# app/api/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.api.deps_db import get_session
from app.models import User  # your ORM model

router = APIRouter()

@router.get("/users/{uid}")
async def get_user(uid: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(User)
        .options(selectinload(User.roles))  # eager load roles
        .where(User.id == uid)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    return {"id": user.id, "email": user.email, "roles": [r.name for r in user.roles]}