import os
import logging
from datetime import datetime, timedelta
from io import BytesIO
#-added 09/14 just space

from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import get_settings #-added 09/15 from app/main.py
from fastapi.responses import RedirectResponse, Response #-same, added from app/main
#--added 09/14
from pydantic import BaseModel
from sqlalchemy import select, insert, update, and_, text

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import json
#--added the following import- 09.14
import hmac, hashlib, secrets, uuid
#from db import SessionLocal, api_keys_table
#--added 09/14 just another table
from app.db import SessionLocal, api_keys_table, audit_admin_events


#--added 09/14--for ADMIN KEY and KEY_PEPPER
# REQUIRED secrets (env vars)
ADMIN_KEY = os.getenv("ADMIN_KEY")
if not ADMIN_KEY:
    raise RuntimeError("ADMIN_KEY is required")

KEY_PEPPER = os.getenv("KEY_PEPPER")
if not KEY_PEPPER:
    raise RuntimeError("KEY_PEPPER is required")

# Per-plan rate limits (you can override via env)
PLAN_LIMITS = json.loads(os.getenv(
    "PLAN_LIMITS_JSON",
    '{"free":"10/minute","pro":"60/minute","enterprise":"120/minute"}'
))
#---end add on 09/14

#--commenting below 09/14--ad table structure has changed--to accomodate different tenants


#def load_api_keys_from_db():
#    session = SessionLocal()
#    keys = {}
#    for row in session.execute(api_keys_table.select()):
#        keys[row.key] = row.rate_limit
#    session.close()
#    return keys

# Replace JSON loading
#API_KEY_TIERS = load_api_keys_from_db()
#-added on 09/14
PREFIX_LEN = 12  # first part users see; we store only prefix, never the secret

def _hash_key(secret: str, salt_hex: str) -> str:
    salt = bytes.fromhex(salt_hex)
    return hashlib.sha256(salt + secret.encode("utf-8") + KEY_PEPPER.encode("utf-8")).hexdigest()

def _parse_key(raw: str):
    # expects "<prefix>.<secret>"
    if not raw or "." not in raw:
        return None, None
    p, s = raw.split(".", 1)
    return p, s
#--finished adding ..09/14

# ------------------ Logging Setup ------------------
logging.basicConfig(filename="pdf_analyzer.log", level=logging.INFO)



# ------------------ FastAPI App Setup ------------------
app = FastAPI()
#--added 09/15 from app/main
def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="PDF Analyzer",
        version="1.0.0",
        docs_url="/docs" if settings.APP_ENV != "prod" else "/docs",  # keep docs on; you can disable in prod later
        openapi_url="/openapi.json",
    )

    # CORS (only if you actually need browser clients)
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=False,
            allow_methods=["POST", "GET", "OPTIONS"],
            allow_headers=["*"],
        )

    # Mount routers
    # app.include_router(v1_router, prefix="/v1")

    @app.get("/v1/health")
    def health():
        return {"ok": True, "env": settings.APP_ENV}

    return app

app = create_app()

@app.get("/", include_in_schema=False)
def root():
    # send people to the docs
    return RedirectResponse(url="/docs")

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    # no favicon; return 204 to avoid 404 spam in logs
    return Response(status_code=204)
#--done adding
from fastapi import HTTPException, Request
#--adding below to debug who is running 09/15
@app.get("/__who")
def __who():
    import pathlib, hashlib
    p = pathlib.Path(__file__)
    return {"file": str(p), "sha": hashlib.sha1(p.read_bytes()).hexdigest()[:8]}

@app.get("/__routes")
def __routes():
    return sorted([getattr(r, "path", None) for r in app.routes if getattr(r, "path", None)])
#---end of debug to test services

#--replacing /test-api-keys 09/14
#@app.get("/test-api-keys")
#async def test_api_keys(request: Request):
#    if request.headers.get("x-api-key") != "admin-key":
#        raise HTTPException(status_code=403, detail="Forbidden")
#    return {"loaded_keys": list(API_KEY_TIERS.keys())}
@app.get("/admin/echo")
def admin_echo(request: Request):
    if request.headers.get("x-admin-token") != os.getenv("ADMIN_KEY"):
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"ok": True, "plans": PLAN_LIMITS}
#--added v1 path as well
@app.get("/v1/admin/echo")
def admin_echo_v1(request: Request):
    if request.headers.get("x-admin-token") != os.getenv("ADMIN_KEY"):
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"ok": True, "plans": PLAN_LIMITS}

#--replaced 09/14

#--added 09/14 minimal create/list/revoke to avud manual SQL
from pydantic import BaseModel

class CreateKeyBody(BaseModel):
    tenant_id: str
    plan: str
    expires_at: str | None = None  # ISO8601 or null

