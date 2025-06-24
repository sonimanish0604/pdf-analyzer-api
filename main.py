import os
import logging
from datetime import datetime, timedelta
from io import BytesIO
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import json

from db import SessionLocal, api_keys_table
from dotenv import load_dotenv
load_dotenv()
def load_api_keys_from_db():
    session = SessionLocal()
    keys = {}
    for row in session.execute(api_keys_table.select()):
        keys[row.key] = row.rate_limit
    session.close()
    return keys

# Replace JSON loading
API_KEY_TIERS = load_api_keys_from_db()

# ------------------ Logging Setup ------------------
logging.basicConfig(filename="pdf_analyzer.log", level=logging.INFO)



# ------------------ FastAPI App Setup ------------------
app = FastAPI()


# ------------------ Rate Limiter Setup ------------------
def get_api_key_from_request(request: Request):
    return request.headers.get("x-api-key") or get_remote_address(request)

def dynamic_limit_provider(request: Request = None):
    if request:
        key = request.headers.get("x-api-key")
        return API_KEY_TIERS.get(key, "5/minute")
    return "5/minute"


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
API_KEY = os.getenv("API_AUTH_KEY")  # Optional for fixed key auth

def verify_api_key(request: Request):
    client_key = request.headers.get("x-api-key")
    if not client_key or client_key not in API_KEY_TIERS:
        raise HTTPException(status_code=403, detail="Invalid or missing API Key")

# ------------------ Custom 429 Error Handler ------------------
@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    reset_time = datetime.now() + timedelta(seconds=60)
    headers = {
        "Retry-After": "60",
        "X-RateLimit-Limit": "5",
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
    logging.info(f"Request from {request.client.host} - API Key: {request.headers.get('x-api-key')}")

    # Rate limit headers
    remaining = "?"
    try:
        context = request.state.view_rate_limit
        if context and isinstance(context, tuple) and len(context) > 1:
            remaining = str(context[1])
    except Exception as e:
        logging.warning(f"Rate limit tracking failed: {e}")

    headers = {
        "X-RateLimit-Limit": API_KEY_TIERS.get(request.headers.get("x-api-key"), "5/minute"),
        "X-RateLimit-Remaining": remaining
    }

    return JSONResponse(
        content={"summary": summary, "verdict": verdict},
        headers=headers
    )
