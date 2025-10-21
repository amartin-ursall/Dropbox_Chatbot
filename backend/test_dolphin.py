"""
Test script to verify Dolphin parser functionality
Tests both REST API and local model parsing
"""

import sys
import os
import asyncio
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.dolphin_parser import (
    get_dolphin_parser,
    is_dolphin_available,
    parse_document_with_dolphin
)
from app.dolphin_rest_client import (
    DolphinRestClient,
    check_dolphin_api_status,
    is_dolphin_api_available
)


def test_dolphin_parser():
    """Test Dolphin parser with example document"""

    print("=" * 80)
    print("DOLPHIN PARSER TEST")
    print("=" * 80)

    # Check if Dolphin is available
    print("\n1. Checking Dolphin availability...")
    available = is_dolphin_available()
    print(f"   Dolphin available: {available}")

    if not available:
        print("\n[ERROR] Dolphin is not available. Cannot proceed with test.")
        print("\nPossible reasons:")
        print("  - Missing dependencies (torch, transformers, omegaconf)")
        print("  - Model files not found")
        print("  - Configuration issues")
        return False

    # Get parser instance
    print("\n2. Loading Dolphin parser...")
    try:
        parser = get_dolphin_parser()
        if parser is None:
            print("   [ERROR] Failed to load Dolphin parser (returned None)")
            return False
        print("   [OK] Dolphin parser loaded successfully")
    except Exception as e:
        print(f"   [ERROR] Error loading parser: {e}")
        return False

    # Find example document
    print("\n3. Looking for test document...")
    example_dir = backend_dir.parent / "example"
    test_files = list(example_dir.glob("*.pdf"))

    if not test_files:
        print(f"   [ERROR] No PDF files found in {example_dir}")
        return False

    test_file = test_files[0]
    print(f"   [OK] Found test file: {test_file.name}")
    print(f"   File size: {test_file.stat().st_size / 1024:.2f} KB")

    # Parse document
    print("\n4. Parsing document with Dolphin...")
    print("   (This may take a few moments...)")

    try:
        parsed_content, confidence = parser.parse_document(str(test_file))
        print(f"   [OK] Document parsed successfully!")
        print(f"   Confidence score: {confidence:.2f}")

        # Display results
        print("\n5. Parse Results:")
        print("-" * 80)
        print(f"   Pages: {parsed_content.get('pages', 'N/A')}")
        print(f"   Has tables: {parsed_content.get('has_tables', False)}")
        print(f"   Has figures: {parsed_content.get('has_figures', False)}")

        text = parsed_content.get('text', '')
        print(f"\n   Extracted text length: {len(text)} characters")

        if text:
            print("\n   First 500 characters of extracted text:")
            print("-" * 80)
            print(text[:500])
            print("-" * 80)
        else:
            print("   [WARNING] No text was extracted")

        print("\n" + "=" * 80)
        print("[SUCCESS] DOLPHIN TEST COMPLETED SUCCESSFULLY")
        print("=" * 80)
        return True

    except Exception as e:
        print(f"   [ERROR] Error during parsing: {e}")
        import traceback
        print("\nFull traceback:")
        print("-" * 80)
        traceback.print_exc()
        print("-" * 80)
        return False


async def test_dolphin_rest_api():
    """Test Dolphin REST API"""

    print("=" * 80)
    print("DOLPHIN REST API TEST")
    print("=" * 80)

    # Check if REST API is available
    print("\n1. Checking Dolphin REST API availability...")
    status = await check_dolphin_api_status()

    if not status.get('available'):
        print(f"   [ERROR] Dolphin REST API is not available")
        print(f"   Error: {status.get('error')}")
        print("\nPossible reasons:")
        print("  - Dolphin API service is not running at 192.168.0.98:1000")
        print("  - Network connectivity issues")
        print("  - DOLPHIN_API_URL not configured in .env")
        return False

    print(f"   [OK] Dolphin REST API is available at {status.get('api_url')}")
    health = status.get('health', {})
    print(f"   Status: {health.get('status')}")
    print(f"   Model loaded: {health.get('model_loaded')}")
    print(f"   Device: {health.get('device')}")

    # Find test document
    print("\n2. Looking for test document...")
    example_dir = backend_dir.parent / "example"
    test_files = list(example_dir.glob("*.pdf"))

    if not test_files:
        # Try to use any test document
        test_files = list(example_dir.glob("*.*"))
        test_files = [f for f in test_files if f.suffix.lower() in ['.pdf', '.jpg', '.jpeg', '.png']]

    if not test_files:
        print(f"   [ERROR] No test files found in {example_dir}")
        print("   Please provide a test file (PDF, JPG, PNG)")
        return False

    test_file = test_files[0]
    print(f"   [OK] Found test file: {test_file.name}")
    print(f"   File size: {test_file.stat().st_size / 1024:.2f} KB")

    # Parse document via REST API
    print("\n3. Parsing document via REST API...")
    print("   (This may take a few moments...)")

    try:
        client = DolphinRestClient()
        parsed_content, confidence = await client.parse_document(str(test_file))

        print(f"   [OK] Document parsed successfully!")
        print(f"   Confidence score: {confidence:.2f}")

        # Display results
        print("\n4. Parse Results:")
        print("-" * 80)
        print(f"   File type: {parsed_content.get('file_type', 'N/A')}")
        print(f"   Pages: {parsed_content.get('pages', 'N/A')}")
        print(f"   Elements found: {len(parsed_content.get('elements', []))}")
        print(f"   Has tables: {parsed_content.get('has_tables', False)}")
        print(f"   Has figures: {parsed_content.get('has_figures', False)}")

        text = parsed_content.get('text', '')
        print(f"\n   Extracted text length: {len(text)} characters")

        if text:
            print("\n   First 500 characters of extracted text:")
            print("-" * 80)
            print(text[:500])
            print("-" * 80)

            # Show element types
            elements = parsed_content.get('elements', [])
            if elements:
                element_types = {}
                for elem in elements:
                    label = elem.get('label', 'unknown')
                    element_types[label] = element_types.get(label, 0) + 1

                print("\n   Element types found:")
                for label, count in sorted(element_types.items()):
                    print(f"     {label}: {count}")
        else:
            print("   [WARNING] No text was extracted")

        print("\n" + "=" * 80)
        print("[SUCCESS] DOLPHIN REST API TEST COMPLETED SUCCESSFULLY")
        print("=" * 80)
        return True

    except Exception as e:
        print(f"   [ERROR] Error during parsing: {e}")
        import traceback
        print("\nFull traceback:")
        print("-" * 80)
        traceback.print_exc()
        print("-" * 80)
        return False


