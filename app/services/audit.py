# app/services/audit.py
from datetime import datetime
from typing import Optional
from sqlalchemy import insert
from app.db import SessionLocal, audit_admin_events

def log_admin(action: str, admin_actor: Optional[str] = None, notes: str = "", tenant_id: Optional[str] = None, key_id: Optional[str] = None):
    with SessionLocal() as s:
        s.execute(insert(audit_admin_events).values(
            id=datetime.utcnow().isoformat(),  # or uuid4
            ts=datetime.utcnow(),
            action=action,
            tenant_id=tenant_id,
            key_id=key_id,
            admin_actor=admin_actor,
            notes=notes[:1024],
        ))
        s.commit()