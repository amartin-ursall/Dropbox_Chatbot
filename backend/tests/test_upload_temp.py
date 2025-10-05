"""
Tests for temporary file upload endpoint (AD-1)
Red phase - These tests should FAIL initially
"""
import pytest
from httpx import AsyncClient, ASGITransport
from pathlib import Path
import os


@pytest.mark.asyncio
async def test_upload_temp_accepts_valid_file(test_client: AsyncClient):
    """
    Test 1: POST /upload-temp acepta archivo válido
    Gherkin: When el usuario selecciona un archivo y lo envía
    """
    # Arrange
    file_content = b"Test file content for upload"
    files = {
        "file": ("test_document.pdf", file_content, "application/pdf")
    }

    # Act
    response = await test_client.post("/api/upload-temp", files=files)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "file_id" in data
    assert data["original_name"] == "test_document.pdf"
    assert data["size"] > 0


@pytest.mark.asyncio
async def test_upload_temp_saves_to_tmp_with_uuid(test_client: AsyncClient, tmp_path):
    """
    Test 2: Archivo se guarda en /tmp con UUID único
    Gherkin: Then el sistema guarda el archivo en almacenamiento temporal
    """
    # Arrange
    file_content = b"Content to be saved"
    files = {"file": ("invoice.pdf", file_content, "application/pdf")}

    # Act
    response = await test_client.post("/api/upload-temp", files=files)

    # Assert
    assert response.status_code == 200
    data = response.json()
    file_id = data["file_id"]

    # Verify file exists in temp storage
    temp_file_path = Path("/tmp") / f"{file_id}_invoice.pdf"
    assert temp_file_path.exists()
    assert temp_file_path.read_bytes() == file_content


@pytest.mark.asyncio
async def test_upload_temp_response_structure(test_client: AsyncClient):
    """
    Test 3: Respuesta incluye file_id, original_name, size
    Gherkin: And el chatbot confirma la recepción del archivo
    """
    # Arrange
    file_content = b"x" * 1024  # 1KB file
    files = {"file": ("contract.docx", file_content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}

    # Act
    response = await test_client.post("/api/upload-temp", files=files)

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Validate response schema
    assert isinstance(data["file_id"], str)
    assert len(data["file_id"]) == 36  # UUID format
    assert data["original_name"] == "contract.docx"
    assert data["size"] == 1024
    assert "extension" in data
    assert data["extension"] == ".docx"


@pytest.mark.asyncio
async def test_upload_temp_rejects_oversized_file(test_client: AsyncClient):
    """
    Test 4: Rechaza archivo > 50MB
    Edge case: validación de tamaño
    """
    # Arrange - Simulate 51MB file (don't actually create it)
    files = {
        "file": ("huge_file.pdf", b"x" * (51 * 1024 * 1024), "application/pdf")
    }

    # Act
    response = await test_client.post("/api/upload-temp", files=files)

    # Assert
    assert response.status_code == 413  # Payload Too Large
    data = response.json()
    assert "error" in data
    assert "50MB" in data["error"] or "size" in data["error"].lower()


@pytest.mark.asyncio
async def test_upload_temp_rejects_forbidden_extension(test_client: AsyncClient):
    """
    Test 5: Rechaza extensión no permitida (.exe, .sh)
    Edge case: seguridad - whitelist de extensiones
    """
    # Arrange
    forbidden_files = [
        ("malware.exe", b"malicious", "application/x-msdownload"),
        ("script.sh", b"#!/bin/bash", "application/x-sh"),
        ("app.bat", b"@echo off", "application/x-bat"),
    ]

    for filename, content, mimetype in forbidden_files:
        files = {"file": (filename, content, mimetype)}

        # Act
        response = await test_client.post("/api/upload-temp", files=files)

        # Assert
        assert response.status_code == 400, f"Should reject {filename}"
        data = response.json()
        assert "extension" in data["error"].lower() or "not allowed" in data["error"].lower()
