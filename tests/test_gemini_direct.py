
import os
from dotenv import load_dotenv

load_dotenv()

def test_gemini():
    print("Testing Gemini Direct Integration...")
    api_key = os.getenv("GOOGLE_API_KEY")
    model_id = os.getenv("GEMINI_MODEL")
    
    print(f"API Key present: {bool(api_key)}")
    print(f"Model ID: {model_id}")
    
    try:
        from google import genai
        
        client = genai.Client(api_key=api_key)
        
        # Test specific model
        model_id = "gemini-3-flash-preview"
        print(f"Testing model: {model_id}")
        response = client.models.generate_content(
            model=model_id,
            contents="Hello Gemini 3!"
        )
        print(f"✅ Success with {model_id}!")
        print(response.text)
        
        # Test with prefix if above fails (but script will exit on fail)

        
        print("\n✅ Response received:")
        print(response.text)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gemini()
