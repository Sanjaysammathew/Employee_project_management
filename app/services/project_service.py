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
