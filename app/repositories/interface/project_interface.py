from abc import ABC, abstractmethod
from typing import Any

from app.models import Projects


class ProjectInterface(ABC):
    @abstractmethod
    async def create_project(self, data: Any) -> Any:
        pass

    @abstractmethod
    async def get_all_projects(self) -> list[Any]:
        pass

    @abstractmethod
    async def get_project_employee_report(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def get_project_employee_count_report(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def delete_project(self, project_id: int) -> Projects | None:
        pass
