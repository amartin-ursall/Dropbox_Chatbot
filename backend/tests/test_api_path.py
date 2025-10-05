"""
Tests for path suggestion API endpoints - AD-4
"""
import pytest
from httpx import AsyncClient


class TestSuggestPathEndpoint:
    """Tests for POST /api/suggest-path endpoint"""

    @pytest.mark.asyncio
    async def test_suggest_path_for_factura(self, client: AsyncClient):
        """Test 9: Endpoint returns correct path for Factura"""
        response = await client.post(
            "/api/suggest-path",
            json={
                "doc_type": "Factura",
                "client": "Acme Corp",
                "date": "2025-01-15"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["suggested_path"] == "/Documentos/Facturas"
        assert "suggested_name" in data
        assert "full_path" in data

    @pytest.mark.asyncio
    async def test_suggest_path_full_path_format(self, client: AsyncClient):
        """Test: Full path has correct format"""
        response = await client.post(
            "/api/suggest-path",
            json={
                "doc_type": "Contrato",
                "client": "Test Client",
                "date": "2025-01-20"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["full_path"].startswith(data["suggested_path"])
        assert data["suggested_name"] in data["full_path"]


class TestGenerateNameWithPath:
    """Tests for modified POST /api/questions/generate-name endpoint"""

    @pytest.mark.asyncio
    async def test_generate_name_includes_suggested_path(self, client: AsyncClient):
        """Test 10: Generate-name endpoint includes suggested_path"""
        response = await client.post(
            "/api/questions/generate-name",
            json={
                "file_id": "test-file-123",
                "answers": {
                    "doc_type": "Factura",
                    "client": "Acme Corp",
                    "date": "2025-01-15"
                },
                "original_extension": ".pdf"
            }
        )
        assert response.status_code == 200
        data = response.json()

        # Original fields (AD-2)
        assert "suggested_name" in data
        assert "original_extension" in data

        # New fields (AD-4)
        assert "suggested_path" in data
        assert "full_path" in data
        assert data["suggested_path"] == "/Documentos/Facturas"

    @pytest.mark.asyncio
    async def test_generate_name_full_path_combines_correctly(self, client: AsyncClient):
        """Test: Full path combines path + name correctly"""
        response = await client.post(
            "/api/questions/generate-name",
            json={
                "file_id": "test-file-456",
                "answers": {
                    "doc_type": "Recibo",
                    "client": "Cliente Test",
                    "date": "2025-02-01"
                },
                "original_extension": ".xlsx"
            }
        )
        assert response.status_code == 200
        data = response.json()

        expected_name = "2025-02-01_Recibo_Cliente_Test.xlsx"
        expected_path = "/Documentos/Recibos"
        expected_full = f"{expected_path}/{expected_name}"

        assert data["suggested_name"] == expected_name
        assert data["suggested_path"] == expected_path
        assert data["full_path"] == expected_full
