from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.services.rate_limit_introspect import effective_limits
from app.api.deps_auth import verify_admin_key  # your existing admin-key verifier

router = APIRouter()

@router.get("/admin/rate-limits", dependencies=[Depends(verify_admin_key)])
async def get_rate_limits():
    return JSONResponse(content=await effective_limits())