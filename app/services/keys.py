# app/services/keys.py
import secrets
import hashlib

def issue_api_key(tenant_id: str) -> str:
    # generate raw key
    raw_key = secrets.token_hex(32)
    # hash for storage (never store raw key)
    hashed = hashlib.sha256(raw_key.encode()).hexdigest()
    # TODO: save hashed + tenant_id into your DB
    return raw_key  # return raw only once to customer