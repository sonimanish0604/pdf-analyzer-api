# app/services/keys.py
import hashlib
import secrets

from app.core.config import get_settings
from app.db import save_api_key_hash  # implement this DB helper


def issue_api_key(tenant_id: str, plan: str = "free") -> str:
    # 1. Generate a raw 64-char hex key (32 bytes)
    raw_key = secrets.token_hex(32)

    # 2. Derive a prefix (first 8 chars + uuid or similar, must be unique)
    key_prefix = raw_key[:8] + uuid.uuid4().hex[:4]

    # 3. Salt + hash for secure storage
    salt = get_settings().API_KEY_HASH_SALT or ""
    hashed = hashlib.sha256((salt + raw_key).encode()).hexdigest()

    # 4. Save hash to DB (not raw key)
    save_api_key_hash(
        tenant_id=tenant_id,
        key_prefix=key_prefix,
        key_hash=hashed,
        salt=salt,
        plan=plan,
        active=True,
    )

    # 5. Return only the raw key (caller gives it to user once)
