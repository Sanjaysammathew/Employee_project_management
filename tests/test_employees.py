import pytest
from fastapi.testclient import TestClient

from app.services.email_service import EmailService


@pytest.fixture(autouse=True)
def prevent_real_email(monkeypatch: pytest.MonkeyPatch) -> None:
    async def skip_email(self, to_email: str, employee_name: str) -> None:
        return None

    monkeypatch.setattr(EmailService, "send_employee_created_email", skip_email)


def _employee_payload(
    name: str = "Morgan Employee",
    email: str = "morgan.employee@example.com",
) -> dict[str, str | float]:
    return {
        "name": name,
        "salary": 72000,
        "email": email,
        "department": "Engineering",
    }


def test_create(client: TestClient) -> None:
    response = client.post("/employees/", json=_employee_payload())

    assert response.status_code == 200
    created = response.json()
    assert created == {
        "id": created["id"],
        "name": "Morgan Employee",
        "salary": 72000.0,
        "email": "morgan.employee@example.com",
        "department": "Engineering",
    }

    detail_response = client.get(f"/employees/{created['id']}")
    assert detail_response.status_code == 200
    assert detail_response.json()["name"] == "Morgan Employee"


def test_create_invalid(client: TestClient) -> None:
    invalid_name = client.post(
        "/employees/",
        json=_employee_payload(name="AB"),
    )
    invalid_salary = client.post(
        "/employees/",
        json={**_employee_payload(), "salary": 2000},
    )

    assert invalid_name.status_code == 422
    assert invalid_salary.status_code == 422
    assert invalid_name.json()["detail"]
    assert invalid_salary.json()["detail"]


def test_list_paginated(client: TestClient) -> None:
    for index in range(3):
        response = client.post(
            "/employees/",
            json=_employee_payload(
                name=f"Employee {index}",
                email=f"employee{index}@example.com",
            ),
        )
        assert response.status_code == 200

    response = client.get("/employees/?page=2&page_size=2")

    assert response.status_code == 200
    result = response.json()
    assert result["page"] == 2
    assert result["page_size"] == 2
    assert result["total"] == 3
    assert result["pages"] == 2
    assert len(result["items"]) == 1
    assert result["items"][0]["name"] == "Employee 2"


def test_list_invalid_pagination(client: TestClient) -> None:
    invalid_page = client.get("/employees/?page=0")
    invalid_page_size = client.get("/employees/?page_size=101")

    assert invalid_page.status_code == 422
    assert invalid_page_size.status_code == 422


def test_get_missing(client: TestClient) -> None:
    response = client.get("/employees/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Employee not found"}


def test_assign_projects(
    client: TestClient,
    project_id: int,
) -> None:
    created = client.post("/employees/", json=_employee_payload()).json()

    response = client.put(
        f"/employees/{created['id']}/projects",
        json={"project_ids": [project_id]},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["id"] == created["id"]
    assert result["projects"] == [{"id": project_id, "title": "API Test Project"}]


def test_assign_missing_project(
    client: TestClient,
) -> None:
    created = client.post("/employees/", json=_employee_payload()).json()

    response = client.put(
        f"/employees/{created['id']}/projects",
        json={"project_ids": [999999]},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Employee or one or more projects not found"
    }


def test_extend_projects(
    client: TestClient,
    project_id: int,
) -> None:
    created = client.post("/employees/", json=_employee_payload()).json()
    payload = {"project_ids": [project_id]}

    response = client.patch(f"/employees/{created['id']}", json=payload)

    assert response.status_code == 200
    projects = response.json()["projects"]
    assert len(projects) == 1
    assert projects[0]["id"] == project_id
    assert projects[0]["title"] == "API Test Project"

    duplicate_response = client.patch(
        f"/employees/{created['id']}",
        json=payload,
    )
    assert duplicate_response.status_code == 409


def test_project_reports(
    client: TestClient,
    project_id: int,
) -> None:
    created = client.post("/employees/", json=_employee_payload()).json()
    assignment = client.put(
        f"/employees/{created['id']}/projects",
        json={"project_ids": [project_id]},
    )
    assert assignment.status_code == 200

    report_response = client.get("/employees/reports/employees-projects")
    join_load_response = client.get("/employees/queries/join-load")

    assert report_response.status_code == 200
    report = report_response.json()
    assert len(report) == 1
    assert report[0]["employee_id"] == created["id"]
    assert report[0]["employee_name"] == "Morgan Employee"
    assert report[0]["project_count"] == 1
    assert report[0]["project_titles"] == ["API Test Project"]

    assert join_load_response.status_code == 200
    loaded_employees = join_load_response.json()
    assert len(loaded_employees) == 1
    assert loaded_employees[0]["id"] == created["id"]
    assert loaded_employees[0]["projects"] == [
        {"id": project_id, "title": "API Test Project"}
    ]


def test_delete(client: TestClient) -> None:
    created = client.post("/employees/", json=_employee_payload()).json()

    delete_response = client.delete(f"/employees/{created['id']}")
    detail_response = client.get(f"/employees/{created['id']}")

    assert delete_response.status_code == 200
    assert delete_response.json() == {
        "message": "Employee deleted successfully"
    }
    assert detail_response.status_code == 404


def test_delete_missing(
    client: TestClient,
) -> None:
    response = client.delete("/employees/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Employee not found"}
