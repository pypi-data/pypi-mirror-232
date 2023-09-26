import pytest
from fastapi.testclient import TestClient

from tests.fastapi_proxy_service.main import app


@pytest.fixture
def client():
    """
    Fixture to HTTP Client
    :return:
    """
    return TestClient(app=app, base_url="http://localhost:8001")