async def test_unified_parser():
    """Test unified parser (auto mode - tries API first, then local)"""

    print("\n" + "=" * 80)
    print("UNIFIED PARSER TEST (AUTO MODE)")
    print("=" * 80)

    # Find test document
    print("\n1. Looking for test document...")
    example_dir = backend_dir.parent / "example"
    test_files = list(example_dir.glob("*.pdf"))

    if not test_files:
        test_files = list(example_dir.glob("*.*"))
        test_files = [f for f in test_files if f.suffix.lower() in ['.pdf', '.jpg', '.jpeg', '.png']]

    if not test_files:
        print(f"   [ERROR] No test files found in {example_dir}")
        return False

    test_file = test_files[0]
    print(f"   [OK] Using test file: {test_file.name}")

    # Parse with auto mode
    print("\n2. Parsing with unified parser (auto mode)...")
    print("   Will try REST API first, then fallback to local model")

    try:
        parsed_content, confidence = await parse_document_with_dolphin(
            str(test_file),
            mode="auto"
        )

        print(f"   [OK] Document parsed successfully!")
        print(f"   Confidence score: {confidence:.2f}")
        print(f"   Pages: {parsed_content.get('pages', 'N/A')}")
        print(f"   Elements: {len(parsed_content.get('elements', []))}")

        print("\n" + "=" * 80)
        print("[SUCCESS] UNIFIED PARSER TEST COMPLETED SUCCESSFULLY")
        print("=" * 80)
        return True

    except Exception as e:
        print(f"   [ERROR] Error during parsing: {e}")
        return False


async def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("DOLPHIN COMPREHENSIVE TEST SUITE")
    print("=" * 80)

    results = []

    # Test 1: REST API
    print("\n>>> TEST 1: REST API")
    results.append(("REST API", await test_dolphin_rest_api()))

    # Test 2: Local Model (if available)
    print("\n>>> TEST 2: LOCAL MODEL")
    if is_dolphin_available():
        results.append(("Local Model", test_dolphin_parser()))
    else:
        print("   [WARNING] Local model not available, skipping...")
        results.append(("Local Model", None))

    # Test 3: Unified Parser
    print("\n>>> TEST 3: UNIFIED PARSER")
    results.append(("Unified Parser", await test_unified_parser()))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result is True)
    skipped = sum(1 for _, result in results if result is None)
    failed = sum(1 for _, result in results if result is False)
    total = len(results)

    for test_name, result in results:
        if result is True:
            status = "[PASSED]"
        elif result is None:
            status = "[SKIPPED]"
        else:
            status = "[FAILED]"
        print(f"  {test_name}: {status}")

    print(f"\n  Passed: {passed}/{total - skipped}")
    if skipped > 0:
        print(f"  Skipped: {skipped}/{total}")
    if failed > 0:
        print(f"  Failed: {failed}/{total}")

    success = failed == 0 and passed > 0
    return success


if __name__ == "__main__":
    print("\nStarting Dolphin comprehensive test suite...\n")

    # Check if user wants to run all tests or specific test
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()

        if mode == "api":
            print("Running REST API test only...\n")
            success = asyncio.run(test_dolphin_rest_api())
        elif mode == "local":
            print("Running local model test only...\n")
            success = test_dolphin_parser()
        elif mode == "unified":
            print("Running unified parser test only...\n")
            success = asyncio.run(test_unified_parser())
        else:
            print(f"Unknown mode: {mode}")
            print("Usage: python test_dolphin.py [api|local|unified]")
            sys.exit(1)
    else:
        # Run all tests
        success = asyncio.run(run_all_tests())

    exit_code = 0 if success else 1
    print(f"\n{'='*80}")
    print(f"OVERALL RESULT: {'[PASSED]' if success else '[FAILED]'}")
    print(f"{'='*80}\n")
    sys.exit(exit_code)
