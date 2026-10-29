from collections.abc import Awaitable, Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import decode_access_token
from app.database import get_db
from app.exceptions.custom_exceptions import (
    ForbiddenError,
    InvalidAccessTokenError,
)
from app.models import User
from app.repositories import UserRepository
from app.repositories.interface import UserInterface
from app.services import AuthService

bearer_scheme = HTTPBearer(auto_error=False)


def get_user_repository(
    db: AsyncSession = Depends(get_db),
) -> UserInterface:
    return UserRepository(db)


def get_auth_service(
    repository: UserInterface = Depends(get_user_repository),
) -> AuthService:
    return AuthService(repository)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    repository: UserInterface = Depends(get_user_repository),
) -> User:
    if credentials is None:
        raise InvalidAccessTokenError("Invalid or missing access token")

    subject = decode_access_token(credentials.credentials)

    user = await repository.get_by_id(int(subject))
    if user is None:
        raise InvalidAccessTokenError("Invalid or missing access token")
    return user


def require_roles(*allowed_roles: str) -> Callable[..., Awaitable[User]]:
    async def check_user_role(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenError()
        return current_user

    return check_user_role
