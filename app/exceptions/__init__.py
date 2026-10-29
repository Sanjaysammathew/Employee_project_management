"""Centralized exceptions package."""

from app.exceptions.custom_exceptions import (
    AppError,
    ConflictError,
    DatabaseError,
    DuplicateUserError,
    EmployeeAlreadyAssignedError,
    EmployeeNotFoundError,
    ForbiddenError,
    InvalidAccessTokenError,
    InvalidCredentialsError,
    JWTConfigurationError,
    NotFoundError,
    ProjectNotFoundError,
    UserNotFoundError,
)
from app.exceptions.exception_handler import register_exception_handlers

__all__ = [
    "AppError",
    "ConflictError",
    "DatabaseError",
    "DuplicateUserError",
    "EmployeeAlreadyAssignedError",
    "EmployeeNotFoundError",
    "ForbiddenError",
    "InvalidAccessTokenError",
    "InvalidCredentialsError",
    "JWTConfigurationError",
    "NotFoundError",
    "ProjectNotFoundError",
    "UserNotFoundError",
    "register_exception_handlers",
]
