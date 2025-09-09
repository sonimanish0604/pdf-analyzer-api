# 📄 PDF Analyzer API

A FastAPI-based microservice that scans uploaded PDF files for common risks:
- 🔐 Encryption/password protection
- 📎 Embedded JavaScript (JS-based malware)
- 📁 Embedded files (e.g. ZIP, DOCX)
- 🕵️ Spoofed file types (e.g. ZIP masquerading as PDF)
- 🌐 URLs with DNS resolution & VirusTotal threat intelligence

## Docs
PRODUCT.md, API_REFERENCE.md, ACCEPTANCE_CRITERIA.md, SECURITY.md, BUSINESS.md.

## 🚀 Features
- Pure in-memory scanning (no temp file writes)
- Safe for PII/regulated data
- VirusTotal API integration (optional)
- Fast, CORS-enabled, ready for frontend use

---

## 🧪 Sample Use Case
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/v1/analyze' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@sample.pdf;type=application/pdf'
```

### Sample Output
```json
{
  "summary": {
    "valid_pdf": true,
    "encrypted": false,
    "embedded_javascript": false,
    "urls_found": {
      "safe": [...],
      "suspicious": [...]
    },
    "embedded_files": true,
    "embedded_file_names": ["invoice.zip"]
  },
  "verdict": "⚠️ Suspicious file — contains JavaScript or embedded files"
}
```

---

## 🔧 Setup

### 1. Clone & enter the repo
```bash
git clone https://github.com/your_username/pdf-analyzer-api.git
cd pdf-analyzer-api
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Set VirusTotal API key
#### On Windows (PowerShell):
```powershell
$env:VT_API_KEY = "your_key_here"
```
#### On macOS/Linux:
```bash
export VT_API_KEY=your_key_here
```

### 4. Run the server
```bash
uvicorn main:app --reload
```

> The app will be available at: http://127.0.0.1:8000

### 🔎 Test in Browser
Visit the [Swagger UI](http://127.0.0.1:8000/docs) to test file uploads interactively.

---

## 🤖 Threat Intelligence
If URLs are found, DNS lookup and VirusTotal score are returned.

### 🔍 What `vt_status` means:
- `clean`: No engine flagged
- `malicious`: Flagged by one or more engines
- `dns_error`: Domain could not be resolved (common for phishing-style URLs)

> Example:
```json
{
  "url": "http://secure123.biz",
  "vt_status": "dns_error",
  "error": "[Errno 11001] getaddrinfo failed"
}
```

### ✅ Valid DNS, but flagged by VirusTotal
```json
{
  "url": "http://phishing-example.com",
  "vt_status": "malicious",
  "vt_score": "4/88",
  "vt_comment": "⚠️ Flagged by 4 of 88 engines"
}
```

---

## 💡 Future Ideas
- Support password-protected PDFs with user input
- File hash check against public malware feeds
- Export scan result as signed JSON or PDF report
- Docker container support

---

## 📂 File Structure
```
pdf-analyzer-api/
│
├── main.py               # FastAPI service entrypoint
├── requirements.txt      # Dependencies
└── README.md             # You're reading it
```

---

## 🛡 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
