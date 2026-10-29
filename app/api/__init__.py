"""API package."""

from app.api.routers import (
    auth_router,
    employee_router,
    health_router,
    project_router,
)

__all__ = ["auth_router", "employee_router", "health_router", "project_router"]
