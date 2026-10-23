from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models.employee import Employee
from app.models.projects import Projects
from app.repositories.interface.employee_interface import EmployeeInterface
from app.schemas.employee_schema import EmployeeCreate
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


class SqlAlchemyEmployeeRepository(EmployeeInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_employee(self, data: EmployeeCreate) -> Employee:
        try:
            employee = Employee(
                name=data.name,
                salary=data.salary,
            )

            self.db.add(employee)
            await self.db.commit()
            await self.db.refresh(employee)

            return employee

        except SQLAlchemyError as er:
            await self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=str(er),
            ) from er

    async def assign_projects(
        self, employee_id: int, project_ids: list[int]
    ) -> Employee | None:
        # Load the current collection before replacing it. Otherwise SQLAlchemy
        # may try to lazy-load it during assignment, which is unsupported with
        # AsyncSession outside an awaited query.
        try:
            statement = (
                select(Employee)
                .options(selectinload(Employee.projects))
                .where(Employee.id == employee_id)
            )

            result = await self.db.execute(statement)
            employee = result.scalar_one_or_none()

            if employee is None:
                return None

            statement = select(Projects).where(Projects.id.in_(project_ids))

            result = await self.db.scalars(statement)
            projects = list(result.all())

            # Ensure every requested project exists.
            if len({project.id for project in projects}) != len(set(project_ids)):
                return None

            # Replace the employee's current project assignments.
            employee.projects = projects

            await self.db.commit()

            # Reload projects explicitly for the response.
            statement = (
                select(Employee)
                .options(selectinload(Employee.projects))
                .where(Employee.id == employee_id)
            )

            result = await self.db.execute(statement)
            return result.scalar_one()

        except SQLAlchemyError as er:
            await self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=str(er),
            ) from er

    async def extend_project(
        self, employee_id: int, project_ids: list[int]
    ) -> Employee | None:
        try:
            statement = (
                select(Employee)
                .options(selectinload(Employee.projects))
                .where(Employee.id == employee_id)
            )
            result = await self.db.execute(statement)
            employee = result.scalar_one_or_none()

            if employee is None:
                return None

            statement = select(Projects).where(Projects.id.in_(project_ids))
            result = await self.db.scalars(statement)
            projects = list(result.all())

            if len({project.id for project in projects}) != len(set(project_ids)):
                return None

            employee.projects.extend(projects)

            await self.db.commit()

            # Reload projects explicitly for the response.
            statement = (
                select(Employee)
                .options(selectinload(Employee.projects))
                .where(Employee.id == employee_id)
            )

            result = await self.db.execute(statement)
            return result.scalar_one()

        except IntegrityError as er:
            await self.db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Employee is already assigned to one of these projects",
            ) from er

        except SQLAlchemyError as er:
            await self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=str(er),
            ) from er

    async def get_employee_eager(self, employee_id: int) -> Employee | None:
        statement = (
            select(Employee)
            .options(selectinload(Employee.projects))
            .where(Employee.id == employee_id)
        )

        result = await self.db.execute(statement)

        return result.scalar_one_or_none()

    async def get_employees_paginated(self, page: int, page_size: int):
        offset = (page - 1) * page_size

        # Fetch one page of employees and eagerly load their projects.
        statement = (
            select(Employee)
            .options(selectinload(Employee.projects))
            .order_by(Employee.id)
            .offset(offset)
            .limit(page_size)
        )

        result = await self.db.execute(statement)
        employees = result.scalars().all()

        # Total number of employees, not just this page.
        count_statement = select(func.count()).select_from(Employee)
        total = await self.db.scalar(count_statement)

        return {
            "items": employees,
            "page": page,
            "page_size": page_size,
            "total": total or 0,
            "pages": ((total or 0) + page_size - 1) // page_size,
        }

    async def get_employees_with_join(self):
        statement = (
            select(
                Employee.id.label("employee_id"),
                Employee.name.label("employee_name"),
                Employee.salary.label("salary"),
                func.count(Projects.id).label("project_count"),
                func.array_agg(Projects.title).label("project_titles"),
            )
            .join(Employee.projects)
            .group_by(Employee.id, Employee.name, Employee.salary)
            .having(func.count(Projects.id) > 0)
            .order_by(Employee.id)
        )

        result = await self.db.execute(statement)

        return [dict(row._mapping) for row in result.all()]

    async def get_employees_with_joinload(self) -> list[Employee]:
        statement = (
            select(Employee)
            .options(joinedload(Employee.projects))
            .order_by(Employee.id)
        )

        result = await self.db.execute(statement)

        return result.unique().scalars().all()
