from datetime import UTC, datetime, timedelta
from typing import Any

import argon2
from jose import jwt

from hbit_api.core.config import settings

ph = argon2.PasswordHasher()


ALGORITHM = "HS256"


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(UTC) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return ph.verify(hashed_password, plain_password)


def get_password_hash(password: str) -> str:
    return ph.hash(password)
