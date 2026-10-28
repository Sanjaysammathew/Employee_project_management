"""Schema package for request and response models."""

from app.schemas.project_schema import ProjectCreate, ProjectResponse, ProjectSummary
from app.schemas.employee_schema import (
    AssignProjects,
    EmployeeCreate,
    EmployeeCreated,
    EmployeeResponse,
)
from app.schemas.auth_schema import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

__all__ = [
    "LoginRequest",
    "RegisterRequest",
    "TokenResponse",
    "UserResponse",
    "AssignProjects",
    "EmployeeCreate",
    "EmployeeCreated",
    "EmployeeResponse",
    "ProjectCreate",
    "ProjectResponse",
    "ProjectSummary",
]
