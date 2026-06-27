"""
Admin authentication — a single shared admin account (no user table, no
signup flow), since this only needs you/your team logging in.

ADMIN_USERNAME and ADMIN_PASSWORD_HASH live in .env (the hash, never the
real password — see backend/README.md for how to generate it).
/auth/login checks the submitted credentials and returns a JWT. Protected
routes use get_current_admin as a dependency to require that token.
"""

import os
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-in-your-.env")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60 * 12  # 12 hours

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verify_admin_credentials(username: str, password: str) -> bool:
    if username != ADMIN_USERNAME or not ADMIN_PASSWORD_HASH:
        return False
    return bcrypt.checkpw(password.encode(), ADMIN_PASSWORD_HASH.encode())


def create_access_token() -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    payload = {"sub": ADMIN_USERNAME, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_admin(token: str = Depends(oauth2_scheme)) -> str:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired session — please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username != ADMIN_USERNAME:
            raise credentials_error
        return username
    except JWTError:
        raise credentials_error