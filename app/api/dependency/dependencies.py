from fastapi import Depends

from app.config.database import get_db
from app.repositories.interface.employee_interface import EmployeeInterface
from app.repositories.interface.project_interface import ProjectInterface
from app.repositories.implement.employee_repository import EmployeeRepository
from app.repositories.implement.project_repository import ProjectRepository
from app.services.employee_service import EmployeeService
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.project_service import ProjectService


def get_employee_repository(
    db: AsyncSession = Depends(get_db),
) -> EmployeeInterface:
    return EmployeeRepository(db)


def get_employee_service(
    repository: EmployeeInterface = Depends(get_employee_repository),
) -> EmployeeService:
    return EmployeeService(repository)


def get_project_repository(
    db: AsyncSession = Depends(get_db),
) -> ProjectInterface:
    return ProjectRepository(db)


def get_project_service(
    repository: ProjectInterface = Depends(get_project_repository),
) -> ProjectService:
    return ProjectService(repository)
