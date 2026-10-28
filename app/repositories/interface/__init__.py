"""Repository interfaces."""

from app.repositories.interface.employee_interface import EmployeeInterface
from app.repositories.interface.project_interface import ProjectInterface
from app.repositories.interface.user_interface import UserInterface

__all__ = [
    "EmployeeInterface",
    "ProjectInterface",
    "UserInterface",
]
