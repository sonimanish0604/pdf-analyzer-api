# app/api/deps_auth.py
import os
from fastapi import Header, HTTPException

ADMIN_KEY = os.getenv("ADMIN_KEY", "")

async def verify_admin_key(x_admin_key: str = Header(None)):
    # Fail closed by default if ADMIN_KEY unset
    if not ADMIN_KEY:
        raise HTTPException(status_code=503, detail="Admin auth not configured")
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: invalid admin key")
    return True