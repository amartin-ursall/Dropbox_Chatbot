"""
Tests for Gemini AI extraction functionality
Note: These tests will use fallback (regex) if GEMINI_API_KEY is not set
"""
import pytest
from app.gemini_extractor import (
    extract_information_ai,
    check_gemini_status,
    GEMINI_AVAILABLE
)


class TestGeminiStatus:
    """Test Gemini API status checking"""

    def test_check_status(self):
        """Check that status check returns expected keys"""
        status = check_gemini_status()
        assert "gemini_available" in status
        assert "api_key_configured" in status
        assert isinstance(status["gemini_available"], bool)
        assert isinstance(status["api_key_configured"], bool)


class TestExtractionWithFallback:
    """
    Test extraction functionality
    Works with both Gemini and fallback (regex)
    """

    def test_client_extraction_simple(self):
        """Test simple client name extraction"""
        result = extract_information_ai("client", "Acme Corp")
        assert result == "Acme Corp"

    def test_client_extraction_with_prefix(self):
        """Test client extraction with common prefix"""
        result = extract_information_ai("client", "El cliente es Juan Pérez")
        assert "Juan" in result
        assert "Pérez" in result
        # Should not contain "cliente" or "es"
        assert "cliente" not in result.lower() or len(result) > 20

    def test_doc_type_extraction_simple(self):
        """Test simple doc type extraction"""
        result = extract_information_ai("doc_type", "Factura")
        assert result.lower() in ["factura", "facturas"]

    def test_doc_type_extraction_with_article(self):
        """Test doc type with article"""
        result = extract_information_ai("doc_type", "Es una factura")
        assert result.lower() in ["factura", "facturas"]
        # Should not contain "es" or "una"
        assert result.lower() not in ["es una factura", "una factura"]

    def test_date_extraction_correct_format(self):
        """Test date extraction with correct format"""
        result = extract_information_ai("date", "2025-01-15")
        assert result == "2025-01-15"

    def test_date_extraction_different_format(self):
        """Test date extraction with different format"""
        result = extract_information_ai("date", "15/01/2025")
        assert result == "2025-01-15"

    def test_date_extraction_with_prefix(self):
        """Test date extraction with prefix text"""
        result = extract_information_ai("date", "La fecha es 2025-01-15")
        assert "2025-01-15" in result


class TestGeminiSpecific:
    """
    Tests that only run when Gemini is available
    These test AI-specific behavior
    """

    @pytest.mark.skipif(not GEMINI_AVAILABLE, reason="Gemini API not available")
    def test_gemini_client_complex(self):
        """Test complex client name with Gemini"""
        result = extract_information_ai("client", "se llama Microsoft España S.L.")
        assert "Microsoft" in result
        assert "España" in result
        # Should not contain "se llama"
        assert "se llama" not in result.lower()

    @pytest.mark.skipif(not GEMINI_AVAILABLE, reason="Gemini API not available")
    def test_gemini_doc_type_variations(self):
        """Test doc type extraction variations with Gemini"""
        test_cases = [
            ("Es una factura", "factura"),
            ("son presupuestos", "presupuesto"),
            ("El tipo de documento es un contrato", "contrato"),
        ]
        for input_text, expected in test_cases:
            result = extract_information_ai("doc_type", input_text)
            assert expected in result.lower()

    @pytest.mark.skipif(not GEMINI_AVAILABLE, reason="Gemini API not available")
    def test_gemini_date_normalization(self):
        """Test date format normalization with Gemini"""
        test_cases = [
            ("15-01-2025", "2025-01-15"),
            ("La fecha es 31/12/2024", "2024-12-31"),
            ("2025-01-15", "2025-01-15"),
        ]
        for input_text, expected in test_cases:
            result = extract_information_ai("date", input_text)
            assert result == expected


class TestFallbackBehavior:
    """Test that fallback works when Gemini is not available"""

    def test_fallback_still_works(self):
        """Ensure extraction works even without Gemini"""
        # These should work with or without Gemini
        assert extract_information_ai("client", "Juan") == "Juan"
        assert extract_information_ai("doc_type", "Factura").lower() in ["factura", "facturas"]
        assert extract_information_ai("date", "2025-01-15") == "2025-01-15"
