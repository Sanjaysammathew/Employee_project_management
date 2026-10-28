from fastapi import Depends

from app.config import get_db
from app.repositories import EmployeeRepository, ProjectRepository
from app.repositories.interface import EmployeeInterface, ProjectInterface
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import EmployeeService, ProjectService


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
