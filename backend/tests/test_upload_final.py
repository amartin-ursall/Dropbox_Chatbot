"""
Tests for final upload endpoint - AD-6
Tests file upload to Dropbox with authentication
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path
import tempfile
import os

from app.main import app, TEMP_STORAGE_PATH


client = TestClient(app)


@pytest.fixture
def mock_auth_token():
    """Mock authenticated session with access token"""
    with patch("app.auth.get_access_token") as mock:
        mock.return_value = "test_access_token_12345"
        yield mock


@pytest.fixture
def temp_test_file():
    """Create a temporary test file"""
    # Create a temp file in TEMP_STORAGE_PATH
    os.makedirs(TEMP_STORAGE_PATH, exist_ok=True)
    file_id = "test-file-123"
    temp_file = TEMP_STORAGE_PATH / f"{file_id}_test_document.pdf"

    with open(temp_file, 'wb') as f:
        f.write(b"Test PDF content")

    yield file_id, temp_file

    # Cleanup
    if temp_file.exists():
        temp_file.unlink()


def test_upload_final_success(mock_auth_token, temp_test_file):
    """Test #16: Upload file to Dropbox successfully"""
    file_id, temp_file = temp_test_file

    # Mock dropbox upload
    with patch("app.main.upload_file_to_dropbox", new_callable=AsyncMock) as mock_upload:
        mock_upload.return_value = {
            "success": True,
            "path": "/Documentos/Facturas/2025-01-15_Factura_ClienteA.pdf",
            "name": "2025-01-15_Factura_ClienteA.pdf",
            "id": "id:abc123",
            "size": 1024
        }

        response = client.post(
            "/api/upload-final",
            json={
                "file_id": file_id,
                "new_filename": "2025-01-15_Factura_ClienteA.pdf",
                "dropbox_path": "/Documentos/Facturas"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Archivo subido exitosamente a Dropbox"
        assert data["dropbox_path"] == "/Documentos/Facturas/2025-01-15_Factura_ClienteA.pdf"
        assert data["dropbox_name"] == "2025-01-15_Factura_ClienteA.pdf"

        # Verify upload was called with correct parameters
        mock_upload.assert_called_once()
        call_args = mock_upload.call_args
        assert call_args.kwargs["access_token"] == "test_access_token_12345"
        assert call_args.kwargs["new_filename"] == "2025-01-15_Factura_ClienteA.pdf"
        assert call_args.kwargs["dropbox_path"] == "/Documentos/Facturas"


def test_upload_final_not_authenticated():
    """Test #17: Upload fails when user is not authenticated"""
    with patch("app.auth.get_access_token") as mock:
        from fastapi import HTTPException
        mock.side_effect = HTTPException(status_code=401, detail="Not authenticated")

        response = client.post(
            "/api/upload-final",
            json={
                "file_id": "test-file-123",
                "new_filename": "2025-01-15_Factura_ClienteA.pdf",
                "dropbox_path": "/Documentos/Facturas"
            }
        )

        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]


def test_upload_final_file_not_found(mock_auth_token):
    """Test #18: Upload fails when temporary file is not found"""
    response = client.post(
        "/api/upload-final",
        json={
            "file_id": "nonexistent-file-id",
            "new_filename": "2025-01-15_Factura_ClienteA.pdf",
            "dropbox_path": "/Documentos/Facturas"
        }
    )

    assert response.status_code == 404
    assert "Temporary file not found" in response.json()["detail"]


def test_upload_final_dropbox_error(mock_auth_token, temp_test_file):
    """Test #19: Upload handles Dropbox API errors"""
    file_id, temp_file = temp_test_file

    # Mock dropbox upload to raise HTTPException
    with patch("app.main.upload_file_to_dropbox", new_callable=AsyncMock) as mock_upload:
        from fastapi import HTTPException
        mock_upload.side_effect = HTTPException(
            status_code=500,
            detail="Dropbox upload failed: Invalid path"
        )

        response = client.post(
            "/api/upload-final",
            json={
                "file_id": file_id,
                "new_filename": "2025-01-15_Factura_ClienteA.pdf",
                "dropbox_path": "/Documentos/Facturas"
            }
        )

        assert response.status_code == 500
        assert "Dropbox upload failed" in response.json()["detail"]


def test_upload_final_cleans_temp_file(mock_auth_token, temp_test_file):
    """Test #20: Temporary file is deleted after successful upload"""
    file_id, temp_file = temp_test_file

    assert temp_file.exists(), "Temp file should exist before upload"

    # Mock dropbox upload
    with patch("app.main.upload_file_to_dropbox", new_callable=AsyncMock) as mock_upload:
        mock_upload.return_value = {
            "success": True,
            "path": "/Documentos/Facturas/2025-01-15_Factura_ClienteA.pdf",
            "name": "2025-01-15_Factura_ClienteA.pdf",
            "id": "id:abc123",
            "size": 1024
        }

        response = client.post(
            "/api/upload-final",
            json={
                "file_id": file_id,
                "new_filename": "2025-01-15_Factura_ClienteA.pdf",
                "dropbox_path": "/Documentos/Facturas"
            }
        )

        assert response.status_code == 200
        assert not temp_file.exists(), "Temp file should be deleted after successful upload"
