from pydantic import BaseModel, ConfigDict , Field
from app.schemas.project_schema import ProjectSummary

NAME = dict(min_length=3, max_length=100, strip_whitespace=True)
SALARY = dict(gt=2_000, lt=100_000)

class EmployeeCreate(BaseModel):
    name: str = Field(**NAME,default="") 
    salary: float = Field(**SALARY)


class EmployeeCreated(BaseModel):
    id: int
    name: str = Field(**NAME) 
    salary: float 

class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str = Field(**NAME) 
    salary: float 
    projects: list[ProjectSummary] = []


class AssignProjects(BaseModel):
    project_ids: list[int]