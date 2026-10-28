from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_db
from app.api.dependency import get_employee_service
from app.repositories.interface import EmployeeInterface
from app.schemas import (
    EmployeeCreate,
    EmployeeCreated,
    EmployeeResponse,
    AssignProjects,
)
from app.services import EmployeeService

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post("/", response_model=EmployeeCreated)
async def create_employee(
    data: EmployeeCreate,
    service: EmployeeService = Depends(get_employee_service),
):
    return await service.create_employee(data)


@router.delete("/{employee_id}")
async def delete_employee(
    employee_id: int,
    service: EmployeeService = Depends(get_employee_service),
):
    await service.delete_employee(employee_id)
    return {"message": "Employee deleted successfully"}


@router.put("/{employee_id}/projects", response_model=EmployeeResponse)
async def assign_projects(
    employee_id: int,
    data: AssignProjects,
    service: EmployeeService = Depends(get_employee_service),
):
    return await service.assign_projects(employee_id, data.project_ids)


@router.get("/", response_model=dict)
async def get_employees(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: EmployeeService = Depends(get_employee_service),
):
    result = await service.get_employees(page, page_size)

    return {
        **result,
        "items": [
            EmployeeResponse.model_validate(employee) for employee in result["items"]
        ],
    }


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int,
    service: EmployeeService = Depends(get_employee_service),
):
    return await service.get_employee(employee_id)


@router.get("/reports/employees-projects")
async def employees_projects_report(
    service: EmployeeService = Depends(get_employee_service),
):
    return await service.get_employees_with_join()


@router.get("/queries/join-load", response_model=list[EmployeeResponse])
async def join_load(service: EmployeeService = Depends(get_employee_service)):
    employees = await service.get_employees_with_joinload()
    return employees


@router.patch("/{employee_id}")
async def extend_project(
    employee_id: int,
    data: AssignProjects,
    service: EmployeeService = Depends(get_employee_service),
):
    return await service.extend_project(employee_id, data.project_ids)
