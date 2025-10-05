"""
Test suite for AD-3: Validación Avanzada de Respuestas
TDD RED phase - These tests MUST fail initially

Tests advanced validation logic:
- Date semantic validation (no future, old date warning)
- Document type character restrictions
- Client name character restrictions
- Suggestion generation for common mistakes
"""
import pytest
from datetime import date, timedelta
from app.validators import (
    validate_date_advanced,
    validate_doc_type_advanced,
    validate_client_advanced,
    generate_date_suggestion,
    generate_doc_type_suggestion,
    FileValidationError
)


class TestAdvancedDateValidation:
    """Tests for advanced date validation"""

    def test_reject_future_date(self):
        """
        Test #1: Backend rechaza fecha futura

        Given: Usuario ingresa una fecha en el futuro
        When: Se valida la fecha
        Then: Lanza error indicando que no puede ser futura
        """
        # Arrange
        tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')

        # Act & Assert
        with pytest.raises(FileValidationError) as exc_info:
            validate_date_advanced(tomorrow)

        assert "futuro" in exc_info.value.message.lower()
        assert exc_info.value.status_code == 400

    def test_reject_far_future_date(self):
        """Future date rejection for dates years ahead"""
        future_date = "2030-01-01"

        with pytest.raises(FileValidationError) as exc_info:
            validate_date_advanced(future_date)

        assert "futuro" in exc_info.value.message.lower()

    def test_warn_old_date_but_allow(self):
        """
        Test #2: Backend advierte fecha > 10 años pero permite

        Given: Usuario ingresa fecha de hace más de 10 años
        When: Se valida la fecha
        Then: Retorna la fecha con una advertencia (warning)
        """
        # Arrange
        old_date = (date.today() - timedelta(days=3650 + 1)).strftime('%Y-%m-%d')  # >10 years

        # Act
        result, warning = validate_date_advanced(old_date)

        # Assert
        assert result == old_date
        assert warning is not None
        assert ("antigua" in warning.lower() or
                "vieja" in warning.lower() or
                "hace más de" in warning.lower() or
                "años" in warning.lower())

    def test_accept_date_within_10_years(self):
        """Accept dates within last 10 years without warning"""
        # Arrange
        recent_date = (date.today() - timedelta(days=365)).strftime('%Y-%m-%d')  # 1 year ago

        # Act
        result, warning = validate_date_advanced(recent_date)

        # Assert
        assert result == recent_date
        assert warning is None

    def test_accept_today(self):
        """Accept today's date"""
        # Arrange
        today = date.today().strftime('%Y-%m-%d')

        # Act
        result, warning = validate_date_advanced(today)

        # Assert
        assert result == today
        assert warning is None


class TestDocTypeValidation:
    """Tests for document type validation"""

    def test_reject_doc_type_with_numbers(self):
        """
        Test #3: Backend rechaza tipo con números

        Given: Usuario ingresa tipo con números
        When: Se valida el tipo
        Then: Lanza error
        """
        # Arrange
        invalid_types = ["Factura123", "Doc2025", "Tipo1"]

        # Act & Assert
        for invalid_type in invalid_types:
            with pytest.raises(FileValidationError) as exc_info:
                validate_doc_type_advanced(invalid_type)

            assert "solo letras" in exc_info.value.message.lower()
            assert exc_info.value.status_code == 400

    def test_reject_doc_type_with_symbols(self):
        """
        Test #4: Backend rechaza tipo con símbolos especiales

        Given: Usuario ingresa tipo con símbolos
        When: Se valida el tipo
        Then: Lanza error
        """
        # Arrange
        invalid_types = ["Factura@2025", "Doc#1", "Tipo$", "Test%", "Doc&Co"]

        # Act & Assert
        for invalid_type in invalid_types:
            with pytest.raises(FileValidationError) as exc_info:
                validate_doc_type_advanced(invalid_type)

            assert "solo letras" in exc_info.value.message.lower()

    def test_reject_doc_type_too_long(self):
        """
        Test #5: Backend rechaza tipo > 50 caracteres

        Given: Tipo de documento con más de 50 chars
        When: Se valida
        Then: Lanza error
        """
        # Arrange
        long_type = "A" * 51

        # Act & Assert
        with pytest.raises(FileValidationError) as exc_info:
            validate_doc_type_advanced(long_type)

        assert "50" in exc_info.value.message or "máximo" in exc_info.value.message.lower()

    def test_accept_doc_type_with_accents(self):
        """
        Test #6: Backend permite tipo con acentos

        Given: Tipo con acentos (Nómina, Título)
        When: Se valida
        Then: Acepta y retorna el valor
        """
        # Arrange
        valid_types = ["Nómina", "Título de Propiedad", "Contraseña", "José"]

        # Act & Assert
        for valid_type in valid_types:
            result = validate_doc_type_advanced(valid_type)
            assert result == valid_type.strip()

    def test_accept_doc_type_with_spaces(self):
        """Accept document types with spaces"""
        # Arrange
        valid_types = ["Factura Electrónica", "Contrato de Servicios", "Nota de Crédito"]

        # Act
        for valid_type in valid_types:
            result = validate_doc_type_advanced(valid_type)
            assert result == valid_type.strip()

    def test_accept_doc_type_min_2_chars(self):
        """Accept valid doc type with minimum 2 chars"""
        result = validate_doc_type_advanced("CV")
        assert result == "CV"


