# -*- coding: utf-8 -*-
"""
Prueba completa del flujo de preguntas URSALL
Simulando respuestas en lenguaje natural
"""
import asyncio
import os
import sys
import json

# Forzar UTF-8 en Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Configurar API key
os.environ["GEMINI_API_KEY"] = "AIzaSyCtLooZwyZSaHRfi-y0JI2bd4PsZ-B6qYw"

from app.questions_ursall import (
    get_first_question_ursall,
    get_next_question_ursall,
    is_last_question_ursall
)
from app.gemini_rest_extractor import extract_with_gemini_rest
from app.nlp_extractor_legal import (
    extract_information_legal,
    extract_partes
)

async def simulate_user_answer(question_id, user_input, session_answers):
    """
    Simula el procesamiento de una respuesta del usuario
    (Igual que hace el endpoint /api/questions/answer)
    """
    print(f"\n  Usuario responde: '{user_input}'")

    # PASO 1: Intentar extracción con Gemini (si aplica)
    gemini_questions = ["client", "doc_type_proc", "doc_type_proyecto"]

    if question_id in gemini_questions:
        # Mapear a tipo de pregunta Gemini
        gemini_type = "client" if question_id == "client" else "doc_type"

        print(f"  -> Enviando a Gemini AI ({gemini_type})...")
        extracted = await extract_with_gemini_rest(gemini_type, user_input)

        if extracted and extracted.upper() != "AMBIGUO":
            print(f"  -> Gemini extrajo: '{extracted}'")
            return extracted
        else:
            print(f"  -> Gemini: AMBIGUO, usando respuesta original")
            return user_input.strip()

    # PASO 2: Usar extractores legales específicos
    legal_questions = [
        "jurisdiccion", "juzgado_num", "demarcacion",
        "num_procedimiento", "partes", "materia_proc",
        "proyecto_year", "proyecto_month",
        "proyecto_nombre", "proyecto_materia"
    ]

    if question_id in legal_questions:
        print(f"  -> Usando extractor legal ({question_id})...")
        extracted = extract_information_legal(question_id, user_input)

        # Caso especial: partes
        if question_id == "partes" and isinstance(extracted, dict):
            parte_a = extracted.get("parte_a", "")
            parte_b = extracted.get("parte_b", "")
            print(f"  -> Extractor legal extrajo:")
            print(f"     - Parte A: '{parte_a}'")
            print(f"     - Parte B: '{parte_b}'")

            # Guardar ambas partes en la sesión
            session_answers["parte_a"] = parte_a
            session_answers["parte_b"] = parte_b

            return extracted
        elif extracted:
            print(f"  -> Extractor legal extrajo: '{extracted}'")
            return extracted

    # PASO 3: Fechas - formato directo
    if question_id == "fecha_procedimiento":
        # Intentar con Gemini para normalización
        print(f"  -> Enviando a Gemini AI (date)...")
        extracted = await extract_with_gemini_rest("date", user_input)

        if extracted and extracted.upper() != "AMBIGUO":
            print(f"  -> Gemini normalizó fecha: '{extracted}'")
            return extracted

    # Por defecto, usar respuesta original
    print(f"  -> Usando respuesta original (sin extracción)")
    return user_input.strip()


