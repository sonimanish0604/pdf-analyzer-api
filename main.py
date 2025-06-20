import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from io import BytesIO
#from dotenv import load_dotenv
from fastapi import FastAPI, Request
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


app = FastAPI()

# Set up the Limiter
limiter = Limiter(key_func=get_remote_address)

# Register exception handler for rate limit exceeded
app.state.limiter = limiter
#app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler) removed to add JSON
#add logic below
@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "error": "Too Many Requests",
            "code": 429,
            "detail": str(exc)  # Optional: shows the limit like "5 per 1 minute"
        }
    )

# Load environment variables from .env file (optional for local dev)
#load_dotenv()


# Allow all CORS (adjust as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load API key from environment variable
API_KEY = os.getenv("API_AUTH_KEY")

def verify_api_key(request: Request):
    client_key = request.headers.get("x-api-key")
    if not client_key or client_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API Key")

# 👇 Protect this route with API key check
@app.post("/analyze-pdf")
@limiter.limit("5/minute")  # Adjust this limit as needed
async def analyze_pdf(
    file: UploadFile = File(...),
    request: Request = None,
    _: None = Depends(verify_api_key)
):
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

    has_files, embedded_files = (False, [])
    if not summary["encrypted"]:
        has_files, embedded_files = has_embedded_files_and_names(BytesIO(file_bytes))

    summary["embedded_files"] = has_files
    summary["embedded_file_names"] = embedded_files

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

    return {"summary": summary, "verdict": verdict}
