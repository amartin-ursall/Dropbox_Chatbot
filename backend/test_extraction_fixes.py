"""
Test script to validate NLP extraction fixes
Tests tipo_trabajo and juzgado_num extractors
"""
import sys
sys.path.insert(0, '.')

from app.nlp_extractor_legal import extract_tipo_trabajo, extract_juzgado_numero

def test_tipo_trabajo():
    """Test tipo_trabajo extraction with various inputs"""
    print("=" * 60)
    print("Testing extract_tipo_trabajo()")
    print("=" * 60)

    test_cases = [
        # Casos que deben devolver "procedimiento"
        ("es un documento judicial", "procedimiento"),
        ("judicial", "procedimiento"),
        ("este documento es judicial", "procedimiento"),
        ("procedimiento", "procedimiento"),
        ("es un procedimiento judicial", "procedimiento"),
        ("demanda laboral", "procedimiento"),
        ("sentencia del juzgado", "procedimiento"),
        ("auto judicial", "procedimiento"),
        ("recurso de apelación", "procedimiento"),

        # Casos que deben devolver "proyecto"
        ("proyecto", "proyecto"),
        ("es un proyecto jurídico", "proyecto"),
        ("informe legal", "proyecto"),
        ("dictamen", "proyecto"),
        ("consultoría legal", "proyecto"),
        ("asesoramiento", "proyecto"),
        ("opinión jurídica", "proyecto"),
        ("estudio legal", "proyecto"),

        # Casos ambiguos (deben devolver None)
        ("documento", None),
        ("archivo", None),
        ("", None),
    ]

    passed = 0
    failed = 0

    for input_text, expected in test_cases:
        result = extract_tipo_trabajo(input_text)
        status = "[PASS]" if result == expected else "[FAIL]"

        if result == expected:
            passed += 1
        else:
            failed += 1

        print(f"{status} | Input: '{input_text:40}' | Expected: {str(expected):15} | Got: {result}")

    print(f"\nResultados: {passed} passed, {failed} failed")
    print("=" * 60)
    return failed == 0


def test_juzgado_num():
    """Test juzgado_num extraction with various inputs"""
    print("\n" + "=" * 60)
    print("Testing extract_juzgado_numero()")
    print("=" * 60)

    test_cases = [
        # Casos simples (números solos) - NUEVO
        ("2", "2"),
        ("3", "3"),
        (" 5 ", "5"),
        ("15", "15"),

        # Casos con texto
        ("Juzgado número 2", "2"),
        ("juzgado nº 3", "3"),
        ("Número 5", "5"),
        ("es el juzgado numero 7", "7"),
        ("Juzgado Social 4", "4"),
        ("CA1", "1"),
        ("SC2", "2"),
        ("Jdo. 8", "8"),

        # Casos que no deberían funcionar
        ("sin número", None),
        ("", None),
    ]

    passed = 0
    failed = 0

    for input_text, expected in test_cases:
        result = extract_juzgado_numero(input_text)
        status = "[PASS]" if result == expected else "[FAIL]"

        if result == expected:
            passed += 1
        else:
            failed += 1

        print(f"{status} | Input: '{input_text:30}' | Expected: {expected} | Got: {result}")

    print(f"\nResultados: {passed} passed, {failed} failed")
    print("=" * 60)
    return failed == 0


if __name__ == "__main__":
    print("\n[TEST] EJECUTANDO PRUEBAS DE EXTRACCION NLP\n")

    tipo_ok = test_tipo_trabajo()
    juzgado_ok = test_juzgado_num()

    print("\n" + "=" * 60)
    if tipo_ok and juzgado_ok:
        print("[OK] TODAS LAS PRUEBAS PASARON")
        print("=" * 60)
        sys.exit(0)
    else:
        print("[ERROR] ALGUNAS PRUEBAS FALLARON")
        print("=" * 60)
        sys.exit(1)
