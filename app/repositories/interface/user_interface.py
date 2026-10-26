from abc import ABC, abstractmethod

from app.models.user import User


class UserInterface(ABC):
    @abstractmethod
    async def get_by_identifier(self, identifier: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_username_or_email(
        self, username: str, email: str
    ) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def create_user(
        self, username: str, email: str, password_hash: str
    ) -> User:
        raise NotImplementedError

    @abstractmethod
    async def delete_user(self, user_id: int) -> User | None:
        raise NotImplementedError
