**#📄 PDF Analyzer API**

A FastAPI-based microservice that scans uploaded PDF files for common risks:

🔐 Encryption/password protection

📎 Embedded JavaScript (JS-based malware)

📁 Embedded files (e.g. ZIP, DOCX)

🕵️ Spoofed file types (e.g. ZIP masquerading as PDF)

🌐 URLs with DNS resolution & VirusTotal threat intelligence

**##📚 Documentation**

This repo follows a full SDLC with dedicated docs:

PRODUCT.md
 → Vision, roadmap, monetization

API_REFERENCE.md
 → Endpoints, request/response, error codes

ACCEPTANCE_CRITERIA.md
 → Testable criteria for each release

SECURITY.md
 → Data handling, key management, disclosure policy

BUSINESS.md
 → Pricing and go-to-market

CHANGELOG.md
 → Release history

**##🚀 Features**

Pure in-memory scanning (safe for PII; no disk writes)

Detects encryption, embedded JS, embedded files, spoofed types, malicious URLs

VirusTotal API integration (optional)

API key authentication + per-key quotas/rate limits

Prometheus metrics + structured logging

CI/CD pipeline: staging auto-deploys, production deploys on GitHub release

**##🧪 Quick Start**
Run Locally
`git clone https://github.com/your_username/pdf-analyzer-api.git
cd pdf-analyzer-api
pip install -r requirements.txt
uvicorn main:app --reload
`

Server available at: http://127.0.0.1:8000

Example Request
`curl -X POST http://127.0.0.1:8000/v1/analyze \
  -H "x-api-key: YOUR_API_KEY" \
  -F "file=@sample.pdf;type=application/pdf"`

`Example Response
{
  "summary": {
    "valid_pdf": true,
    "encrypted": false,
    "embedded_javascript": false,
    "urls_found": {
      "safe": ["https://example.com"],
      "suspicious": []
    },
    "embedded_files": true,
    "embedded_file_names": ["invoice.zip"]
  },
  "verdict": "⚠️ Suspicious file — contains embedded files"
}`

Browser Testing

Visit Swagger UI
.

**##🔧 Configuration**

VirusTotal API key (optional):

export VT_API_KEY=your_key_here


Environment variables (dev/test/prod): see SECURITY.md
.

**##🤖 Observability**

GET /v1/health → service health

GET /metrics → Prometheus metrics

Structured JSON logs (request id, key id hash, route, status, latency)

**##📦 CI/CD & Releases**

Environments: dev (local), staging (auto-deploy from main), production (deploys on tag).

Releases: Tag a version (vX.Y.Z) → CI builds Docker image, publishes GitHub release with notes from CHANGELOG.md
.

Acceptance: Criteria checked via ACCEPTANCE_CRITERIA.md
.

**##💡 Roadmap**

v1.x: Hardened PDF analysis, quotas, billing integration

v2.x: Password-protected PDFs, signed scan reports

v3.x: Multi-format analysis (DOCX, PNG, JPEG, XLSX, media files)

See PRODUCT.md
 for full roadmap.

**##📂 Project Structure**
pdf-analyzer-api/
├── app/                    # FastAPI source
├── tests/                  # Unit & integration tests
├── scripts/                # DevOps scripts (changelog extraction, etc.)
├── .github/workflows/      # CI/CD pipelines
├── README.md               # You're here
├── PRODUCT.md
├── API_REFERENCE.md
├── ACCEPTANCE_CRITERIA.md
├── SECURITY.md
├── BUSINESS.md
├── CHANGELOG.md
└── LICENSE

**##🛡 License**

MIT License — see LICENSE
.
