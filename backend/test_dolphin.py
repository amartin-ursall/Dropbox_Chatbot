"""
Test script to verify Dolphin parser functionality
Tests parsing a document from the example folder
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.dolphin_parser import get_dolphin_parser, is_dolphin_available


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
        print("\n❌ Dolphin is not available. Cannot proceed with test.")
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
            print("   ❌ Failed to load Dolphin parser (returned None)")
            return False
        print("   ✅ Dolphin parser loaded successfully")
    except Exception as e:
        print(f"   ❌ Error loading parser: {e}")
        return False

    # Find example document
    print("\n3. Looking for test document...")
    example_dir = backend_dir.parent / "example"
    test_files = list(example_dir.glob("*.pdf"))

    if not test_files:
        print(f"   ❌ No PDF files found in {example_dir}")
        return False

    test_file = test_files[0]
    print(f"   ✅ Found test file: {test_file.name}")
    print(f"   File size: {test_file.stat().st_size / 1024:.2f} KB")

    # Parse document
    print("\n4. Parsing document with Dolphin...")
    print("   (This may take a few moments...)")

    try:
        parsed_content, confidence = parser.parse_document(str(test_file))
        print(f"   ✅ Document parsed successfully!")
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
            print("   ⚠️  Warning: No text was extracted")

        print("\n" + "=" * 80)
        print("✅ DOLPHIN TEST COMPLETED SUCCESSFULLY")
        print("=" * 80)
        return True

    except Exception as e:
        print(f"   ❌ Error during parsing: {e}")
        import traceback
        print("\nFull traceback:")
        print("-" * 80)
        traceback.print_exc()
        print("-" * 80)
        return False


if __name__ == "__main__":
    print("\nStarting Dolphin parser test...\n")
    success = test_dolphin_parser()

    exit_code = 0 if success else 1
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(exit_code)
