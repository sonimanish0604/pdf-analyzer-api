import os
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, Column, String, Table, MetaData
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL)
metadata = MetaData()

api_keys_table = Table(
    "api_keys", metadata,
    Column("key", String, primary_key=True),
    Column("rate_limit", String)
)

metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