class TestClientValidation:
    """Tests for client name validation"""

    def test_reject_client_with_prohibited_symbols(self):
        """
        Test #7: Backend rechaza cliente con símbolos prohibidos

        Given: Cliente con @, #, $, %, &, *, etc.
        When: Se valida
        Then: Lanza error
        """
        # Arrange
        invalid_clients = [
            "Cliente@Email.com",
            "Test#123",
            "Company$Corp",
            "Name%Test",
            "Client&Associates",
            "Test*Star"
        ]

        # Act & Assert
        for invalid_client in invalid_clients:
            with pytest.raises(FileValidationError) as exc_info:
                validate_client_advanced(invalid_client)

            assert "letras" in exc_info.value.message.lower() or "números" in exc_info.value.message.lower()

    def test_accept_client_with_allowed_chars(self):
        """
        Test #8: Backend permite cliente con guiones y puntos

        Given: Cliente con guiones, puntos, números
        When: Se valida
        Then: Acepta
        """
        # Arrange
        valid_clients = [
            "Acme Corp.",
            "Cliente-123",
            "José Pérez",
            "Company S.A.",
            "Test-Client.Co"
        ]

        # Act & Assert
        for valid_client in valid_clients:
            result = validate_client_advanced(valid_client)
            assert result == valid_client.strip()

    def test_reject_client_too_long(self):
        """
        Test #9: Backend rechaza cliente > 100 caracteres

        Given: Cliente con más de 100 chars
        When: Se valida
        Then: Lanza error
        """
        # Arrange
        long_client = "A" * 101

        # Act & Assert
        with pytest.raises(FileValidationError) as exc_info:
            validate_client_advanced(long_client)

        assert "100" in exc_info.value.message or "máximo" in exc_info.value.message.lower()

    def test_accept_client_with_accents(self):
        """Accept client names with accents"""
        valid_clients = ["José García", "Ñoño López", "Françoise Müller"]

        for valid_client in valid_clients:
            result = validate_client_advanced(valid_client)
            assert result == valid_client.strip()


class TestSuggestionGeneration:
    """Tests for suggestion generation"""

    def test_generate_suggestion_for_doc_type_with_numbers(self):
        """
        Test #10: Backend genera sugerencia para tipo con números eliminados

        Given: Tipo con números "Factura123"
        When: Se genera sugerencia
        Then: Retorna "Factura" (números eliminados)
        """
        # Arrange
        invalid_input = "Factura123"

        # Act
        suggestion = generate_doc_type_suggestion(invalid_input)

        # Assert
        assert suggestion == "Factura"
        assert suggestion.isalpha() or " " in suggestion

    def test_generate_suggestion_for_doc_type_with_symbols(self):
        """Generate cleaned suggestion removing symbols"""
        # Arrange
        invalid_input = "Doc@2025#Test"

        # Act
        suggestion = generate_doc_type_suggestion(invalid_input)

        # Assert
        assert suggestion == "DocTest"
        assert "@" not in suggestion
        assert "#" not in suggestion

    def test_generate_suggestion_for_date_dd_mm_yyyy(self):
        """
        Test #11: Backend genera sugerencia para fecha mal formateada

        Given: Fecha en formato DD-MM-YYYY "15-01-2025"
        When: Se genera sugerencia
        Then: Retorna "2025-01-15"
        """
        # Arrange
        invalid_dates = [
            ("15-01-2025", "2025-01-15"),
            ("01-12-2024", "2024-12-01"),
            ("31-03-2023", "2023-03-31")
        ]

        # Act & Assert
        for invalid, expected in invalid_dates:
            suggestion = generate_date_suggestion(invalid)
            assert suggestion == expected

    def test_generate_suggestion_for_date_mm_dd_yyyy(self):
        """Generate suggestion from MM/DD/YYYY format"""
        # Arrange
        invalid_dates = [
            ("01/15/2025", "2025-01-15"),
            ("12/01/2024", "2024-12-01")
        ]

        # Act & Assert
        for invalid, expected in invalid_dates:
            suggestion = generate_date_suggestion(invalid)
            assert suggestion == expected

    def test_generate_suggestion_returns_none_for_unparseable(self):
        """Return None if date cannot be parsed"""
        # Arrange
        invalid_input = "not-a-date-at-all"

        # Act
        suggestion = generate_date_suggestion(invalid_input)

        # Assert
        assert suggestion is None
