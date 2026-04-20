import os
import pytest
from unittest.mock import MagicMock, patch

# Provide dummy env vars so connect_redis() doesn't KeyError on import
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ.setdefault("REDIS_PASSWORD", "testpassword")


@pytest.fixture()
def mock_redis():
    mock_client = MagicMock()
    mock_client.ping.return_value = True
    mock_client.hget.return_value = b"queued"
    return mock_client


@pytest.fixture()
def client(mock_redis):
    from fastapi.testclient import TestClient
    with patch("api.main.connect_redis", return_value=mock_redis):
        from api.main import app
        with TestClient(app) as c:
            yield c
