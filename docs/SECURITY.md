**#🛡️ Security Policy — PDF Analyzer API**

Last updated: 2025-09-09

**##1) Data Handling & Privacy**

Processing model: Scans are performed in-memory only. Uploaded bytes are not written to disk by default.

Retention: The service does not persist uploaded files or parsed content. We retain only minimal usage metadata (API key id, timestamp, endpoint, bytes processed, status code) for billing/analytics.

URL Intelligence (optional): If VirusTotal/DNS lookups are enabled, only URLs extracted from PDFs are queried—never the PDF contents.

PII/Sensitive data: Designed to minimize data exposure; customers remain data controllers for any uploaded content.

If you require store-and-scan behavior (e.g., async reports), enable it explicitly in your own deployment and document retention/TTL settings.

**##2) Transport & Perimeter**

TLS: All endpoints require HTTPS (TLS 1.2+). HSTS enabled on the managed domain.

CORS: Disabled by default. If a browser client must call the API, restrict Access-Control-Allow-Origin to an allowlist and disallow credentials.

Headers: X-Content-Type-Options: nosniff, Referrer-Policy: no-referrer, and JSON responses with correct Content-Type: application/json.

**##3) Authentication, Authorization, & Rate Limiting**

API keys: Each customer receives a key with a short key id (public) and a secret (never logged). Server stores only hashed secrets (bcrypt/argon2).

Rotation & Revocation: Keys can be rotated without downtime; old keys can be revoked immediately.

Scopes/Plans: Keys are bound to plans (Free/Pro/Enterprise) and quotas (requests/month, max bytes per request).

Abuse controls: Per-key rate limits, burst controls, and anomaly detection (sudden spikes) returning 429 Too Many Requests.

**##4) Input Validation & Parser Safety**

Content verification: File-signature (magic) checks and strict media-type validation. Non-PDF input → 415 Unsupported Media Type.

Limits: Configurable max file size and CPU/time budgets per request. Oversized/long-running parses → 413/504.

Risk checks: Detection of encrypted PDFs, embedded JavaScript, embedded files, spoofed file types, and suspicious URLs.

Isolation: No shelling out to untrusted binaries; safe parsing settings; no execution of embedded content.

**##5) Secrets & Configuration**

Secret storage: Environment variables / platform secret store (🔧 Render/GitHub Environments). Never commit secrets to Git.

Config separation: Distinct secrets for staging and production.

Key material: API secrets, HMAC signing keys (if enabled), and integration tokens (e.g., VirusTotal) are scoped least-privilege.

**##6) Logging, Metrics, & Monitoring**

Logs: Structured JSON (timestamp, request id, route, status, latency, key id hash). No file contents are logged.

Metrics: Prometheus counters/histograms (requests, latency, findings). Uptime checks from external monitors.

Alerts: Error-rate and latency SLO alerts (🔧 your email/Slack).

**##7) Dependency & Supply-Chain Security**

Pinning: Python dependencies pinned; builds are reproducible via Docker.

Scanning: pip-audit (vulns) and a weekly ZAP baseline scan run in CI.

Updates: Security patches prioritized; CHANGELOG captures security-relevant releases.

**##8) Secure SDLC Practices**

Branch protection: Required reviews and green CI (lint, type check, tests, audit) before merge to main.

Tests: Unit/integration tests cover parsing edge cases and error paths.

Releases: Staging auto-deploy on main; production only on signed tags (v*). Rollback via previous image tag.

**##9) Versioning & Compatibility**

Stable contracts: /v1 is additive-only.

Breaking changes: Introduced under /v2.

Deprecation: Deprecation + Sunset headers with ≥6-month notice; Link header to successor endpoint.

**##10) Incident Response**

Detection: Pager on error-rate/latency spikes, 5xx anomalies, or abuse patterns.

Triage: Classify severity; mitigate (rate-limit, revoke keys, hotfix).

Comms: Customer notice for incidents affecting confidentiality, integrity, or availability; post-mortem for major incidents.

**##11) Responsible Disclosure**

We appreciate coordinated disclosure.

Report a vulnerability: Email 🔧 security@yourdomain.com with steps to reproduce, impact, and any PoC.

We commit to:

Acknowledge within 72 hours.

Provide a remediation plan or fix ETA within 7 business days for high-severity issues.

Credit researchers upon request.

(If needed, publish a /.well-known/security.txt with the same contact.)

**##12) Deployment Options**

Managed (Render) URL: 🔧 https://<prod-app>.onrender.com

Self-hosted: Use our Docker image; configure secrets, CORS, quotas, and monitoring as above.

**##13) Compliance Posture (Roadmap)**

Now: Best-practice controls as listed, privacy-friendly defaults (no storage), audit-ready logs.

Planned: Optional data-processing addendum (DPA), configurable retention, and SIEM export (Splunk/ELK) for enterprise plans.

**##14) Checklist (Operator Quick Start)**

 Enforce HTTPS/HSTS on public domain

 Configure CORS allowlist (if browser clients)

 Set file size + request time limits

 Store API keys hashed; enable rotation

 Enable structured logs + Prometheus + alerts

 Run pip-audit + ZAP in CI; patch vulns

 Separate staging/prod secrets; least-privilege tokens

 Publish security@ contact & (optional) security.txt
