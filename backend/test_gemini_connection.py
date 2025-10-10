"""
Script de prueba para verificar la conexión con Gemini API
y la extracción de información del lenguaje natural
"""
import asyncio
import os
from dotenv import load_dotenv

# Configurar la API key directamente para la prueba
os.environ["GEMINI_API_KEY"] = "AIzaSyCtLooZwyZSaHRfi-y0JI2bd4PsZ-B6qYw"

# Importar el extractor
from app.gemini_rest_extractor import extract_with_gemini_rest, check_gemini_status, GEMINI_AVAILABLE

def print_separator():
    print("=" * 70)

def print_test_header(test_name):
    print_separator()
    print(f"[TEST] {test_name}")
    print_separator()

async def test_gemini_status():
    """Verificar que Gemini API está configurada"""
    print_test_header("Verificación de Configuración de Gemini")

    status = check_gemini_status()
    print(f"✓ Estado de Gemini:")
    for key, value in status.items():
        print(f"  - {key}: {value}")

    if not GEMINI_AVAILABLE:
        print("\n❌ ERROR: GEMINI_API_KEY no está configurada")
        return False

    print("\n✅ Gemini API configurada correctamente")
    return True

async def test_client_extraction():
    """Probar extracción de nombres de clientes"""
    print_test_header("Extracción de Nombres de Clientes")

    test_cases = [
        ("El cliente es GRUPO GORETTI", "GRUPO GORETTI"),
        ("se llama Microsoft España S.L.", "Microsoft España S.L."),
        ("nombre del cliente: Acme Corp", "Acme Corp"),
        ("Tech & Solutions Inc.", "Tech & Solutions Inc."),
        ("Juan Pérez García", "Juan Pérez García"),
        ("Cabildo de La Gomera", "Cabildo de La Gomera"),
        ("no sé", "AMBIGUO"),
    ]

    passed = 0
    failed = 0

    for user_input, expected in test_cases:
        print(f"\n📝 Input: '{user_input}'")
        print(f"   Esperado: '{expected}'")

        result = await extract_with_gemini_rest("client", user_input)

        if result:
            print(f"   ✅ Resultado: '{result}'")

            # Verificación flexible (ignorar mayúsculas/minúsculas)
            if result.upper() == expected.upper() or expected.upper() in result.upper():
                passed += 1
                print("   ✓ CORRECTO")
            else:
                failed += 1
                print(f"   ✗ FALLO - Se esperaba '{expected}'")
        else:
            print(f"   ❌ ERROR: No se obtuvo resultado")
            failed += 1

    print(f"\n{'='*70}")
    print(f"Resultado: {passed} ✅ / {failed} ❌ (Total: {len(test_cases)})")
    return failed == 0

async def test_doc_type_extraction():
    """Probar extracción de tipos de documentos"""
    print_test_header("Extracción de Tipos de Documentos")

    test_cases = [
        ("Es una factura", "factura"),
        ("son contratos", "contrato"),
        ("documento jurídico", "juridico"),
        ("tipo de documento: presupuesto", "presupuesto"),
        ("Es una Escritura", "escritura"),
        ("Pericial", "pericial"),
        ("no estoy seguro", "AMBIGUO"),
    ]

    passed = 0
    failed = 0

    for user_input, expected in test_cases:
        print(f"\n📝 Input: '{user_input}'")
        print(f"   Esperado: '{expected}'")

        result = await extract_with_gemini_rest("doc_type", user_input)

        if result:
            print(f"   ✅ Resultado: '{result}'")

            if result.lower() == expected.lower() or expected.lower() in result.lower():
                passed += 1
                print("   ✓ CORRECTO")
            else:
                failed += 1
                print(f"   ✗ FALLO - Se esperaba '{expected}'")
        else:
            print(f"   ❌ ERROR: No se obtuvo resultado")
            failed += 1

    print(f"\n{'='*70}")
    print(f"Resultado: {passed} ✅ / {failed} ❌ (Total: {len(test_cases)})")
    return failed == 0

async def test_date_extraction():
    """Probar extracción de fechas"""
    print_test_header("Extracción y Normalización de Fechas")

    test_cases = [
        ("La fecha es 15/01/2025", "2025-01-15"),
        ("31-12-2024", "2024-12-31"),
        ("2025-01-15", "2025-01-15"),
        ("15 de enero de 2025", "2025-01-15"),
        ("08/05/2025", "2025-05-08"),
        ("ayer", "AMBIGUO"),
        ("no recuerdo", "AMBIGUO"),
    ]

    passed = 0
    failed = 0

    for user_input, expected in test_cases:
        print(f"\n📝 Input: '{user_input}'")
        print(f"   Esperado: '{expected}'")

        result = await extract_with_gemini_rest("date", user_input)

        if result:
            print(f"   ✅ Resultado: '{result}'")

            if result == expected or expected in result:
                passed += 1
                print("   ✓ CORRECTO")
            else:
                failed += 1
                print(f"   ✗ FALLO - Se esperaba '{expected}'")
        else:
            print(f"   ❌ ERROR: No se obtuvo resultado")
            failed += 1

    print(f"\n{'='*70}")
    print(f"Resultado: {passed} ✅ / {failed} ❌ (Total: {len(test_cases)})")
    return failed == 0

