from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.utils.logging_config import configure_logging

from app.core import settings
from app.database import Base, engine
from app.exceptions.exception_handler import register_exception_handlers

# Import models so SQLAlchemy registers their tables.
from app.models import Employee, Projects, User, employee_project

from app.api import (
    auth_router,
    employee_router,
    health_router,
    project_router,
)

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

register_exception_handlers(app)

app.include_router(employee_router)
app.include_router(project_router)
app.include_router(auth_router)
app.include_router(health_router)


@app.get("/")
async def home():
    return {"message": "Employee Project API is running"}
