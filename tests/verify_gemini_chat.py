
import requests
import json
import sys

def test_gemini_chat():
    url = "http://localhost:8000/chat/stream"
    headers = {"Content-Type": "application/json"}
    payload = {
        "message": "Hello, are you Gemini 2.0?",
        "depth": "quick",
        "model": "gemini"
    }

    print("Testing Gemini Chat API...")
    try:
        with requests.post(url, json=payload, headers=headers, stream=True) as response:
            if response.status_code != 200:
                print(f"❌ API Error: {response.status_code}")
                print(response.text)
                sys.exit(1)
            
            print("✅ Connection established. Streaming response...")
            full_response = ""
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if data['type'] == 'content':
                            content = data['data']
                            print(content, end="", flush=True)
                            full_response += content
                        elif data['type'] == 'error':
                             print(f"\n❌ Stream Error: {data['data']}")
                             sys.exit(1)
                    except json.JSONDecodeError:
                        pass
            
            print("\n\n✅ Stream completed successfully.")
            if len(full_response) == 0:
                print("⚠️ Warning: Received empty response content.")
            else: 
                print(f"Response length: {len(full_response)} chars")

    except Exception as e:
        print(f"\n❌ Request failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_gemini_chat()
