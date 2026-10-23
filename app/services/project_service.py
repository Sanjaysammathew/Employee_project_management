from fastapi import HTTPException

from app.repositories.interface.project_interface import ProjectInterface
from app.models.projects import Projects
from app.schemas.project_schema import ProjectCreate


class ProjectService:
    def __init__(self, repository: ProjectInterface):
        self.repository = repository

    async def create_project(self, data: ProjectCreate) -> Projects:
        return await self.repository.create_project(data)

    async def get_projects(self) -> list[Projects]:
        return await self.repository.get_all_projects()

    async def get_project_employee_report(self) -> list[dict[str, object]]:
        return await self.repository.get_project_employee_report()

    async def get_project_employee_count_report(self) -> list[dict[str, object]]:
        return await self.repository.get_project_employee_count_report()

    async def delete_project(self, project_id: int) -> None:
        deleted = await self.repository.delete_project(project_id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Project not found",
            )
