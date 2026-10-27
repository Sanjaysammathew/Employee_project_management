from collections.abc import Awaitable, Callable

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.config.security import (
    InvalidAccessTokenError,
    JWTConfigurationError,
    decode_access_token,
)
from app.models.user import User
from app.repositories.implement.user_repository import UserRepository
from app.repositories.interface.user_interface import UserInterface
from app.services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    auto_error=False,
)


def get_user_repository(
    db: AsyncSession = Depends(get_db),
) -> UserInterface:
    return UserRepository(db)


def get_auth_service(
    repository: UserInterface = Depends(get_user_repository),
) -> AuthService:
    return AuthService(repository)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    repository: UserInterface = Depends(get_user_repository),
) -> User:
    unauthorized = HTTPException(
        status_code=401,
        detail="Invalid or missing access token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise unauthorized

    try:
        subject = decode_access_token(token)
    except InvalidAccessTokenError:
        raise unauthorized from None
    except JWTConfigurationError as exc:
        raise HTTPException(
            status_code=503,
            detail="Authentication is not configured",
        ) from exc

    user = await repository.get_by_id(int(subject))
    if user is None:
        raise unauthorized
    return user


def require_roles(*allowed_roles: str) -> Callable[..., Awaitable[User]]:
    async def check_user_role(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource",
            )
        return current_user

    return check_user_role
