from app.core import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.exceptions.custom_exceptions import (
    DuplicateUserError,
    InvalidAccessTokenError,
    InvalidCredentialsError,
    UserNotFoundError,
)
from app.models import User
from app.repositories.interface import UserInterface
from app.schemas import LoginRequest, RegisterRequest


class AuthService:
    def __init__(self, repository: UserInterface):
        self.repository = repository

    async def register(self, data: RegisterRequest) -> User:
        existing_user = await self.repository.get_by_username_or_email(
            data.username,
            str(data.email),
        )
        if existing_user is not None:
            raise DuplicateUserError(
                "Username or email is already registered"
            )

        return await self.repository.create_user(
            username=data.username,
            email=str(data.email),
            password_hash=hash_password(data.password),
        )

    async def login(self, data: LoginRequest) -> tuple[str, str]:
        user = await self.repository.get_by_identifier(data.username)
        if user is None or not verify_password(data.password, user.password_hash):
            raise InvalidCredentialsError

        subject = str(user.id)
        return create_access_token(subject), create_refresh_token(subject)

    async def refresh(self, refresh_token: str) -> tuple[str, str]:
        subject = decode_refresh_token(refresh_token)
        user = await self.repository.get_by_id(int(subject))
        if user is None:
            raise InvalidAccessTokenError(
                "The refresh token is invalid or expired"
            )

        return create_access_token(subject), create_refresh_token(subject)

    async def delete_user(self, user_id: int) -> None:
        user = await self.repository.delete_user(user_id)
        if user is None:
            raise UserNotFoundError
