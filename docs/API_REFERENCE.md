#📘 API Reference — PDF Analyzer API
##1. Overview

The PDF Analyzer API scans uploaded PDF files for common risks such as encryption, embedded JavaScript, hidden files, spoofed file types, and malicious URLs.

Base URLs

Staging: https://<staging-app>.onrender.com/v1

Production: https://<prod-app>.onrender.com/v1

Authentication

API key must be included in the request header:

x-api-key: YOUR_API_KEY


Content Types

All file uploads use multipart/form-data.

##2. Endpoints
###2.1 POST /v1/analyze

Analyze an uploaded PDF file.

Headers

x-api-key: <YOUR_API_KEY> (required)

Content-Type: multipart/form-data

Body

file: PDF file to analyze.

Sample Request

curl -X POST https://<prod-app>.onrender.com/v1/analyze \
  -H "x-api-key: YOUR_API_KEY" \
  -F "file=@sample.pdf;type=application/pdf"


Sample Response

{
  "summary": {
    "valid_pdf": true,
    "encrypted": false,
    "embedded_javascript": false,
    "urls_found": {
      "safe": ["https://example.com"],
      "suspicious": []
    },
    "embedded_files": false,
    "embedded_file_names": []
  },
  "verdict": "✅ Clean file"
}


Error Codes

HTTP Code	Error Code	Description
400	invalid_file	Corrupted or unreadable file
401	missing_api_key	API key not provided
403	invalid_api_key	API key invalid or revoked
413	oversized_file	File size exceeded allowed limit
415	unsupported_media	Non-PDF file uploaded
429	rate_limit_exceeded	Plan quota or rate limit exceeded
500	server_error	Unexpected server issue
###2.2 GET /v1/health

Health check endpoint.

Sample Response

{ "ok": true }

###2.3 GET /metrics

Prometheus metrics for observability.

Output

Exposes counters and histograms, e.g.:

requests_total{route,code}

request_latency_ms{route}

findings_total{type}

###2.4 GET /docs

Interactive Swagger UI for testing and exploration.

##3. Error Model

Errors are returned in a consistent JSON format:

{
  "error": {
    "code": "invalid_file",
    "message": "The uploaded file is not a valid PDF"
  }
}

##4. Rate Limits & Quotas

Free Plan (example): 100 scans/month, max file size 5 MB.

Pro Plan: Higher limits, larger file sizes.

Enterprise Plan: Custom quotas, SLAs.

If quota is exceeded, the API returns:

HTTP/1.1 429 Too Many Requests

{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "You have exceeded your monthly quota. Please upgrade your plan."
  }
}

##5. Versioning

Current stable version: /v1

Breaking changes → released under /v2

Deprecation policy:

Responses may include a Deprecation header with a sunset date

Link header points to successor endpoint

##6. Sample Workflows
###6.1 Quick CLI Scan
curl -X POST https://<prod-app>.onrender.com/v1/analyze \
  -H "x-api-key: YOUR_API_KEY" \
  -F "file=@invoice.pdf;type=application/pdf"

###6.2 Python Example
import requests

url = "https://<prod-app>.onrender.com/v1/analyze"
headers = {"x-api-key": "YOUR_API_KEY"}
files = {"file": open("sample.pdf", "rb")}

response = requests.post(url, headers=headers, files=files)
print(response.json())

###6.3 Node.js Example
import axios from "axios";
import fs from "fs";

const url = "https://<prod-app>.onrender.com/v1/analyze";
const headers = { "x-api-key": "YOUR_API_KEY" };
const file = fs.createReadStream("sample.pdf");

axios.post(url, { file }, { headers })
  .then(res => console.log(res.data))
  .catch(err => console.error(err.response.data));
