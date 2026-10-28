"""Dependency injection helpers for the API."""

from app.api.dependency.auth_dependencies import (
    get_auth_service,
    get_current_user,
    get_user_repository,
    require_roles,
)
from app.api.dependency.dependencies import (
    get_employee_repository,
    get_employee_service,
    get_project_repository,
    get_project_service,
)

__all__ = [
    "get_auth_service",
    "get_current_user",
    "get_user_repository",
    "require_roles",
    "get_employee_repository",
    "get_employee_service",
    "get_project_repository",
    "get_project_service",
]
