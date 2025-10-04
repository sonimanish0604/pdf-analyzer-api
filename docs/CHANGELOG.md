**#📜 Changelog — PDF Analyzer API**

All notable changes to this project will be documented here.
Format follows Semantic Versioning
 (MAJOR.MINOR.PATCH).

**###[Unreleased]**

Add async job processing for large PDF scans

Add Splunk/ELK log export for enterprise plans

Improve error codes with more granular messages

#09.22 - to test pull request

**##[1.0.0] — 2025-09-09**
Added

Initial public release of PDF Analyzer API v1 🎉

Endpoint: POST /v1/analyze — scan uploaded PDFs for:

Encryption/password protection

Embedded JavaScript

Embedded files

Spoofed file types

Suspicious URLs (DNS + optional VirusTotal check)

Endpoint: GET /v1/health — service health check

Endpoint: GET /metrics — Prometheus metrics

Endpoint: GET /docs — Swagger UI

API key authentication with per-key rate limiting

In-memory processing (no disk writes) for privacy

Usage metering for future billing integration

**##Legend**

Added → New features

Changed → Updates/improvements (backward-compatible)

Fixed → Bug fixes

Removed → Features removed/deprecated

## [1.1.0] — 2025-09-15
### Added
- DOCX/PNG analyzers (beta)

