"""
Test script for natural language interpretation in URSALL
Tests that the system accepts natural language responses
"""
import asyncio
import sys
from app.gemini_rest_extractor import extract_with_gemini_rest, GEMINI_AVAILABLE
from app.nlp_extractor_legal import extract_information_legal


async def test_tipo_trabajo_extraction():
    """Test tipo_trabajo extraction with various natural language inputs"""

    print("=" * 70)
    print("Testing Natural Language Interpretation for 'tipo_trabajo'")
    print("=" * 70)
    print()

    test_cases = [
        # Direct responses
        ("procedimiento", "Direct: procedimiento"),
        ("proyecto", "Direct: proyecto"),

        # Natural language - procedimiento
        ("Es un procedimiento judicial", "NL: judicial procedure"),
        ("es un juicio", "NL: juicio"),
        ("una demanda", "NL: demanda"),
        ("recurso de apelación", "NL: recurso"),

        # Natural language - proyecto
        ("Es un proyecto de asesoría", "NL: proyecto de asesoría"),
        ("proyecto jurídico", "NL: proyecto jurídico"),
        ("informe legal", "NL: informe legal"),
        ("consultoría", "NL: consultoría"),

        # Ambiguous
        ("no sé", "Ambiguous: no sé"),
        ("quizás", "Ambiguous: quizás"),
    ]

    print("[INFO] Testing with Gemini AI extraction...")
    print()

    if not GEMINI_AVAILABLE:
        print("[WARNING] Gemini API not available. Set GEMINI_API_KEY in .env")
        print("[INFO] Testing with fuzzy matching only...")
        print()

    for user_input, description in test_cases:
        print(f"Test: {description}")
        print(f"  Input: '{user_input}'")

        # Try Gemini first
        gemini_result = None
        if GEMINI_AVAILABLE:
            try:
                gemini_result = await extract_with_gemini_rest("tipo_trabajo", user_input)
                print(f"  Gemini: {gemini_result}")
            except Exception as e:
                print(f"  Gemini: [ERROR] {e}")

        # Fallback to fuzzy matching (same logic as main.py)
        answer_lower = user_input.lower().strip()
        fuzzy_result = None

        if answer_lower in ["procedimiento", "proyecto"]:
            fuzzy_result = answer_lower
        elif any(word in answer_lower for word in ["procedimiento", "judicial", "juicio", "demanda", "recurso", "juzgado"]):
            fuzzy_result = "procedimiento"
        elif any(word in answer_lower for word in ["proyecto", "asesor", "consultoria", "consultoría", "opinion", "opinión", "informe"]):
            fuzzy_result = "proyecto"
        else:
            fuzzy_result = "AMBIGUO"

        print(f"  Fuzzy: {fuzzy_result}")

        # Final result (Gemini preferred)
        final_result = gemini_result if (gemini_result and gemini_result.upper() != "AMBIGUO") else fuzzy_result
        print(f"  Final: {final_result}")

        # Expected result
        if "procedimiento" in user_input.lower() or any(w in user_input.lower() for w in ["judicial", "juicio", "demanda", "recurso"]):
            expected = "procedimiento"
        elif "proyecto" in user_input.lower() or any(w in user_input.lower() for w in ["asesor", "informe", "consultor"]):
            expected = "proyecto"
        else:
            expected = user_input.lower() if user_input.lower() in ["procedimiento", "proyecto"] else "AMBIGUO"

        status = "[OK]" if final_result == expected else "[WARNING]"
        print(f"  Status: {status} (expected: {expected})")
        print()


async def test_doc_type_extraction():
    """Test document type extraction"""

    print("=" * 70)
    print("Testing Document Type Extraction")
    print("=" * 70)
    print()

    test_cases = [
        ("Es una demanda", "doc_type_proc", "Demanda"),
        ("Recurso de apelación", "doc_type_proc", "Recurso de apelación"),
        ("Un informe jurídico", "doc_type_proyecto", "Informe jurídico"),
        ("Contrato", "doc_type_proyecto", "Contrato"),
    ]

    if not GEMINI_AVAILABLE:
        print("[WARNING] Gemini API not available. Skipping doc_type tests.")
        return

    for user_input, question_id, expected in test_cases:
        print(f"Test: {question_id}")
        print(f"  Input: '{user_input}'")

        try:
            result = await extract_with_gemini_rest(question_id, user_input)
            print(f"  Result: {result}")
            status = "[OK]" if result and expected.lower() in result.lower() else "[WARNING]"
            print(f"  Status: {status} (expected: {expected})")
        except Exception as e:
            print(f"  [ERROR] {e}")

        print()


async def main():
    """Run all tests"""

    print()
    print("=" * 70)
    print("URSALL Natural Language Interpretation Test")
    print("=" * 70)
    print()

    if GEMINI_AVAILABLE:
        print("[INFO] Gemini API is configured")
    else:
        print("[WARNING] Gemini API is NOT configured")
        print("[INFO] Set GEMINI_API_KEY in backend/.env to enable AI extraction")

    print()

    await test_tipo_trabajo_extraction()
    await test_doc_type_extraction()

    print("=" * 70)
    print("Test Complete")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
