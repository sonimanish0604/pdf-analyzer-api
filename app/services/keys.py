# app/services/keys.py
import secrets
import hashlib
from app.core.config import get_settings
from app.db import save_api_key_hash  # implement this DB helper

def issue_api_key(tenant_id: str) -> str:
    raw_key = secrets.token_hex(32)

    salt = (get_settings().API_KEY_HASH_SALT or "")
    hashed = hashlib.sha256((salt + raw_key).encode()).hexdigest()

    save_api_key_hash(tenant_id=tenant_id, key_hash=hashed)  # <-- use it
    return raw_key
