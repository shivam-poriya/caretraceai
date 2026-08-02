import os
from config.settings.utils import load_env

environment = os.getenv("ENVIRONMENT", "development")
load_env(environment)

# Secret key for JWT token
SECRET_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJSb2xlIjoiQWRtaW4iLCJJc3N1ZXIiOiJJc3N1ZXIiLCJVc2VybmFtZSI6IkphdmFJblVzZSIsImV4cCI6MTcxNTkzNDI5OCwiaWF0IjoxNzE1OTM4MjAwfQ"
REFRESH_TOKEN_SECRET_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJSb2xlIjoiQWRtaW4iLCJJc3N1ZXIiOiJJc3N1ZXIiLCJVc2VybmFtZSI6IkphdmFJblVzZSIsImV4cCI6MTcxNTkzODIwMCwiaWF0IjoxNzE1OTM4MjAwfQ"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300
REFRESH_TOKEN_EXPIRE_DAYS = 7

UPLOAD_DIR = "media"
os.makedirs(UPLOAD_DIR, exist_ok=True)
