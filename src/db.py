# src/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # repo/src/..
DB_PATH = os.path.join(BASE_DIR, "data", "sales.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create DB dir if missing
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
