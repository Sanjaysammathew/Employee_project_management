from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import Base, engine

# Import models so SQLAlchemy registers their tables.
from app.models import Employee, Projects, User, employee_project

from app.api import auth_router, employee_router, project_router


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