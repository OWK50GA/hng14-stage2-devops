def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_job_returns_job_id(client):
    response = client.post("/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert len(data["job_id"]) == 36  # UUID format


def test_create_job_pushes_to_redis(client, mock_redis):
    response = client.post("/jobs")
    assert response.status_code == 200
    job_id = response.json()["job_id"]
    mock_redis.lpush.assert_called_with("job", job_id)
    mock_redis.hset.assert_called_with(
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
