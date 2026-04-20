from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pytest


# Patch redis.Redis before importing the app so the module-level
# connect_redis() call never touches a real Redis instance.
@pytest.fixture(autouse=True)
def mock_redis():
    with patch("api.main.connect_redis") as mock_connect:
        mock_client = MagicMock()
        mock_client.ping.return_value = True
        mock_client.hget.return_value = b"queued"
        mock_connect.return_value = mock_client
        yield mock_client


@pytest.fixture()
def client(mock_redis):
    from api.main import app
    return TestClient(app)


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_job_returns_job_id(client, mock_redis):
    mock_redis.hget.return_value = b"queued"
    response = client.post("/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert len(data["job_id"]) == 36  # UUID format


def test_create_job_pushes_to_redis(client, mock_redis):
    response = client.post("/jobs")
    assert response.status_code == 200
    job_id = response.json()["job_id"]
    mock_redis.lpush.assert_called_once_with("job", job_id)
    mock_redis.hset.assert_called_once_with(
        f"job:{job_id}", mapping={"status": "queued"}
    )


def test_get_job_returns_status(client, mock_redis):
    mock_redis.hget.return_value = b"queued"
    response = client.get("/jobs/test-job-id")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "test-job-id"
    assert data["status"] == "queued"


def test_get_job_not_found(client, mock_redis):
    mock_redis.hget.return_value = None
    response = client.get("/jobs/nonexistent-id")
    assert response.status_code == 200
    assert response.json() == {"error": "not found"}
