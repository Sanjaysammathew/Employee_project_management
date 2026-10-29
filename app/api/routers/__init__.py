"""API route modules."""

from app.api.routers.auth_router import router as auth_router
from app.api.routers.employee_router import router as employee_router
from app.api.routers.health_router import router as health_router
from app.api.routers.project_router import router as project_router

__all__ = ["auth_router", "employee_router", "health_router", "project_router"]
