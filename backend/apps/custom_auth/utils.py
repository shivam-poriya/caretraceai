import bcrypt
from datetime import datetime, timedelta
from jose import jwt
from config.settings import base as settings


def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')[:72]  # Truncate to max 72 bytes as per bcrypt spec
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode('utf-8')[:72]
    hash_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hash_bytes)


class PwdContextAdapter:
    def verify(self, secret: str, hash: str) -> bool:
        return verify_password(secret, hash)

    def hash(self, secret: str) -> str:
        return get_password_hash(secret)


pwd_context = PwdContextAdapter()


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 300)
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, getattr(settings, "SECRET_KEY"), algorithm=getattr(settings, "ALGORITHM", "HS256")
    )
    return encoded_jwt


def create_refresh_token(data: dict):
    expire = datetime.utcnow() + timedelta(days=getattr(settings, "REFRESH_TOKEN_EXPIRE_DAYS", 7))
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    refresh_token = jwt.encode(
        to_encode, getattr(settings, "REFRESH_TOKEN_SECRET_KEY"), algorithm="HS256"
    )
    return refresh_token
