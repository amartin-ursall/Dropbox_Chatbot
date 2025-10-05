"""
Test suite for AD-2: Guía por preguntas
TDD RED phase - These tests MUST fail initially

Tests the question flow endpoints:
- POST /api/questions/start - Get first question
- POST /api/questions/answer - Submit answer and get next question
- POST /api/questions/generate-name - Generate final filename
"""
import pytest
from httpx import AsyncClient
from datetime import date


class TestQuestionFlow:
    """Tests for sequential question asking"""

    @pytest.mark.asyncio
    async def test_start_questions_returns_first_question(self, client: AsyncClient):
        """
        Test #1: Backend responde con primera pregunta (tipo doc) cuando hay file_id válido

        Given: Un file_id válido de un archivo subido
        When: POST /api/questions/start con {"file_id": "valid-uuid"}
        Then: Responde con primera pregunta sobre tipo de documento
        """
        # Arrange
        file_id = "123e4567-e89b-12d3-a456-426614174000"

        # Act
        response = await client.post(
            "/api/questions/start",
            json={"file_id": file_id}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["question_id"] == "doc_type"
        assert "tipo de documento" in data["question_text"].lower()
        assert data["required"] is True
        assert data["validation"] == {"min_length": 2}

    @pytest.mark.asyncio
    async def test_answer_doc_type_validates_not_empty(self, client: AsyncClient):
        """
        Test #2: Backend valida respuesta de tipo de documento (no vacía, min 2 chars)

        Given: Primera pregunta activa
        When: POST /api/questions/answer con respuesta vacía o < 2 chars
        Then: Responde con error 400 y mensaje de validación
        """
        # Arrange
        file_id = "123e4567-e89b-12d3-a456-426614174000"

        # Act - Empty answer
        response_empty = await client.post(
            "/api/questions/answer",
            json={
                "file_id": file_id,
                "question_id": "doc_type",
                "answer": ""
            }
        )

        # Act - Single char
        response_short = await client.post(
            "/api/questions/answer",
            json={
                "file_id": file_id,
                "question_id": "doc_type",
                "answer": "F"
            }
        )

        # Assert
        assert response_empty.status_code == 400
        assert "mínimo 2 caracteres" in response_empty.json()["detail"].lower()

        assert response_short.status_code == 400
        assert "mínimo 2 caracteres" in response_short.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_answer_doc_type_returns_client_question(self, client: AsyncClient):
        """
        Test #3: Backend responde con segunda pregunta (cliente) tras responder tipo doc

        Given: Respuesta válida a pregunta de tipo de documento
        When: POST /api/questions/answer con answer="Factura"
        Then: Responde con segunda pregunta sobre cliente
        """
        # Arrange
        file_id = "123e4567-e89b-12d3-a456-426614174000"

        # Act
        response = await client.post(
            "/api/questions/answer",
            json={
                "file_id": file_id,
                "question_id": "doc_type",
                "answer": "Factura"
            }
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["next_question"]["question_id"] == "client"
        assert "cliente" in data["next_question"]["question_text"].lower()
        assert data["completed"] is False

    @pytest.mark.asyncio
    async def test_answer_client_validates_min_length(self, client: AsyncClient):
        """
        Test #4: Backend valida respuesta de cliente (no vacía, min 2 chars)

        Given: Segunda pregunta activa (cliente)
        When: POST /api/questions/answer con respuesta < 2 chars
        Then: Responde con error 400
        """
        # Arrange
        file_id = "123e4567-e89b-12d3-a456-426614174000"

        # Act
        response = await client.post(
            "/api/questions/answer",
            json={
                "file_id": file_id,
                "question_id": "client",
                "answer": "X"
            }
        )

        # Assert
        assert response.status_code == 400
        assert "mínimo 2 caracteres" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_answer_client_returns_date_question(self, client: AsyncClient):
        """
        Test #5: Backend responde con tercera pregunta (fecha) tras responder cliente

        Given: Respuesta válida a pregunta de cliente
        When: POST /api/questions/answer con answer="Acme Corp"
        Then: Responde con tercera pregunta sobre fecha
        """
        # Arrange
        file_id = "123e4567-e89b-12d3-a456-426614174000"

        # Act
        response = await client.post(
            "/api/questions/answer",
            json={
                "file_id": file_id,
                "question_id": "client",
                "answer": "Acme Corp"
            }
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["next_question"]["question_id"] == "date"
        assert "fecha" in data["next_question"]["question_text"].lower()
        assert data["next_question"]["validation"]["format"] == "YYYY-MM-DD"

    @pytest.mark.asyncio
    async def test_answer_date_validates_format_yyyy_mm_dd(self, client: AsyncClient):
        """
        Test #6: Backend valida formato de fecha YYYY-MM-DD

        Given: Tercera pregunta activa (fecha)
        When: POST /api/questions/answer con fecha en formato válido
        Then: Responde 200 y marca como completed
        """
        # Arrange
        file_id = "123e4567-e89b-12d3-a456-426614174000"
        valid_date = "2025-01-15"

        # Act
        response = await client.post(
            "/api/questions/answer",
            json={
                "file_id": file_id,
                "question_id": "date",
                "answer": valid_date
            }
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is True
        assert data["next_question"] is None

    @pytest.mark.asyncio
    async def test_answer_date_rejects_invalid_formats(self, client: AsyncClient):
        """
        Test #7: Backend rechaza fechas inválidas (formatos incorrectos)

        Given: Tercera pregunta activa (fecha)
        When: POST /api/questions/answer con formatos inválidos
        Then: Responde 400 con mensaje de error
        """
        # Arrange
        file_id = "123e4567-e89b-12d3-a456-426614174000"
        invalid_dates = [
            "15-01-2025",  # DD-MM-YYYY
            "01/15/2025",  # MM/DD/YYYY
            "2025/01/15",  # Wrong separator
            "15 Jan 2025", # Text format
            "2025-1-5",    # Missing zeros
            "not-a-date",  # Invalid
        ]

        # Act & Assert
        for invalid_date in invalid_dates:
            response = await client.post(
                "/api/questions/answer",
                json={
                    "file_id": file_id,
                    "question_id": "date",
                    "answer": invalid_date
                }
            )
            assert response.status_code == 400, f"Failed for date: {invalid_date}"
            assert "YYYY-MM-DD" in response.json()["detail"]


class TestFileNaming:
    """Tests for filename generation"""

    @pytest.mark.asyncio
    async def test_generate_name_with_correct_format(self, client: AsyncClient):
        """
        Test #8: Backend genera nombre con formato {fecha}_{tipo}_{cliente}.{ext}

        Given: Todas las preguntas respondidas
        When: POST /api/questions/generate-name
        Then: Responde con nombre en formato correcto
        """
        # Arrange
        file_id = "123e4567-e89b-12d3-a456-426614174000"
        answers = {
            "doc_type": "Factura",
            "client": "Acme Corp",
            "date": "2025-01-15"
        }
        original_extension = ".pdf"

        # Act
        response = await client.post(
            "/api/questions/generate-name",
            json={
                "file_id": file_id,
                "answers": answers,
                "original_extension": original_extension
            }
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        expected_name = "2025-01-15_Factura_Acme_Corp.pdf"
        assert data["suggested_name"] == expected_name
        assert data["original_extension"] == original_extension

    @pytest.mark.asyncio
    async def test_generate_name_sanitizes_special_chars(self, client: AsyncClient):
        """
        Test #9: Backend sanitiza nombre: espacios → _, elimina caracteres especiales

        Given: Respuestas con espacios y caracteres especiales
        When: POST /api/questions/generate-name
        Then: Nombre sanitizado correctamente
        """
        # Arrange
        file_id = "123e4567-e89b-12d3-a456-426614174000"

        test_cases = [
            {
                "answers": {
                    "doc_type": "Factura Electrónica",
                    "client": "Cliente & Asociados S.A.",
                    "date": "2025-01-15"
                },
                "original_extension": ".pdf",
                "expected": "2025-01-15_Factura_Electronica_Cliente_Asociados_SA.pdf"
            },
            {
                "answers": {
                    "doc_type": "Presupuesto",
                    "client": "Test@Company (Spain)",
                    "date": "2024-12-01"
                },
                "original_extension": ".xlsx",
                "expected": "2024-12-01_Presupuesto_TestCompany_Spain.xlsx"
            }
        ]

        # Act & Assert
        for test_case in test_cases:
            response = await client.post(
                "/api/questions/generate-name",
                json={
                    "file_id": file_id,
                    "answers": test_case["answers"],
                    "original_extension": test_case["original_extension"]
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["suggested_name"] == test_case["expected"]
