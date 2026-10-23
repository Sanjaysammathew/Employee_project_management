from abc import ABC, abstractmethod
from typing import Any


class ProjectInterface(ABC):
    @abstractmethod
    async def create_project(self, data: Any) -> Any:
        pass

    @abstractmethod
    async def get_all_projects(self) -> list[Any]:
        pass
