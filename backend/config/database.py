"""
Centralized database module for the Clinic Intake Assistant.
Provides engine, session factory, and FastAPI dependency.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Load environment variables
env = os.getenv("ENVIRONMENT", "development")
dotenv_path = os.path.join(os.path.dirname(__file__), 'settings', 'env', f'.env.{env}')
load_dotenv(dotenv_path)

DATABASE_URL = os.getenv("DB_URI", "postgresql://postgres:123@127.0.0.1:5435/clinic_intake")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency that provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database: enable pgvector extension and create all tables."""
    from apps.db_models import Base
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        Base.metadata.create_all(bind=engine)
        print("[+] Database tables created successfully.")
    except Exception as e:
        print("[!] Database initialization warning:", e)
