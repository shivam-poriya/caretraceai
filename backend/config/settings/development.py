from .base import *
from config.database import engine, SessionLocal, init_db
import os


class Database:
    """Database wrapper for backward compatibility with existing auth module."""
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal

    def is_connected(self):
        try:
            with self.engine.connect() as conn:
                return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False


api_key = os.getenv("API_KEY")
host = os.getenv("HOST")
port = os.getenv("PORT")

# Create an instance of Database class
db = Database()

if db.is_connected():
    print("[+] Database connection is established.")
    init_db()
else:
    print("[-] Failed to connect to the database.")

db_name = os.getenv("DB_NAME")
print(f"[DB] Database Name: {db_name}")

SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")