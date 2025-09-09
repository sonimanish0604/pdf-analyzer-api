#!/usr/bin/env bash
set -euo pipefail

TAG="${1:-}"
CHANGELOG_FILE="${2:-CHANGELOG.md}"
OUT_FILE="${3:-CHANGELOG_RELEASE.md}"

if [[ -z "$TAG" ]]; then
  echo "Usage: $0 <tag> [changelog_file] [out_file]" >&2
  exit 1
fi
if [[ ! -f "$CHANGELOG_FILE" ]]; then
  echo "Changelog file not found: $CHANGELOG_FILE" >&2
  exit 1
fi

# Escape tag for regex (e.g., v1.2.3)
TAG_ESCAPED=$(printf '%s\n' "$TAG" | sed -e 's/[]\/$*.^|[]/\\&/g')

# Grab lines from "## [<tag>]" until the next "## [" or end-of-file
awk -v tag="## \\[""$TAG_ESCAPED""\\]" '
  $0 ~ "^"tag"$" { capture=1; print; next }
  capture && /^## \[/ { capture=0 }
  capture { print }
' "$CHANGELOG_FILE" > "$OUT_FILE"

# Fallback if section missing
if ! grep -q "## \[$TAG_ESCAPED\]" "$OUT_FILE"; then
  echo "## [$TAG]" > "$OUT_FILE"
  echo "" >> "$OUT_FILE"
  echo "_No matching section found in CHANGELOG.md. Consider updating it._" >> "$OUT_FILE"
fi

echo "Wrote release notes to: $OUT_FILE"