async def test_procedimiento_flow():
    """
    Prueba flujo completo de PROCEDIMIENTO con lenguaje natural
    """
    print("\n" + "="*70)
    print("  TEST: FLUJO DE PROCEDIMIENTO JUDICIAL")
    print("="*70)

    # Simular sesión
    session = {
        "current_question": "tipo_trabajo",
        "answers": {},
        "extracted_answers": {}
    }

    # Respuestas del usuario en lenguaje natural
    user_responses = {
        "tipo_trabajo": "procedimiento",
        "client": "el cliente es GRUPO GORETTI",
        "jurisdiccion": "Juzgado de lo Social",
        "juzgado_num": "es el juzgado numero 2",
        "demarcacion": "de Tenerife",
        "num_procedimiento": "el numero es 455/2025",
        "fecha_procedimiento": "la fecha es 08/05/2025",
        "partes": "Pedro Perez contra Cabildo Gomera",
        "materia_proc": "materia de Despidos",
        "doc_type_proc": "Es una Escritura de demanda"
    }

    # Orden de preguntas esperado (segun questions_ursall.py)
    question_order = [
        "tipo_trabajo",
        "client",
        "jurisdiccion",
        "juzgado_num",
        "demarcacion",
        "num_procedimiento",
        "fecha_procedimiento",
        "partes",
        "materia_proc",
        "doc_type_proc"
    ]

    current_q = "tipo_trabajo"
    question_num = 1
    total_questions = len(question_order)

    for expected_q in question_order:
        print(f"\n[{question_num}/{total_questions}] Pregunta: {expected_q}")

        # Obtener pregunta
        if current_q == "tipo_trabajo":
            question_data = get_first_question_ursall()
        else:
            question_data = get_next_question_ursall(
                current_question_id=prev_q,
                answers=session["answers"]
            )

        print(f"  Sistema pregunta: '{question_data['question_text']}'")

        # Obtener respuesta del usuario
        user_input = user_responses.get(current_q, "")

        # Procesar respuesta
        extracted = await simulate_user_answer(current_q, user_input, session["answers"])

        # Guardar en sesión
        session["answers"][current_q] = extracted
        session["extracted_answers"][current_q] = extracted

        print(f"  [OK] Valor guardado: '{extracted}'")

        # Avanzar a siguiente pregunta
        prev_q = current_q

        if question_num < total_questions:
            next_q = get_next_question_ursall(current_q, session["answers"])
            current_q = next_q["question_id"] if next_q else None

        question_num += 1

    # Mostrar resumen
    print("\n" + "="*70)
    print("  RESUMEN DE DATOS EXTRAIDOS")
    print("="*70)

    for key, value in session["answers"].items():
        print(f"  {key:<25} = {value}")

    # Validaciones
    print("\n" + "="*70)
    print("  VALIDACIONES")
    print("="*70)

    validations = [
        ("Cliente", "GORETTI" in str(session["answers"].get("client", "")).upper()),
        ("Tipo doc", "escritura" in str(session["answers"].get("doc_type_proc", "")).lower()),
        ("Fecha ISO", "2025-05-08" in str(session["answers"].get("fecha_procedimiento", ""))),
        ("Jurisdiccion", "social" in str(session["answers"].get("jurisdiccion", "")).lower()),
        ("Juzgado num", session["answers"].get("juzgado_num") == "2"),
        ("Demarcacion", "Tenerife" in str(session["answers"].get("demarcacion", ""))),
        ("Num proc", "455/2025" in str(session["answers"].get("num_procedimiento", ""))),
        ("Parte A", "Pedro" in str(session["answers"].get("parte_a", ""))),
        ("Parte B", "Cabildo" in str(session["answers"].get("parte_b", ""))),
        ("Materia", "Despidos" in str(session["answers"].get("materia_proc", ""))),
    ]

    passed = sum(1 for _, valid in validations if valid)
    total = len(validations)

    for name, valid in validations:
        status = "[OK]" if valid else "[FAIL]"
        print(f"  {status} {name}")

    print(f"\n  Resultado: {passed}/{total} validaciones pasaron")

    return passed == total


