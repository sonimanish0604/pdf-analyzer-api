# tests/test_sanity_samples.py
import os
import json
import time
from pathlib import Path
import requests
import pytest

# --- Config: use env vars; fallback to sensible defaults for local runs ---
API_URL = os.getenv("API_URL", "https://pdf-analyzer-api-staging.onrender.com/analyze-pdf")
API_KEY = os.getenv("API_KEY", "")  # keep empty locally if you run behind a dev key
HEADERS = {"accept": "application/json", **({"x-api-key": API_KEY} if API_KEY else {})}

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"
EXPECTED_FILE = SAMPLES_DIR / "expected.json"   # optional exact expectations per file

# Optional: rate-limit friendliness
REQUEST_DELAY_SEC = float(os.getenv("SANITY_DELAY", "0.4"))  # spacing requests slightly


def _load_expected():
    """
    expected.json schema (optional):
    {
      "pdfanalyzer-testdoc.pdf": {
        "encrypted": false,
        "has_javascript": false,
        "has_embedded_files": false,
        "mime_spoofed": false,
        "verdict": "clean"
      },
      "malicious-js.pdf": {
        "has_javascript": true,
        "verdict": "suspicious"
      }
    }
    """
    if EXPECTED_FILE.exists():
        with EXPECTED_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _iter_pdfs():
    # All PDFs directly under samples/ (adjust to '**/*.pdf' if you nest folders)
    return sorted(p for p in SAMPLES_DIR.glob("*.pdf") if p.is_file())


@pytest.mark.parametrize("pdf_path", _iter_pdfs(), ids=lambda p: p.name)
def test_sample_pdf_flags_shape_and_optionals(pdf_path):
    # Space requests to be nice to rate limits
    time.sleep(REQUEST_DELAY_SEC)

    with pdf_path.open("rb") as f:
        resp = requests.post(API_URL, headers=HEADERS, files={"file": f}, timeout=60)

    # Basic transport checks
    assert resp.status_code in (200, 400, 415, 422), f"{pdf_path.name}: unexpected status {resp.status_code}"
    # If your API always returns 200 with 'verdict' field, tighten this to == 200

    # Parse JSON
    data = resp.json()
    assert isinstance(data, dict), f"{pdf_path.name}: response is not a JSON object"

    # --- Schema/shape checks (adapt keys to your API’s contract) ---
    # We only *assert presence* of keys that should exist; loosen/tighten as needed.
    expected_bool_keys = [
        "encrypted",
        "has_javascript",
        "has_embedded_files",
        "mime_spoofed",
    ]
    for k in expected_bool_keys:
        assert k in data, f"{pdf_path.name}: missing key '{k}'"
        assert isinstance(data[k], bool), f"{pdf_path.name}: '{k}' should be bool"

    assert "verdict" in data, f"{pdf_path.name}: missing key 'verdict'"
    assert data["verdict"] in {"clean", "suspicious", "malicious"}, f"{pdf_path.name}: unexpected verdict {data['verdict']}"

    # Optional: other metadata checks if your API returns them
    # for k in ("filename", "filesize", "mime_type"):
    #     assert k in data, f"{pdf_path.name}: missing key '{k}'"

    # --- Exact expectations per file (optional) ---
    expected = _load_expected().get(pdf_path.name)
    if expected:
        for k, v in expected.items():
            assert k in data, f"{pdf_path.name}: expected key '{k}' not in response"
            assert data[k] == v, f"{pdf_path.name}: expected {k}={v}, got {data[k]}"