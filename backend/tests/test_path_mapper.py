"""
Tests for path_mapper module - AD-4
Tests path suggestion logic based on document type
"""
import pytest
from app.path_mapper import suggest_path, get_full_path


class TestPathMapper:
    """Tests for document type to Dropbox path mapping"""

    def test_factura_maps_to_facturas_folder(self):
        """Test 1: Maps 'Factura' to /Documentos/Facturas"""
        result = suggest_path("Factura")
        assert result == "/Documentos/Facturas"

    def test_factura_lowercase_maps_correctly(self):
        """Test 2: Case-insensitive mapping for 'factura'"""
        result = suggest_path("factura")
        assert result == "/Documentos/Facturas"

    def test_contrato_maps_to_contratos_folder(self):
        """Test 3: Maps 'Contrato' to /Documentos/Contratos"""
        result = suggest_path("Contrato")
        assert result == "/Documentos/Contratos"

    def test_recibo_maps_to_recibos_folder(self):
        """Test 4: Maps 'Recibo' to /Documentos/Recibos"""
        result = suggest_path("Recibo")
        assert result == "/Documentos/Recibos"

    def test_nomina_with_accent_maps_correctly(self):
        """Test 5: Maps 'Nómina' to /Documentos/Nóminas"""
        result = suggest_path("Nómina")
        assert result == "/Documentos/Nóminas"

    def test_nomina_without_accent_maps_correctly(self):
        """Test 6: Maps 'Nomina' (no accent) to /Documentos/Nóminas"""
        result = suggest_path("Nomina")
        assert result == "/Documentos/Nóminas"

    def test_unknown_type_maps_to_otros(self):
        """Test 7: Unknown types map to /Documentos/Otros"""
        result = suggest_path("Reporte Mensual")
        assert result == "/Documentos/Otros"

    def test_presupuesto_maps_correctly(self):
        """Test: Maps 'Presupuesto' to /Documentos/Presupuestos"""
        result = suggest_path("Presupuesto")
        assert result == "/Documentos/Presupuestos"

    def test_facturas_plural_maps_correctly(self):
        """Test: Plural 'Facturas' also maps to /Documentos/Facturas"""
        result = suggest_path("Facturas")
        assert result == "/Documentos/Facturas"

    def test_uppercase_factura_maps_correctly(self):
        """Test: UPPERCASE 'FACTURA' maps correctly"""
        result = suggest_path("FACTURA")
        assert result == "/Documentos/Facturas"


class TestFullPath:
    """Tests for full path generation"""

    def test_generate_full_path(self):
        """Test 8: Generates full path correctly"""
        path = suggest_path("Factura")
        filename = "2025-01-15_Factura_Acme-Corp.pdf"
        full_path = get_full_path(path, filename)
        assert full_path == "/Documentos/Facturas/2025-01-15_Factura_Acme-Corp.pdf"

    def test_full_path_with_otros(self):
        """Test: Full path with Otros folder"""
        path = suggest_path("Documento Extraño")
        filename = "2025-01-15_Documento-Extraño_Cliente.pdf"
        full_path = get_full_path(path, filename)
        assert full_path == "/Documentos/Otros/2025-01-15_Documento-Extraño_Cliente.pdf"
