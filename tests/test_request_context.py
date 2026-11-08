from fastapi.testclient import TestClient

from app.main import app


def test_request_id_is_preserved_from_client():
    client = TestClient(app)
    response = client.get("/health", headers={"X-Request-ID": "req-test-123"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-test-123"
