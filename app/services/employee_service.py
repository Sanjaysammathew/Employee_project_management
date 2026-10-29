from app.exceptions.custom_exceptions import (
    EmployeeNotFoundError,
    NotFoundError,
)
from app.models import Employee
from app.repositories.interface import EmployeeInterface
from app.schemas import EmployeeCreate


class EmployeeService:
    def __init__(self, repository: EmployeeInterface):
        self.repository = repository

    async def create_employee(self, data: EmployeeCreate) -> Employee:
        return await self.repository.create_employee(data)

    async def delete_employee(self, employee_id: int) -> Employee:
        employee = await self.repository.delete_employee(employee_id)

        if employee is None:
            raise EmployeeNotFoundError

        return employee

    async def assign_projects(
        self, employee_id: int, project_ids: list[int]
    ) -> Employee:
        employee = await self.repository.assign_projects(employee_id, project_ids)

        if employee is None:
            raise NotFoundError("Employee or one or more projects not found")

        return employee

    async def get_employee(self, employee_id: int) -> Employee:
        employee = await self.repository.get_employee_eager(employee_id)

        if employee is None:
            raise EmployeeNotFoundError

        return employee

    async def get_employees(self, page: int, page_size: int):
        return await self.repository.get_employees_paginated(page, page_size)

    async def get_employees_with_join(self):
        return await self.repository.get_employees_with_join()

    async def get_employees_with_joinload(self) -> list[Employee]:
        return await self.repository.get_employees_with_joinload()

    async def extend_project(
        self, employee_id: int, project_ids: list[int]
    ) -> Employee:
        employee = await self.repository.extend_project(employee_id, project_ids)
        if employee is None:
            raise NotFoundError("Employee or one or more projects not found")
        return employee
