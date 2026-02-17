
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

def list_models():
    print("Listing models...")
    try:
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        for model in client.models.list():
            print(f"- {model.name}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_models()
