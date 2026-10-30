from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from app.exceptions.custom_exceptions import EmployeeNotFoundError
from app.models import Employee
from app.schemas import EmployeeCreate
from app.services.employee_service import EmployeeService


class TestEmployeeService(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.repository = MagicMock()
        self.service = EmployeeService(self.repository)

    async def test_get_employee_returns_employee(self) -> None:
        employee = Employee(
            id=1,
            name="Morgan Employee",
            salary=72000,
            email="morgan.employee@example.com",
            department="Engineering",
        )
        self.repository.get_employee_eager = AsyncMock(return_value=employee)

        result = await self.service.get_employee(1)

        self.assertIs(result, employee)
        self.repository.get_employee_eager.assert_awaited_once_with(1)

    async def test_get_employee_raises_when_employee_is_missing(self) -> None:
        self.repository.get_employee_eager = AsyncMock(return_value=None)

        with self.assertRaises(EmployeeNotFoundError):
            await self.service.get_employee(999)

    async def test_get_employees_returns_paginated_result(self) -> None:
        result_data = {
            "items": [],
            "page": 2,
            "page_size": 5,
            "total": 0,
            "pages": 0,
        }
        self.repository.get_employees_paginated = AsyncMock(return_value=result_data)

        result = await self.service.get_employees(page=2, page_size=5)

        self.assertIs(result, result_data)
        self.repository.get_employees_paginated.assert_awaited_once_with(2, 5)

    async def test_delete_employee_returns_deleted_employee(self) -> None:
        employee = Employee(
            id=1,
            name="Morgan Employee",
            salary=72000,
            email="morgan.employee@example.com",
            department="Engineering",
        )
        self.repository.delete_employee = AsyncMock(return_value=employee)

        result = await self.service.delete_employee(1)

        self.assertIs(result, employee)
        self.repository.delete_employee.assert_awaited_once_with(1)
