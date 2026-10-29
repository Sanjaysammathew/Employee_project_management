from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.custom_exceptions import DatabaseError, DuplicateUserError
from app.models import User
from app.repositories.interface import UserInterface


class UserRepository(UserInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_identifier(self, identifier: str) -> User | None:
        try:
            statement = select(User).where(
                or_(User.username == identifier, User.email == identifier)
            )
            return await self.db.scalar(statement)
        except SQLAlchemyError as er:
            await self.db.rollback()
            raise DatabaseError() from er

    async def get_by_username_or_email(
        self, username: str, email: str
    ) -> User | None:
        try:
            statement = select(User).where(
                or_(User.username == username, User.email == email)
            )
            return await self.db.scalar(statement)
        except SQLAlchemyError as er:
            await self.db.rollback()
            raise DatabaseError() from er

    async def get_by_id(self, user_id: int) -> User | None:
        try:
            return await self.db.get(User, user_id)
        except SQLAlchemyError as er:
            await self.db.rollback()
            raise DatabaseError() from er

    async def create_user(
        self, username: str, email: str, password_hash: str
    ) -> User:
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role="user",
        )
        try:
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except IntegrityError as exc:
            await self.db.rollback()
            constraint_name = getattr(exc.orig, "constraint_name", None)
            if constraint_name is None:
                constraint_name = getattr(
                    getattr(exc.orig, "diag", None),
                    "constraint_name",
                    None,
                )
            if constraint_name in {"uq_users_username", "uq_users_email"}:
                raise DuplicateUserError(
                    "Username or email is already registered"
                ) from exc
            raise DatabaseError() from exc
        except SQLAlchemyError as er:
            await self.db.rollback()
            raise DatabaseError() from er

    async def delete_user(self, user_id: int) -> User | None:
        try:
            user = await self.db.get(User, user_id)
            if user is None:
                return None

            await self.db.delete(user)
            await self.db.commit()
            return user
        except SQLAlchemyError as er:
            await self.db.rollback()
            raise DatabaseError() from er