async def test_real_scenario():
    """Simular un escenario real completo"""
    print_test_header("Escenario Real - Flujo Completo de Extracción")

    print("\n📋 Simulando respuestas del usuario en un caso real:")

    scenarios = [
        {
            "pregunta": "¿Cuál es el nombre del cliente?",
            "respuesta": "el cliente es GRUPO GORETTI",
            "question_id": "client",
            "esperado": "GRUPO GORETTI"
        },
        {
            "pregunta": "¿Qué tipo de documento es?",
            "respuesta": "Es una Escritura de demanda",
            "question_id": "doc_type",
            "esperado": "escritura"
        },
        {
            "pregunta": "¿Cuál es la fecha del documento?",
            "respuesta": "la fecha es 08/05/2025",
            "question_id": "date",
            "esperado": "2025-05-08"
        }
    ]

    all_passed = True

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n--- Pregunta {i} ---")
        print(f"❓ {scenario['pregunta']}")
        print(f"💬 Usuario responde: '{scenario['respuesta']}'")

        result = await extract_with_gemini_rest(scenario['question_id'], scenario['respuesta'])

        if result:
            print(f"🤖 Gemini extrae: '{result}'")

            # Verificar si la extracción es correcta
            if scenario['esperado'].lower() in result.lower() or result.lower() == scenario['esperado'].lower():
                print(f"✅ Extracción correcta (esperado: '{scenario['esperado']}')")
            else:
                print(f"⚠️ Extracción diferente (esperado: '{scenario['esperado']}')")
                all_passed = False
        else:
            print(f"❌ ERROR: Gemini no pudo extraer información")
            all_passed = False

    print(f"\n{'='*70}")
    if all_passed:
        print("✅ ESCENARIO COMPLETO: ÉXITO")
    else:
        print("⚠️ ESCENARIO COMPLETO: ALGUNAS DIFERENCIAS")

    return all_passed

async def main():
    """Función principal de pruebas"""
    print("\n")
    print("=" * 70)
    print("         PRUEBAS DE GEMINI API")
    print("    Dropbox AI Organizer - URSALL System")
    print("=" * 70)
    print("\n")

    # Test 1: Verificar configuración
    if not await test_gemini_status():
        print("\n❌ No se puede continuar sin Gemini API configurada")
        return

    # Pausar entre tests
    await asyncio.sleep(1)

    # Test 2: Extracción de clientes
    test2_passed = await test_client_extraction()
    await asyncio.sleep(1)

    # Test 3: Extracción de tipos de documentos
    test3_passed = await test_doc_type_extraction()
    await asyncio.sleep(1)

    # Test 4: Extracción de fechas
    test4_passed = await test_date_extraction()
    await asyncio.sleep(1)

    # Test 5: Escenario real
    test5_passed = await test_real_scenario()

    # Resumen final
    print("\n")
    print("=" * 70)
    print("              RESUMEN FINAL")
    print("=" * 70)

    tests = [
        ("Configuración de Gemini", True),
        ("Extracción de Clientes", test2_passed),
        ("Extracción de Tipos de Documentos", test3_passed),
        ("Extracción de Fechas", test4_passed),
        ("Escenario Real Completo", test5_passed),
    ]

    passed_count = sum(1 for _, passed in tests if passed)
    total_count = len(tests)

    print(f"\n{'Test':<40} {'Resultado':>20}")
    print("-" * 70)
    for test_name, passed in tests:
        status = "✅ PASADO" if passed else "❌ FALLADO"
        print(f"{test_name:<40} {status:>20}")

    print("-" * 70)
    print(f"{'TOTAL':<40} {passed_count}/{total_count} PASADOS")
    print("=" * 70)

    if passed_count == total_count:
        print("\n[EXITO] TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
        print("\n[OK] Gemini esta funcionando correctamente y extrayendo informacion")
        print("     del lenguaje natural de las respuestas del usuario.")
    else:
        print(f"\n[ADVERTENCIA] {total_count - passed_count} prueba(s) fallaron")
        print("\nRevisa los logs anteriores para ver los detalles de los fallos.")

    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
