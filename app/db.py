# import os

# from sqlalchemy import create_engine, Column, String, Table, MetaData
# from sqlalchemy.orm import sessionmaker

# DATABASE_URL = os.environ.get("DATABASE_URL")

# engine = create_engine(DATABASE_URL)
# metadata = MetaData()

# api_keys_table = Table(
#    "api_keys", metadata,
#    Column("key", String, primary_key=True),
#    Column("rate_limit", String)
# )

# metadata.create_all(engine)

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# ----------------------------------------------------------------------------------#
# ***added 09/14/2025 for database**--commented above lines
import uuid
import os
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import insert, select, update
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError


from sqlalchemy import (
    create_engine,
    Column,
    String,
    Table,
    MetaData,
    Boolean,
    DateTime,
    Index,
)
# ------------------ Config ------------------
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is required")


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

metadata = MetaData()

# ------------------ Tables ------------------
# api_keys: hashed storage + tenant + expiry
api_keys_table = Table(
    "api_keys",
    metadata,
    Column("id", String(36), primary_key=True),  # uuid4 string
    Column("tenant_id", String(64), nullable=False, index=True),
    Column("key_prefix", String(16), nullable=False, unique=True),
    Column("key_hash", String(128), nullable=False),  # hex SHA-256
    Column("salt", String(32), nullable=False),  # 16-byte hex
    Column("plan", String(32), nullable=False, default="free"),
    Column("active", Boolean, nullable=False, default=True),
    Column("created_at", DateTime, nullable=False, default=datetime.utcnow),
    Column("expires_at", DateTime, nullable=True),
    Column("last_used_at", DateTime, nullable=True),
)
Index("ix_api_keys_prefix", api_keys_table.c.key_prefix, unique=True)

# Optional but audit-friendly: admin actions log
audit_admin_events = Table(
    "audit_admin_events",
    metadata,
    Column("id", String(36), primary_key=True),  # uuid4 string
    Column("ts", DateTime, nullable=False, default=datetime.utcnow),
    Column("action", String(16), nullable=False),  # create/revoke/rotate/list
    Column("tenant_id", String(64), nullable=True),
    Column("key_id", String(36), nullable=True),
    Column("admin_actor", String(128), nullable=True),  # e.g., IP or 'CI'
    Column("user_agent", String(256), nullable=True),
    Column("notes", String(1024), nullable=True),
)

# Create missing tables on first boot
#
# metadata.create_all(engine)
metadata = MetaData()
# ORM session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#SessionLocal = async_sessionmaker(
#    bind=engine, class_=AsyncSession, expire_on_commit=False  # <- important
#)

def save_api_key_hash(
    *,
    tenant_id: str,
    key_prefix: str,
    key_hash: str,
    salt: str,
    plan: str = "free",
    active: bool = True,
    expires_at: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Persist a newly issued API key hash (NOT the raw key).
    Returns a dict with the inserted record's basic fields.
    """
    key_id = str(uuid.uuid4())
    with SessionLocal() as session:
        stmt = insert(api_keys_table).values(
            id=key_id,
            tenant_id=tenant_id,
            key_prefix=key_prefix,
            key_hash=key_hash,
            salt=salt,
            plan=plan,
            active=active,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            last_used_at=None,
        )
        try:
            session.execute(stmt)
            session.commit()
        except IntegrityError as e:
            session.rollback()
            # likely duplicate key_prefix (unique)
            raise ValueError(f"API key prefix already exists: {key_prefix}") from e

        # return a minimal echo (don’t return sensitive hash/salt to callers)
        return {
            "id": key_id,
            "tenant_id": tenant_id,
            "key_prefix": key_prefix,
            "plan": plan,
            "active": active,
            "created_at": datetime.utcnow().isoformat(),
        }

def get_api_key_by_prefix(key_prefix: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a key row by its prefix (used in request auth).
    Returns a dict with stored fields or None.
    """
    with SessionLocal() as session:
        stmt = select(api_keys_table).where(api_keys_table.c.key_prefix == key_prefix)
        row = session.execute(stmt).mappings().first()
        return dict(row) if row else None

def mark_api_key_used(key_id: str) -> None:
    """
    Update last_used_at for observability. Safe to ignore errors upstream.
    """
    with SessionLocal() as session:
        stmt = (
            update(api_keys_table)
            .where(api_keys_table.c.id == key_id)
            .values(last_used_at=datetime.utcnow())
        )
        session.execute(stmt)
        session.commit()

def upsert_tenant_mapping(provider, customer_identifier, product_code, account_id):
    # check DB if tenant already exists
    # if not, create it
    # return tenant_id
    ...