from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.core.config import settings
from app.exceptions.custom_exceptions import (
    InvalidAccessTokenError,
    JWTConfigurationError,
)

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(subject: str) -> str:
    secret = settings.JWT_SECRET_KEY
    if secret is None:
        raise JWTConfigurationError("JWT_SECRET_KEY is not configured")

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": subject, "iat": now, "exp": expires_at, "type": "access"},
        secret.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token(subject: str) -> str:
    secret = settings.JWT_SECRET_KEY
    if secret is None:
        raise JWTConfigurationError("JWT_SECRET_KEY is not configured")
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    return jwt.encode(
        {"sub": subject, "iat": now, "exp": expires_at, "type": "refresh"},
        secret.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> str:
    secret = settings.JWT_SECRET_KEY
    if secret is None:
        raise JWTConfigurationError("JWT_SECRET_KEY is not configured")

    try:
        payload = jwt.decode(
            token,
            secret.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["exp", "sub", "type"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise InvalidAccessTokenError("Access token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise InvalidAccessTokenError("The access token is invalid or expired") from exc

    subject = payload.get("sub")
    if (
        payload.get("type") != "access"
        or not isinstance(subject, str)
        or not subject.isdecimal()
    ):
        raise InvalidAccessTokenError("The access token is invalid or expired")
    return subject


def decode_refresh_token(token: str) -> str:
    secret = settings.JWT_SECRET_KEY

    if secret is None:
        raise JWTConfigurationError("JWT_SECRET_KEY is not configured")

    try:
        payload = jwt.decode(
            token,
            secret.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["exp", "sub", "type"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise InvalidAccessTokenError("Refresh token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise InvalidAccessTokenError(
            "The refresh token is invalid or expired"
        ) from exc

    subject = payload.get("sub")

    if (
        payload.get("type") != "refresh"
        or not isinstance(subject, str)
        or not subject.isdecimal()
    ):
        raise InvalidAccessTokenError("The refresh token is invalid or expired")

    return subject
