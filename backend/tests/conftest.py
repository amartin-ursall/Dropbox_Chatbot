"""
Pytest configuration and fixtures
"""
import pytest
from httpx import AsyncClient, ASGITransport
from pathlib import Path
import shutil


@pytest.fixture
async def test_client():
    """
    Fixture that provides an async HTTP client for testing FastAPI app
    """
    from app.main import app  # Import will fail initially - this is expected in RED phase

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
async def client(test_client):
    """Alias for test_client for convenience"""
    return test_client


@pytest.fixture
def tmp_path(tmp_path_factory):
    """
    Provides a temporary directory for file uploads during tests
    """
    temp_dir = tmp_path_factory.mktemp("uploads")
    yield temp_dir
    # Cleanup after test
    shutil.rmtree(temp_dir, ignore_errors=True)
