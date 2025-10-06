"""
Tests for NLP extraction functionality
"""
import pytest
from app.nlp_extractor import (
    extract_client_name,
    extract_doc_type,
    extract_date,
    extract_information,
    normalize_date_format
)


class TestClientExtraction:
    """Test client name extraction"""

    def test_simple_name(self):
        assert extract_client_name("Juan") == "Juan"
        assert extract_client_name("Acme Corp") == "Acme Corp"

    def test_with_prefix(self):
        assert extract_client_name("El cliente es Juan") == "Juan"
        assert extract_client_name("El nombre del cliente es Acme Corp") == "Acme Corp"
        assert extract_client_name("se llama Microsoft España S.L.") == "Microsoft España S.L."
        assert extract_client_name("cliente: Google Inc.") == "Google Inc."

    def test_complex_names(self):
        assert extract_client_name("El cliente es Juan Pérez García") == "Juan Pérez García"
        assert extract_client_name("Microsoft España S.L.") == "Microsoft España S.L."
        assert extract_client_name("El nombre es Tech & Solutions Inc.") == "Tech & Solutions Inc."

    def test_with_accents(self):
        assert extract_client_name("El cliente es José María López") == "José María López"
        assert extract_client_name("Comunicación y Diseño S.A.") == "Comunicación y Diseño S.A."


class TestDocTypeExtraction:
    """Test document type extraction"""

    def test_simple_type(self):
        assert extract_doc_type("Factura").lower() == "factura"
        assert extract_doc_type("Contrato").lower() == "contrato"

    def test_with_article(self):
        assert extract_doc_type("una factura").lower() == "factura"
        assert extract_doc_type("un contrato").lower() == "contrato"
        assert extract_doc_type("unos presupuestos").lower() == "presupuestos"

    def test_with_prefix(self):
        assert extract_doc_type("Es una factura").lower() == "factura"
        assert extract_doc_type("El tipo de documento es un contrato").lower() == "contrato"
        assert extract_doc_type("son presupuestos").lower() == "presupuestos"

    def test_known_types(self):
        assert extract_doc_type("Es una nómina").lower() == "nómina"
        assert extract_doc_type("El documento es un recibo").lower() == "recibo"
        assert extract_doc_type("tipo: albarán").lower() == "albarán"

    def test_unknown_types(self):
        # Should still extract the word even if not in known list
        result = extract_doc_type("Es un certificado")
        assert result.lower() == "certificado"


class TestDateExtraction:
    """Test date extraction"""

    def test_simple_date_correct_format(self):
        assert extract_date("2025-01-15") == "2025-01-15"
        assert extract_date("2024-12-31") == "2024-12-31"

    def test_with_prefix(self):
        assert extract_date("La fecha es 2025-01-15") == "2025-01-15"
        assert extract_date("Es del día 2025-01-15") == "2025-01-15"

    def test_different_formats(self):
        assert extract_date("15/01/2025") == "2025-01-15"
        assert extract_date("15-01-2025") == "2025-01-15"
        assert extract_date("La fecha es 31/12/2024") == "2024-12-31"

    def test_normalize_formats(self):
        assert normalize_date_format("2025-01-15") == "2025-01-15"
        assert normalize_date_format("15/01/2025") == "2025-01-15"
        assert normalize_date_format("15-01-2025") == "2025-01-15"


class TestMainExtractor:
    """Test main extraction function"""

    def test_client_extraction(self):
        assert extract_information("client", "El cliente es Acme Corp") == "Acme Corp"
        assert extract_information("client", "Juan Pérez") == "Juan Pérez"

    def test_doc_type_extraction(self):
        result = extract_information("doc_type", "Es una factura")
        assert result.lower() == "factura"
        result = extract_information("doc_type", "Contrato")
        assert result.lower() == "contrato"

    def test_date_extraction(self):
        assert extract_information("date", "2025-01-15") == "2025-01-15"
        assert extract_information("date", "15/01/2025") == "2025-01-15"
        assert extract_information("date", "La fecha es 2024-12-31") == "2024-12-31"

    def test_unknown_question_type(self):
        # Should just return trimmed input
        assert extract_information("unknown", "  some text  ") == "some text"


class TestEdgeCases:
    """Test edge cases and special scenarios"""

    def test_empty_input(self):
        assert extract_client_name("") == ""
        assert extract_doc_type("") == ""
        assert extract_date("") == ""

    def test_only_whitespace(self):
        assert extract_client_name("   ") == ""
        assert extract_doc_type("   ") == ""

    def test_mixed_case(self):
        assert extract_client_name("EL CLIENTE ES ACME CORP") == "ACME CORP"
        result = extract_doc_type("ES UNA FACTURA")
        assert result.lower() == "factura"

    def test_extra_spaces(self):
        assert extract_client_name("El   cliente   es   Acme Corp") == "Acme Corp"
        assert extract_date("La  fecha  es  2025-01-15") == "2025-01-15"
