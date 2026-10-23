from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.projects import Projects
from app.repositories.interface.project_interface import ProjectInterface


async def create_project(db: AsyncSession, data):
    try:
        project = Projects(
            title=data.title,
            description=data.description,
        )

        db.add(project)
        await db.commit()
        await db.refresh(project)

        return project

    except SQLAlchemyError as er:
        await db.db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(er),
        ) from er


async def get_all_projects(db: AsyncSession):
    statement = select(Projects).order_by(Projects.id)

    result = await db.scalars(statement)
    return result.all()


class SqlAlchemyProjectRepository(ProjectInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_project(self, data):
        return await create_project(self.db, data)

    async def get_all_projects(self):
        return await get_all_projects(self.db)
