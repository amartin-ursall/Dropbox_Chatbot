"""
Test the question flow with natural language responses
"""
import asyncio
from app.questions_ursall import get_first_question_ursall


async def test_first_question():
    """Test that the first question accepts natural language"""

    print("=" * 70)
    print("Testing First Question Natural Language Support")
    print("=" * 70)
    print()

    first_question = get_first_question_ursall()

    print(f"Question ID: {first_question['question_id']}")
    print(f"Question Text: {first_question['question_text']}")
    print()
    print(f"Help Text: {first_question['help_text']}")
    print()
    print("Examples:")
    for example in first_question['examples']:
        print(f"  - {example}")
    print()

    print("=" * 70)
    print()

    # Verify the question text is more open
    assert "procedimiento o proyecto" not in first_question['question_text'].lower(), \
        "Question text should not force exact keywords"

    assert len(first_question['examples']) > 2, \
        "Should have multiple natural language examples"

    print("[OK] First question supports natural language")
    print()


async def main():
    await test_first_question()


if __name__ == "__main__":
    asyncio.run(main())