@app.post("/admin/keys")
def admin_create_key(body: CreateKeyBody, request: Request):
    if request.headers.get("x-admin-token") != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
    if body.plan not in PLAN_LIMITS:
        raise HTTPException(status_code=400, detail=f"Unknown plan '{body.plan}'")

    # optional expiry
    expires_dt = None
    if body.expires_at:
        try:
            expires_dt = datetime.fromisoformat(body.expires_at.replace("Z","+00:00"))
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid expires_at; use ISO8601")

    prefix   = secrets.token_hex(PREFIX_LEN // 2)
    secret   = secrets.token_urlsafe(32)
    salt_hex = secrets.token_hex(16)
    key_hash = _hash_key(secret, salt_hex)
    key_id   = str(uuid.uuid4())

    s = SessionLocal()
    try:
        s.execute(insert(api_keys_table).values(
            id=key_id, tenant_id=body.tenant_id,
            key_prefix=prefix, key_hash=key_hash, salt=salt_hex,
            plan=body.plan, active=True, created_at=datetime.utcnow(),
            expires_at=expires_dt
        ))
        s.commit()
    finally:
        s.close()

    # Show full key ONCE
    return {
        "id": key_id,
        "tenant_id": body.tenant_id,
        "prefix": prefix,
        "plan": body.plan,
        "expires_at": expires_dt.isoformat() if expires_dt else None,
        "api_key": f"{prefix}.{secret}"
    }

@app.get("/admin/keys")
def admin_list_keys(request: Request, tenant_id: str | None = None):
    if request.headers.get("x-admin-token") != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
    s = SessionLocal()
    try:
        stmt = select(api_keys_table)
        if tenant_id:
            stmt = stmt.where(api_keys_table.c.tenant_id == tenant_id)
        rows = s.execute(stmt).all()
        out = []
        for (row,) in rows:
            out.append({
                "id": row.id, "tenant_id": row.tenant_id,
                "prefix": row.key_prefix, "plan": row.plan, "active": row.active,
                "created_at": row.created_at.isoformat(),
                "expires_at": row.expires_at.isoformat() if row.expires_at else None,
                "last_used_at": row.last_used_at.isoformat() if row.last_used_at else None
            })
        return {"keys": out}
    finally:
        s.close()

@app.post("/admin/keys/{key_id}/revoke")
def admin_revoke_key(key_id: str, request: Request):
    if request.headers.get("x-admin-token") != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
    s = SessionLocal()
    try:
        res = s.execute(
            update(api_keys_table)
            .where(api_keys_table.c.id == key_id)
            .values(active=False)
        )
        s.commit()
        if res.rowcount == 0:
            raise HTTPException(status_code=404, detail="Key not found")
        return {"id": key_id, "revoked": True}
    finally:
        s.close()
#---finishede 09/14
# ------------------ Rate Limiter Setup ------------------
def get_api_key_from_request(request: Request):
    #--added 09/14
    raw = request.headers.get("x-api-key")
    p, _ = _parse_key(raw) if raw else (None, None)
    #return request.headers.get("x-api-key") or get_remote_address(request)
    return p or get_remote_address(request)

#-removed below 09/14
def dynamic_limit_provider(request: Request = None):
    if request:
        key = request.headers.get("x-api-key")
        return API_KEY_TIERS.get(key, "5/minute")
    return "5/minute"
#-added below 09/14
def dynamic_limit_provider(request: Request = None):
    plan = getattr(request.state, "plan", "free") if request else "free"
    return PLAN_LIMITS.get(plan, "10/minute")

limiter = Limiter(
    key_func=get_api_key_from_request,
    default_limits=[],
    enabled=True
)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# ------------------ CORS ------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ API Key Verification ------------------
#API_KEY = os.getenv("API_AUTH_KEY")  # Optional for fixed key auth
API_KEY = os.getenv("ADMIN_KEY")  # Optional for fixed key auth -- changed 09/14
#--replacing VERIFY_API_KEY --09/14
#def verify_api_key(request: Request):
#    client_key = request.headers.get("x-api-key")
#    if not client_key or client_key not in API_KEY_TIERS:
#        raise HTTPException(status_code=403, detail="Invalid or missing API Key")
def verify_api_key(request: Request):
    raw = request.headers.get("x-api-key")
    if not raw:
        # missing → 401
        raise HTTPException(status_code=401, detail="Missing API Key")

    prefix, secret = _parse_key(raw)
    if not prefix or not secret:
        raise HTTPException(status_code=403, detail="Invalid API Key format")

    s = SessionLocal()
    try:
        row = s.execute(
            select(
                api_keys_table.c.id,
                api_keys_table.c.tenant_id,
                api_keys_table.c.key_hash,
                api_keys_table.c.salt,
                api_keys_table.c.plan,
                api_keys_table.c.active,
                api_keys_table.c.expires_at,
            ).where(and_(
                api_keys_table.c.key_prefix == prefix,
                api_keys_table.c.active == True
            ))
        ).first()

        if not row:
            raise HTTPException(status_code=403, detail="Invalid API Key")

        key_id, tenant_id, stored_hash, salt_hex, plan, active, expires_at = row
        if expires_at and datetime.utcnow() >= expires_at:
            raise HTTPException(status_code=403, detail="Expired API Key")

        # constant-time compare
        if not hmac.compare_digest(_hash_key(secret, salt_hex), stored_hash):
            raise HTTPException(status_code=403, detail="Invalid API Key")

        # attach plan/prefix for rate limiting & logs
        request.state.plan = plan
        request.state.key_prefix = prefix
        request.state.key_id = key_id
        request.state.tenant_id = tenant_id

        # best-effort last_used_at
        try:
            s.execute(update(api_keys_table).where(api_keys_table.c.id == key_id).values(last_used_at=datetime.utcnow()))
            s.commit()
        except Exception:
            s.rollback()
    finally:
        s.close()
#--finished replacing verify_api_key-09/14

# ------------------ Custom 429 Error Handler ------------------
@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    reset_time = datetime.now() + timedelta(seconds=60)
    headers = {
        "Retry-After": "60",
        #"X-RateLimit-Limit": "5",
        "X-RateLimit-Limit": dynamic_limit_provider(request),
        "X-RateLimit-Remaining": "0",
        "X-RateLimit-Reset": str(int(reset_time.timestamp()))
    }
    logging.warning(f"Rate limit exceeded for {request.client.host} - API Key: {request.headers.get('x-api-key')}")
    return JSONResponse(
        status_code=429,
        content={
            "error": "Too Many Requests",
            "code": 429,
            "detail": str(exc)
        },
        headers=headers
    )

# ------------------ Main Endpoint ------------------
@app.post("/analyze-pdf")
@limiter.limit(lambda *args, **kwargs: dynamic_limit_provider(kwargs.get("request")))
async def analyze_pdf(
    file: UploadFile = File(...),
    request: Request = None,
    _: None = Depends(verify_api_key)
):
    try:
        file_bytes = await file.read()
        file_stream = BytesIO(file_bytes)

        from pdf_utils import (
            is_true_pdf,
            is_encrypted,
            has_embedded_javascript,
            extract_urls,
            has_embedded_files_and_names,
        )

        summary = {
            "valid_pdf": is_true_pdf(BytesIO(file_bytes)),
            "encrypted": is_encrypted(BytesIO(file_bytes)),
            "embedded_javascript": False,
            "urls_found": {"safe": [], "suspicious": []}
        }

        if not summary["encrypted"]:
            summary["embedded_javascript"] = has_embedded_javascript(file_bytes)
            summary["urls_found"] = extract_urls(BytesIO(file_bytes))

            has_files, embedded_files = has_embedded_files_and_names(BytesIO(file_bytes))
            summary["embedded_files"] = has_files
            summary["embedded_file_names"] = embedded_files
        else:
            summary["embedded_files"] = False
            summary["embedded_file_names"] = []

        if not summary["valid_pdf"]:
            verdict = "❌ Invalid or spoofed PDF — rejected"
        elif summary["encrypted"]:
            verdict = "🔒 File is encrypted — cannot be scanned"
        elif summary["urls_found"]["suspicious"]:
            verdict = "🚫 File contains suspicious URLs — flagged for review"
        elif summary["embedded_javascript"] or summary["embedded_files"]:
            verdict = "⚠️ Suspicious file — contains JavaScript or embedded files"
        else:
            verdict = "✅ File appears safe"
#---------added to catch exception for 500 errors when handling files
    except Exception as e:
        logging.error("Error processing PDF: " + str(e))
        raise HTTPException(status_code=500, detail="Error processing PDF")

        
    # Logging
    #--changed 09/14, avoid logging full keys - log prefix only

    #logging.info(f"Request from {request.client.host} - API Key: {request.headers.get('x-api-key')}")
    logging.info(f"Request from {request.client.host} - KeyPrefix: {getattr(request.state, 'key_prefix','')}")

    # Rate limit headers
    remaining = "?"
    try:
        context = request.state.view_rate_limit
        if context and isinstance(context, tuple) and len(context) > 1:
            remaining = str(context[1])
    except Exception as e:
        logging.warning(f"Rate limit tracking failed: {e}")

    headers = {
        #"X-RateLimit-Limit": API_KEY_TIERS.get(request.headers.get("x-api-key"), "5/minute"),
        "X-RateLimit-Limit": dynamic_limit_provider(request),#--added 09/14 after commenting above line
        "X-RateLimit-Remaining": remaining
    }

    return JSONResponse(
        content={"summary": summary, "verdict": verdict},
        headers=headers
    )
