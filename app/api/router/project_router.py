from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.api.dependency.dependencies import get_project_service
from app.repositories.interface.project_interface import ProjectInterface
from app.schemas.project_schema import ProjectCreate, ProjectResponse
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", response_model=ProjectResponse)
async def create_project(
    data: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
):
    return await service.create_project(data)


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
):
    await service.delete_project(project_id)
    return {"message": "Project deleted successfully"}


@router.get("/", response_model=list[ProjectResponse])
async def get_projects(service: ProjectService = Depends(get_project_service)):
    return await service.get_projects()


@router.get("/reports/employee-summary")
async def get_project_employee_report(
    service: ProjectService = Depends(get_project_service),
):
    return await service.get_project_employee_report()


@router.get("/reports/employee-count")
async def get_project_employee_count_report(
    service: ProjectService = Depends(get_project_service),
):
    return await service.get_project_employee_count_report()
