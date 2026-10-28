from fastapi import HTTPException
from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Employee, Projects, employee_project
from app.repositories.interface import ProjectInterface
from app.schemas import ProjectCreate


class ProjectRepository(ProjectInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_project(self, data: ProjectCreate) -> Projects:
        try:
            result = await self.db.execute(
                text(
                    "CALL public.insert_project("
                    ":title, :description, :status, CAST(NULL AS INTEGER))"
                ),
                {
                    "title": data.title,
                    "description": data.description,
                    "status": data.status,
                },
            )
            project_id = result.scalar_one()

            project = await self.db.scalar(
                select(Projects).where(Projects.id == project_id)
            )
            if project is None:
                raise RuntimeError(
                    "insert_project procedure created a project that could not be retrieved"
                )

            await self.db.commit()
            return project

        except RuntimeError:
            await self.db.rollback()
            raise

        except SQLAlchemyError as er:
            await self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=str(er),
            ) from er

    async def get_all_projects(self) -> list[Projects]:
        statement = select(Projects).order_by(Projects.id)
        result = await self.db.scalars(statement)
        return list(result.all())

    async def get_project_employee_report(self) -> list[dict[str, object]]:
        statement = (
            select(
                Projects.id.label("project_id"),
                Projects.title,
                Projects.status,
                func.count(Employee.id).label("employee_count"),
                func.array_agg(Employee.name)
                .filter(Employee.id.is_not(None))
                .label("employee_names"),
            )
            .outerjoin(Projects.employees)
            .group_by(Projects.id, Projects.title, Projects.status)
            .order_by(Projects.id)
        )

        try:
            result = await self.db.execute(statement)
            return [
                {
                    **dict(row._mapping),
                    "employee_names": row.employee_names or [],
                }
                for row in result
            ]
        except SQLAlchemyError as er:
            raise HTTPException(
                status_code=500,
                detail=str(er),
            ) from er

    async def get_project_employee_count_report(self) -> list[dict[str, object]]:
        employee_count = (
            select(func.count(employee_project.c.employee_id))
            .where(employee_project.c.project_id == Projects.id)
            .scalar_subquery()
        )
        statement = (
            select(
                Projects.id.label("project_id"),
                Projects.title,
                Projects.status,
                employee_count.label("employee_count"),
            )
            .order_by(Projects.id)
        )

        try:
            result = await self.db.execute(statement)
            return [dict(row._mapping) for row in result]
        except SQLAlchemyError as er:
            raise HTTPException(
                status_code=500,
                detail=str(er),
            ) from er

    async def delete_project(self, project_id: int) -> bool:
        try:
            statement = (
                select(Projects)
                .options(selectinload(Projects.employees))
                .where(Projects.id == project_id)
            )
            result = await self.db.execute(statement)
            project = result.scalar_one_or_none()

            if project is None:
                return False

            await self.db.delete(project)
            await self.db.commit()
            return True

        except SQLAlchemyError as er:
            await self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=str(er),
            ) from er
