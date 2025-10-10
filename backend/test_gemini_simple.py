# -*- coding: utf-8 -*-
"""
Script de prueba simplificado para verificar Gemini API
"""
import asyncio
import os
import sys

# Forzar UTF-8 en Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Configurar API key
os.environ["GEMINI_API_KEY"] = "AIzaSyCtLooZwyZSaHRfi-y0JI2bd4PsZ-B6qYw"

from app.gemini_rest_extractor import extract_with_gemini_rest, check_gemini_status

async def main():
    print("\n" + "="*70)
    print("  PRUEBAS DE GEMINI API - URSALL System")
    print("="*70 + "\n")

    # Test 1: Verificar configuración
    print("[1/4] Verificando configuracion de Gemini...")
    status = check_gemini_status()
    print(f"  - Gemini disponible: {status['gemini_available']}")
    print(f"  - API key configurada: {status['api_key_configured']}")
    print(f"  - Tipo de API: {status['api_type']}")

    if not status['gemini_available']:
        print("\n[ERROR] Gemini API no esta configurada")
        return

    print("  [OK] Gemini configurado correctamente\n")

    # Test 2: Extracción de cliente
    print("[2/4] Probando extraccion de nombre de cliente...")
    test_input = "El cliente es GRUPO GORETTI"
    print(f"  Input: '{test_input}'")

    result = await extract_with_gemini_rest("client", test_input)
    if result:
        print(f"  Output: '{result}'")
        if "GORETTI" in result.upper():
            print("  [OK] Extraccion correcta\n")
        else:
            print(f"  [WARN] Resultado inesperado\n")
    else:
        print("  [ERROR] No se obtuvo resultado\n")

    # Test 3: Extracción de tipo de documento
    print("[3/4] Probando extraccion de tipo de documento...")
    test_input = "Es una Escritura de demanda"
    print(f"  Input: '{test_input}'")

    result = await extract_with_gemini_rest("doc_type", test_input)
    if result:
        print(f"  Output: '{result}'")
        if "escritura" in result.lower():
            print("  [OK] Extraccion correcta\n")
        else:
            print(f"  [WARN] Resultado: {result}\n")
    else:
        print("  [ERROR] No se obtuvo resultado\n")

    # Test 4: Extracción de fecha
    print("[4/4] Probando extraccion y normalizacion de fecha...")
    test_input = "La fecha es 08/05/2025"
    print(f"  Input: '{test_input}'")

    result = await extract_with_gemini_rest("date", test_input)
    if result:
        print(f"  Output: '{result}'")
        if "2025-05-08" in result:
            print("  [OK] Fecha normalizada correctamente\n")
        else:
            print(f"  [WARN] Formato de fecha: {result}\n")
    else:
        print("  [ERROR] No se obtuvo resultado\n")

    # Test 5: Caso real completo
    print("="*70)
    print("  ESCENARIO REAL COMPLETO")
    print("="*70 + "\n")

    casos = [
        ("client", "el cliente es GRUPO GORETTI", "GRUPO GORETTI"),
        ("doc_type", "Es una Pericial", "pericial"),
        ("date", "08/05/2025", "2025-05-08"),
        ("client", "Cabildo de La Gomera", "Cabildo"),
    ]

    exitos = 0
    total = len(casos)

    for i, (qid, input_text, expected) in enumerate(casos, 1):
        print(f"[{i}/{total}] Pregunta: {qid}")
        print(f"      Usuario: '{input_text}'")

        result = await extract_with_gemini_rest(qid, input_text)

        if result and expected.lower() in result.lower():
            print(f"      Gemini: '{result}' [OK]")
            exitos += 1
        elif result:
            print(f"      Gemini: '{result}' [DIFERENTE]")
        else:
            print(f"      [ERROR] Sin resultado")

        print()
        await asyncio.sleep(0.5)

    # Resumen final
    print("="*70)
    print("  RESUMEN FINAL")
    print("="*70)
    print(f"\nPruebas exitosas: {exitos}/{total}")

    if exitos == total:
        print("\n[EXITO] Gemini funciona correctamente!")
        print("        Esta extrayendo informacion del lenguaje natural.")
    else:
        print(f"\n[PARCIAL] {exitos} de {total} pruebas pasaron")

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
