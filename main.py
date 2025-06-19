from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
import fitz  # PyMuPDF
import filetype
from io import BytesIO
import tempfile
import os
import requests
import urllib.parse
import socket
import os as system_os

app = FastAPI(
    title="PDF Analyzer API",
    description="""
    This API analyzes uploaded PDF files for:
    - Valid PDF structure
    - Password protection
    - Embedded JavaScript or files
    - Spoofed ZIP masquerading as PDF
    - URLs with DNS and VirusTotal validation

    ⚠️ **About `dns_error` in URL Analysis:**
    If a URL returns `vt_status: dns_error`, it means the system couldn’t resolve the domain. This is often due to:
    - 🌐 No internet access
    - 🧱 Firewall or VPN blocking DNS
    - 📛 Fake or typo domains like `secure123.biz`
    - 🧪 Intentionally spoofed phishing-style URLs for testing

    In such cases, VirusTotal will not be queried because the domain doesn’t resolve at the DNS level.
    """
)

# Enable CORS for frontend testing if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Add this to redirect root "/" to Swagger UI
@app.get("/")
def read_root():
    return RedirectResponse(url="/docs")

# Your existing API logic continues below
# Example:
@app.post("/analyze-pdf")
async def analyze_pdf(file: UploadFile = File(...)):
    # ... Your threat detection logic here ...
    return {"result": "ok"}


def is_true_pdf(file_stream):
    file_stream.seek(0)
    header = file_stream.read(5)
    file_stream.seek(0)
    if header != b"%PDF-":
        return False
    kind = filetype.guess(file_stream.read(261))
    file_stream.seek(0)
    if not kind or kind.mime != 'application/pdf':
        return False
    from zipfile import is_zipfile
    if is_zipfile(file_stream):
        return False
    return True

def is_encrypted(file_stream):
    try:
        file_stream.seek(0)
        doc = fitz.open(stream=file_stream.read(), filetype="pdf")
        return doc.is_encrypted
    except:
        return False

def has_embedded_javascript(file_bytes):
    try:
        from PyPDF2.generic import IndirectObject

        def resolve(obj):
            while isinstance(obj, IndirectObject):
                obj = obj.get_object()
            return obj

        reader = PdfReader(BytesIO(file_bytes))
        catalog = resolve(reader.trailer.get("/Root", {}))

        names = resolve(catalog.get("/Names"))
        if names and "/JavaScript" in names:
            return True

        open_action = resolve(catalog.get("/OpenAction"))
        if open_action:
            js = open_action.get("/JS") or open_action.get("/JavaScript")
            js = resolve(js)
            if js:
                return True
    except Exception as e:
        print("Deep JS check error:", e)

    return False

def has_embedded_files_and_names(file_stream):
    try:
        file_stream.seek(0)
        doc = fitz.open(stream=file_stream.read(), filetype="pdf")
        embedded_files = []
        for i in range(doc.embfile_count()):
            info = doc.embfile_info(i)
            embedded_files.append(info.get("filename"))
        return len(embedded_files) > 0, embedded_files
    except:
        return False, []

def check_url_virustotal(url):
    try:
        api_key = system_os.getenv("VT_API_KEY")
        if not api_key:
            return {"url": url, "vt_status": "missing_api_key"}
        encoded_url = urllib.parse.quote_plus(url)
        api_url = f"https://www.virustotal.com/api/v3/urls/{encoded_url}"
        headers = {"x-apikey": api_key}
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            attr = data.get("data", {}).get("attributes", {})
            stats = attr.get("last_analysis_stats", {})
            total = sum(stats.values())
            flagged = stats.get("malicious", 0) + stats.get("suspicious", 0)
            score = f"{flagged}/{total}" if total > 0 else "0/0"
            comment = f"⚠️ Flagged by {flagged} of {total} engines" if flagged > 0 else "✅ No engines flagged"
            return {
                "url": url,
                "vt_status": "malicious" if flagged > 0 else "clean",
                "vt_score": score,
                "vt_comment": comment
            }
        else:
            return {"url": url, "vt_status": "error"}
    except Exception as e:
        return {"url": url, "vt_status": "error", "error": str(e)}
    except:
        return "error"

def extract_urls(file_stream):
    try:
        file_stream.seek(0)
        doc = fitz.open(stream=file_stream.read(), filetype="pdf")
        urls = set()
        for page in doc:
            links = page.get_links()
            for link in links:
                uri = link.get("uri", None)
                if uri:
                    urls.add(uri)
        validated = {"safe": [], "suspicious": []}
        for url in urls:
            try:
                parsed = urllib.parse.urlparse(url)
                if not parsed.scheme.startswith("http"):
                    validated["suspicious"].append({"url": url, "vt_status": "invalid_scheme"})
                    continue
                socket.gethostbyname(parsed.netloc)
                vt_result = check_url_virustotal(url)
                if vt_result["vt_status"] == "malicious":
                    validated["suspicious"].append(vt_result)
                else:
                    validated["safe"].append(vt_result)
            except Exception as e:
                validated["suspicious"].append({"url": url, "vt_status": "dns_error", "error": str(e)})
        return validated
    except:
        return {"safe": [], "suspicious": []}

@app.post("/analyze-pdf")
async def analyze_pdf(file: UploadFile = File(...)):
    file_bytes = await file.read()
    file_stream = BytesIO(file_bytes)

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

    return {
        "summary": summary,
        "verdict": verdict
    }
