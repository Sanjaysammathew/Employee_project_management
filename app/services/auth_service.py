from fastapi import HTTPException

from app.config.security import (
    JWTConfigurationError,
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.implement.user_repository import DuplicateUserError
from app.repositories.interface.user_interface import UserInterface
from app.schemas.auth_schema import LoginRequest, RegisterRequest


class AuthService:
    def __init__(self, repository: UserInterface):
        self.repository = repository

    async def register(self, data: RegisterRequest) -> User:
        existing_user = await self.repository.get_by_username_or_email(
            data.username,
            str(data.email),
        )
        if existing_user is not None:
            raise HTTPException(
                status_code=409,
                detail="Username or email is already registered",
            )

        try:
            return await self.repository.create_user(
                username=data.username,
                email=str(data.email),
                password_hash=hash_password(data.password),
            )
        except DuplicateUserError as exc:
            raise HTTPException(
                status_code=409,
                detail="Username or email is already registered",
            ) from exc

    async def login(self, data: LoginRequest) -> str:
        user = await self.repository.get_by_identifier(data.username)
        if user is None or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=401,
                detail="Invalid username/email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            return create_access_token(str(user.id))
        except JWTConfigurationError as exc:
            raise HTTPException(
                status_code=503,
                detail="Authentication is not configured",
            ) from exc

    async def delete_user(self, user_id: int) -> None:
        user = await self.repository.delete_user(user_id)
        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )
