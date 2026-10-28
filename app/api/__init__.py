"""API package."""

from app.api.router.auth_router import router as auth_router
from app.api.router.employee_router import router as employee_router
from app.api.router.project_router import router as project_router

__all__ = ["auth_router", "employee_router", "project_router"]
