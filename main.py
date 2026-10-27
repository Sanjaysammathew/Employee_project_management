from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config.database import engine, Base

# Import models so SQLAlchemy registers their tables.
from app.models.employee import Employee
from app.models.projects import Projects
from app.models.association import employee_project
from app.models.user import User

from app.api.router.employee_router import router as employee_router
from app.api.router.project_router import router as project_router
from app.api.router.auth_router import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(
    title="Employee Project API",
    lifespan=lifespan,
)

app.include_router(employee_router)
app.include_router(project_router)
app.include_router(auth_router)


@app.get("/")
async def home():
    return {"message": "Employee Project API is running"}