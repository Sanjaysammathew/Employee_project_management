import os
import asyncio
from collections.abc import AsyncIterator

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import delete, make_url
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from app.core import settings
from app.database import Base, get_db
from app.models import Employee, Projects, User, employee_project
from app.main import app

load_dotenv()

# 1. Read and validate the test database URL
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise RuntimeError("Set TEST_DATABASE_URL in your .env file")

test_url = make_url(TEST_DATABASE_URL)
app_url = make_url(settings.database_url)


# 2. Create the test database engine and session factory
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture
def project_id(clean_test_data) -> int:
    async def create_project():
        async with TestSessionLocal() as db:
            project = Projects(
                title="API Test Project",
                description="Project created for Employee API tests",
            )

            db.add(project)
            await db.commit()
            await db.refresh(project)

            return project.id

    return asyncio.run(create_project())


# 3. Create tables before tests and remove them afterward
@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    async def setup():
        async with test_engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    asyncio.run(setup())

    yield

    async def cleanup():
        try:
            async with test_engine.begin() as connection:
                await connection.run_sync(Base.metadata.drop_all)
        finally:
            await test_engine.dispose()

    asyncio.run(cleanup())


# 4. Clear data before each test
@pytest.fixture(autouse=True)
def clean_test_data(setup_test_database):
    async def clear():
        async with test_engine.begin() as connection:
            await connection.execute(delete(employee_project))
            await connection.execute(delete(Employee))
            await connection.execute(delete(Projects))
            await connection.execute(delete(User))

    asyncio.run(clear())


# 5. Override the application's database dependency
@pytest.fixture
def client(clean_test_data):

    async def override_get_db():
        async with TestSessionLocal() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
