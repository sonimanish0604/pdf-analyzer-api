#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://localhost:8000}"

echo "🔎 Running smoke test against $BASE_URL"

# 1) Health check (no key required)
curl -fsS "$BASE_URL/v1/health" >/dev/null

# 2) Check that docs (or OpenAPI) endpoint is reachable
curl -fsS "$BASE_URL/openapi.json" >/dev/null

echo "✅ Smoke OK against $BASE_URL"
