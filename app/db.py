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
import os
from datetime import datetime
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
#SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False  # <- important
)
def upsert_tenant_mapping(provider, customer_identifier, product_code, account_id):
    # check DB if tenant already exists
    # if not, create it
    # return tenant_id
    ...