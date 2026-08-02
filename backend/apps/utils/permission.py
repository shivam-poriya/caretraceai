from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from config.settings import base as settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def verify_user_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, getattr(settings, "SECRET_KEY"), algorithms=[getattr(settings, "ALGORITHM", "HS256")])
        _id: str = payload.get("sub")
        if _id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return {"_id": _id}
