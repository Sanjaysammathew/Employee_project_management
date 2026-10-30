from contextlib import asynccontextmanager
import logging
import time

from fastapi import FastAPI, Request

from app.utils.logging_config import configure_logging

from app.core import settings
from app.database import Base, engine
from app.exceptions.exception_handler import register_exception_handlers

# Import models so SQLAlchemy registers their tables.
from app.models import Employee, Projects, User, employee_project

from fastapi import FastAPI, Request
import time
import logging
import uuid

from app.api import (
    auth_router,
    employee_router,
    health_router,
    project_router,
)

configure_logging()
logger = logging.getLogger("app")


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


app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

logger = logging.getLogger(__name__)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    # 1. Generate a unique correlation ID
    correlation_id = str(uuid.uuid4())

    # 2. Store it in the request state
    request.state.correlation_id = correlation_id

    start_time = time.perf_counter()

    logger.info(
        "Request started: %s %s | Correlation ID: %s",
        request.method,
        request.url.path,
        correlation_id,
    )

    response = await call_next(request)

    process_time = time.perf_counter() - start_time

    # 3. Add headers to the response
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Correlation-ID"] = correlation_id

    # 4. Log request completion
    logger.info(
        "Request completed: %s %s | Status: %s | Time: %.4f seconds | Correlation ID: %s",
        request.method,
        request.url.path,
        response.status_code,
        process_time,
        correlation_id,
    )

    return response


register_exception_handlers(app)

app.include_router(employee_router)
app.include_router(project_router)
app.include_router(auth_router)
app.include_router(health_router)


@app.get("/")
async def home():
    return {"message": "Employee Project API is running"}
