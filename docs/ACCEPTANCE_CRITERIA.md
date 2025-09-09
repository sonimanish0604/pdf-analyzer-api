# Acceptance Criteria — PDF Analyzer API (v1)

## 0. Scope & Definitions

**In-scope endpoint:**  
`POST /v1/analyze` (multipart file upload)

**Aux endpoints:**  
- `GET /v1/health`
- `GET /metrics` (Prometheus)
- `GET /docs` (Swagger UI)
- `GET /openapi.json`

**Auth:** API key required on protected routes  
**Output shape:** JSON matching the README’s structure (see “Sample Output”).

---

## 1. Functional — Core Scans (`POST /v1/analyze`)

### 1.1 Clean valid PDF
- **Given:** A well-formed, non-encrypted PDF with no embedded JS, no embedded files, and only safe/empty URLs
- **When:** Client uploads the file to `/v1/analyze`
- **Then:** Response is 200 OK with:
  - `summary.valid_pdf = true`
  - `summary.encrypted = false`
  - `summary.embedded_javascript = false`
  - `summary.embedded_files = false`
  - `summary.embedded_file_names = []`
  - `summary.urls_found.safe` contains only benign URLs (or empty)
  - `summary.urls_found.suspicious = []`
  - `verdict` conveys a clean result (e.g., "✅ Clean file")

### 1.2 Encrypted/password-protected PDF
- **Given:** Valid, password-protected PDF
- **When:** Uploaded
- **Then:** 200 OK with:
  - `summary.encrypted = true`
  - `verdict` flags encryption (e.g., "⚠️ Suspicious — encrypted/password-protected")

### 1.3 Embedded JavaScript detected
- **Given:** PDF containing embedded JavaScript
- **When:** Uploaded
- **Then:** 200 OK with:
  - `summary.embedded_javascript = true`
  - `verdict` warns about JS

### 1.4 Embedded files detected
- **Given:** PDF with embedded files (e.g., a ZIP)
- **When:** Uploaded
- **Then:** 200 OK with:
  - `summary.embedded_files = true`
  - `summary.embedded_file_names`: lists names (e.g., `["invoice.zip"]`)
  - `verdict` warns about embedded files

### 1.5 Spoofed file types
- **Given:** File with mismatched header/MIME
- **When:** Uploaded
- **Then:** Either
  - `415 Unsupported Media Type`
  - or `200 OK` with `summary.valid_pdf = false` and verdict flags spoofing

### 1.6 URL checks (DNS + VirusTotal, if configured)
- **Given:** PDF with URLs
- **When:** Uploaded
- **Then:** For each URL:
  - DNS failures: `vt_status = "dns_error"` with error note
  - VT-flagged: `vt_status = "malicious"` with score/comment
  - Safe links: under `summary.urls_found.safe`

---

## 2. Error Handling & Limits

- **Non-PDF upload:** `415 Unsupported Media Type` or `400 Bad Request` (machine-readable error)
- **Corrupted PDF:** `400 Bad Request`
- **Oversized file:** `413 Payload Too Large`
- **Parser timeout:** `504 Gateway Timeout` (or `408`)
- **Missing/invalid API key:** `401` or `403`
- **Over quota/rate limit:** `429 Too Many Requests`
- All errors include:
  - `error.code`
  - `error.message`

---

## 3. Contract (Schema) Stability

- The JSON fields in README sample are present and stable in v1.
- No breaking changes within `/v1`
- `/openapi.json` reflects live contract
- `/docs` (Swagger UI) loads and allows interactive testing

---

## 4. Security & Privacy

- API keys verified; only hashed keys stored
- Auth endpoints reject requests without/bad keys
- Scanning is in-memory (no disk writes)
- No persistent uploaded file storage; only minimal metadata/usage metrics retained
- Strict content-type validation
- Safe parsing defaults

---

## 5. Performance & Reliability Targets

- **Latency:** P95 ≤ 1.5s for PDFs ≤ N MB
- **Availability:** 99.9% monthly for `/v1/analyze` and `/v1/health`
- **Throughput:** Sustains X RPS with back-pressure

---

## 6. Observability

### 6.1 Logging
- Structured JSON logs: `request_id`, `route`, `api_key_id`, `status`, `latency_ms`, decision flags

### 6.2 Metrics
- Prometheus counters/histograms:
  - `requests_total{route,code}`
  - `request_latency_ms{route}`
  - `findings_total{type}`
- `/metrics` endpoint is scrape-ready

### 6.3 Health
- `GET /v1/health` returns `200` and minimal payload (`{"ok": true}`)

---

## 7. Versioning & Deprecation

- All criteria apply to `/v1/*`
- Breaking changes trigger `/v2/*`
- If `/v1` deprecated, responses include:
  - Deprecation header (sunset date ≥ 6 months away)
  - Link: `</v2/analyze>; rel="successor-version"`

---

## 8. Admin & Metering

- Admin can create/revoke keys and set plan/limits
- Usage event per request (key, endpoint, bytes, timestamp)
- Over-limit requests: `429` with next steps

---

## 9. Smoke Test

```bash
curl -X POST https://<yourapp>.onrender.com/v1/analyze \
  -H "x-api-key: <YOUR_API_KEY>" \
  -F "file=@sample.pdf;type=application/pdf"
```

---

## 10. Acceptance Checklist

| Criteria | Yes/No |
|----------|--------|
| `/v1/analyze` returns required fields |        |
| Non-PDF/corrupt/oversized requests fail with correct codes |        |
| API key required; 401/403/429 handled correctly |        |
| OpenAPI serves and matches actual responses; `/docs` usable |        |
| Health + metrics endpoints live; logs structured |        |
| P95 latency/availability targets met |        |
| Usage events stored; over-limit returns 429 |        |
| Versioning policy observed; no breaking changes within `/v1` |        |