async def test_proyecto_flow():
    """
    Prueba flujo completo de PROYECTO con lenguaje natural
    """
    print("\n" + "="*70)
    print("  TEST: FLUJO DE PROYECTO JURIDICO")
    print("="*70)

    session = {
        "current_question": "tipo_trabajo",
        "answers": {},
        "extracted_answers": {}
    }

    user_responses = {
        "tipo_trabajo": "proyecto",
        "client": "el cliente se llama Ayuntamiento de La Laguna",
        "proyecto_year": "año 2025",
        "proyecto_month": "mes de agosto",
        "proyecto_nombre": "Informe sobre accidente laboral",
        "proyecto_materia": "sobre Derecho Laboral",
        "doc_type_proyecto": "Es un Informe pericial"
    }

    question_order = [
        "tipo_trabajo",
        "client",
        "proyecto_year",
        "proyecto_month",
        "proyecto_nombre",
        "proyecto_materia",
        "doc_type_proyecto"
    ]

    current_q = "tipo_trabajo"
    question_num = 1
    total_questions = len(question_order)

    for expected_q in question_order:
        print(f"\n[{question_num}/{total_questions}] Pregunta: {expected_q}")

        if current_q == "tipo_trabajo":
            question_data = get_first_question_ursall()
        else:
            question_data = get_next_question_ursall(
                current_question_id=prev_q,
                answers=session["answers"]
            )

        print(f"  Sistema pregunta: '{question_data['question_text']}'")

        user_input = user_responses.get(current_q, "")
        extracted = await simulate_user_answer(current_q, user_input, session["answers"])

        session["answers"][current_q] = extracted
        session["extracted_answers"][current_q] = extracted

        print(f"  [OK] Valor guardado: '{extracted}'")

        prev_q = current_q

        if question_num < total_questions:
            next_q = get_next_question_ursall(current_q, session["answers"])
            current_q = next_q["question_id"] if next_q else None

        question_num += 1

    # Mostrar resumen
    print("\n" + "="*70)
    print("  RESUMEN DE DATOS EXTRAIDOS")
    print("="*70)

    for key, value in session["answers"].items():
        print(f"  {key:<25} = {value}")

    # Validaciones
    print("\n" + "="*70)
    print("  VALIDACIONES")
    print("="*70)

    validations = [
        ("Cliente", "Ayuntamiento" in str(session["answers"].get("client", ""))),
        ("Tipo doc", "informe" in str(session["answers"].get("doc_type_proyecto", "")).lower()),
        ("Año", "2025" in str(session["answers"].get("proyecto_year", ""))),
        ("Mes", "08" in str(session["answers"].get("proyecto_month", ""))),
    ]

    passed = sum(1 for _, valid in validations if valid)
    total = len(validations)

    for name, valid in validations:
        status = "[OK]" if valid else "[FAIL]"
        print(f"  {status} {name}")

    print(f"\n  Resultado: {passed}/{total} validaciones pasaron")

    return passed == total


async def main():
    print("\n" + "="*70)
    print("  PRUEBA COMPLETA DE FLUJO DE PREGUNTAS URSALL")
    print("  Con respuestas en lenguaje natural")
    print("="*70)

    # Test 1: Procedimiento
    test1_passed = await test_procedimiento_flow()
    await asyncio.sleep(1)

    # Test 2: Proyecto
    test2_passed = await test_proyecto_flow()

    # Resumen final
    print("\n" + "="*70)
    print("  RESUMEN FINAL")
    print("="*70)

    tests = [
        ("Flujo de Procedimiento", test1_passed),
        ("Flujo de Proyecto", test2_passed)
    ]

    passed_count = sum(1 for _, passed in tests if passed)
    total_count = len(tests)

    print(f"\n{'Test':<40} {'Resultado':>20}")
    print("-" * 70)
    for test_name, passed in tests:
        status = "[OK] PASADO" if passed else "[FAIL] FALLADO"
        print(f"{test_name:<40} {status:>25}")

    print("-" * 70)
    print(f"{'TOTAL':<40} {passed_count}/{total_count} PASADOS")
    print("=" * 70)

    if passed_count == total_count:
        print("\n[EXITO] Todas las pruebas pasaron!")
        print("        El sistema extrae informacion correctamente del lenguaje natural.")
    else:
        print(f"\n[PARCIAL] {total_count - passed_count} prueba(s) fallaron")

    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nPrueba interrumpida por el usuario")
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
