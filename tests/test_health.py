from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/health/")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "message": "Application is running",
    }


def test_health_endpoint_is_documented(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/health/" in response.json()["paths"]
