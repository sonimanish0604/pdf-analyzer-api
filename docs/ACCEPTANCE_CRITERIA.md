Acceptance Criteria — PDF Analyzer API (v1)
0) Scope & Definitions

In-scope endpoint: POST /v1/analyze (multipart file upload)

Aux endpoints: GET /v1/health, GET /metrics (Prometheus), GET /docs (Swagger UI), GET /openapi.json

Auth: API key required on protected routes

Output shape: JSON matching the README’s structure (see “Sample Output”).

1) Functional — Core Scans (POST /v1/analyze)
1.1 Clean valid PDF

Given a well-formed, non-encrypted PDF with no embedded JS, no embedded files, and only safe/empty URLs
When the client uploads the file to /v1/analyze
Then the response is 200 OK with:

summary.valid_pdf = true

summary.encrypted = false

summary.embedded_javascript = false

summary.embedded_files = false

summary.embedded_file_names = []

summary.urls_found.safe contains only benign URLs (or empty)

summary.urls_found.suspicious = []

verdict conveys a clean result (e.g., “✅ Clean file”).
(Names/sections per your sample JSON).

1.2 Encrypted/password-protected PDF

Given a valid, password-protected PDF
When uploaded
Then 200 OK with:

summary.encrypted = true

verdict clearly flags encryption (e.g., “⚠️ Suspicious — encrypted/password-protected”).

1.3 Embedded JavaScript detected

Given a PDF containing embedded JavaScript
When uploaded
Then 200 OK with:

summary.embedded_javascript = true

verdict warns about JS (per README’s “JS-based malware” risk).

1.4 Embedded files detected

Given a PDF with embedded files (e.g., a ZIP)
When uploaded
Then 200 OK with:

summary.embedded_files = true

summary.embedded_file_names lists the names (e.g., ["invoice.zip"]).

verdict warns about embedded files.

1.5 Spoofed file types

Given a file with a mismatched header/MIME (e.g., ZIP disguised as .pdf)
When uploaded
Then either

415 Unsupported Media Type or 200 OK with summary.valid_pdf = false and a verdict that flags spoofing, consistent with your chosen contract.

1.6 URL checks (DNS + VirusTotal, if configured)

Given a PDF with URLs
When uploaded
Then for each URL:

DNS failures appear with vt_status = "dns_error" and an error note (per README example).

VT-flagged links return vt_status = "malicious" with a score/comment when VT is enabled.

Safe links appear under summary.urls_found.safe.

2) Error Handling & Limits
2.1 Non-PDF or corrupted PDF

Non-PDF upload → 415 Unsupported Media Type or 400 Bad Request with machine-readable error code.

Corrupted PDF → 400 Bad Request with machine-readable error code.

2.2 File size/time limits

Oversized file (> configured limit) → 413 Payload Too Large.

Parser timeout (e.g., pathological PDFs) → 504 Gateway Timeout (or 408) with explanatory error.

2.3 Auth & rate limiting

Missing/invalid API key → 401 (missing) or 403 (invalid/revoked).

Over quota/rate limit → 429 Too Many Requests with reset hint.

All errors include a stable, machine-readable error.code and human-readable error.message.

3) Contract (Schema) Stability
3.1 Response schema (v1)

The JSON fields used in README’s sample are present and stable in v1:

summary.valid_pdf, summary.encrypted, summary.embedded_javascript,

summary.embedded_files, summary.embedded_file_names[],

summary.urls_found.safe[], summary.urls_found.suspicious[],

verdict string.

No breaking changes within /v1 (only additive/optional fields).

3.2 OpenAPI & Docs

/openapi.json reflects the live contract.

/docs (Swagger UI) loads and allows interactive testing (as in README).

4) Security & Privacy
4.1 Key handling

API keys are verified; server stores only hashed keys.

Endpoints requiring auth reject requests without/with bad keys.

4.2 Data handling

Scanning is in-memory (no disk writes) as stated in README.

No persistent storage of uploaded file bytes; only minimal metadata/usage metrics retained.

4.3 Input validation

Strict content-type validation.

Safe parsing defaults to avoid known PDF parser exploits.

5) Performance & Reliability Targets (v1 “good enough”)

Latency: P95 ≤ 1.5s for PDFs ≤ N MB on staging hardware (set N to your limit).

Availability: 99.9% monthly for /v1/analyze and /v1/health in production.

Throughput: Sustains X RPS with graceful back-pressure (you can start small and revise).

6) Observability
6.1 Logging

Structured JSON logs per request with: request_id, route, api_key_id (or hashed id), status, latency_ms, and key decision flags (e.g., encrypted=true, embedded_js=true).

6.2 Metrics

Prometheus counters/histograms:

requests_total{route,code}, request_latency_ms{route}, findings_total{type} (e.g., encrypted, embedded_js).

/metrics endpoint is scrape-ready.

6.3 Health

GET /v1/health returns 200 and a minimal payload (e.g., {"ok": true}), suitable for uptime checks.

7) Versioning & Deprecation

All criteria above apply to /v1/*.

Any breaking change triggers /v2/*.

If /v1 is ever deprecated, responses include:

Deprecation header with a sunset date ≥ 6 months away.

Link: </v2/analyze>; rel="successor-version".

8) Admin & Metering (Minimal for v1)

Admin can create/revoke keys and set plan/limits (via admin API or console).

Each request records a usage event (key, endpoint, bytes, timestamp) for quotas/billing.

Over-limit requests return 429 with a clear message on next steps.

9) Smoke Test


curl -X POST https://<yourapp>.onrender.com/v1/analyze \
  -H "x-api-key: <YOUR_API_KEY>" \
  -F "file=@sample.pdf;type=application/pdf"


10) Acceptance Checklist (quick yes/no)

 /v1/analyze returns the fields shown in README for clean and flagged cases

 Non-PDF/corrupt/oversized requests fail with correct HTTP codes

 API key required; 401/403/429 handled correctly

 OpenAPI serves and matches actual responses; /docs usable

 Health + metrics endpoints live; logs structured

 P95 latency and basic availability targets met on staging

 Usage events stored; over-limit requests return 429

 Versioning policy observed; no breaking changes within /v1
