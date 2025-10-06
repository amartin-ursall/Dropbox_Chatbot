"""
Test script to diagnose Gemini API issues
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print(f"API Key found: {bool(GEMINI_API_KEY)}")
print(f"API Key starts with: {GEMINI_API_KEY[:20] if GEMINI_API_KEY else 'N/A'}...")

if GEMINI_API_KEY:
    try:
        # Configure
        genai.configure(api_key=GEMINI_API_KEY)
        print("✓ Gemini configured successfully")

        # Create model
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✓ Model created successfully")

        # Test simple prompt
        print("\n--- Testing simple extraction ---")
        prompt = """Extrae ÚNICAMENTE el nombre del cliente de la siguiente respuesta del usuario.
Respuesta del usuario: "El cliente es Juan"
Nombre del cliente:"""

        print(f"Prompt: {prompt[:100]}...")

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=50,
            )
        )

        print(f"\n✓ Response received")
        print(f"Response object: {type(response)}")
        print(f"Has text attribute: {hasattr(response, 'text')}")

        if hasattr(response, 'candidates'):
            print(f"Candidates: {len(response.candidates)}")
            if response.candidates:
                print(f"First candidate: {response.candidates[0]}")
                print(f"Finish reason: {response.candidates[0].finish_reason}")

        try:
            text = response.text
            print(f"\n✓ Extracted text: '{text}'")
        except Exception as e:
            print(f"\n✗ Error accessing text: {e}")
            print(f"Full response: {response}")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("✗ No API key found in .env file")
