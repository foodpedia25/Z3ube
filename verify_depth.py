
import requests
import json
import sys

API_URL = "http://localhost:8000"

def test_chat_depth(depth="quick"):
    print(f"\n--- Testing /chat with depth='{depth}' ---")
    payload = {
        "message": "What is the capital of France?",
        "depth": depth
    }
    
    try:
        response = requests.post(f"{API_URL}/chat", json=payload)
        response.raise_for_status()
        data = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Response: {data['response'][:50]}...")
        
        # Verify thinking steps count based on depth
        steps = data.get("thinking_steps", [])
        print(f"Thinking Steps: {len(steps)}")
        
        expected_steps = 3 if depth == "quick" else 5 if depth == "normal" else 8
        if len(steps) == expected_steps:
             print("✅ Steps count matches expected depth.")
        else:
             print(f"⚠️ Steps count ({len(steps)}) does not match expected ({expected_steps}).")
             
    except Exception as e:
        print(f"❌ Error: {e}")
        try:
            if 'response' in locals():
                print(f"Error Details: {response.text}")
        except:
            pass

def test_stream_depth(depth="quick"):
    print(f"\n--- Testing /chat/stream with depth='{depth}' ---")
    payload = {
        "message": "Count to 3",
        "depth": depth
    }
    
    try:
        response = requests.post(f"{API_URL}/chat/stream", json=payload, stream=True)
        response.raise_for_status()
        
        step_count = 0
        print("Streaming response...")
        
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if data.get("type") == "step":
                        step_count += 1
                        print(f"  Step {data['data']['step']}: {data['data']['thought'][:40]}...")
                except:
                    pass
        
        print(f"Total Steps Received: {step_count}")
        
        expected_steps = 3 if depth == "quick" else 5 if depth == "normal" else 8
        if step_count == expected_steps:
             print("✅ Stream steps count matches expected depth.")
        else:
             print(f"⚠️ Stream steps count ({step_count}) does not match expected ({expected_steps}).")

    except Exception as e:
        print(f"❌ Error: {e}")
        try:
            if 'response' in locals():
                print(f"Error Details: {response.text}")
        except:
            pass

if __name__ == "__main__":
    print("🚀 Verifying Backend Depth Parameter...")
    
    # Test Quick (3 steps)
    test_chat_depth("quick")
    
    # Test Normal (5 steps)
    test_chat_depth("normal")
    
    # Test Deep Stream (8 steps)
    test_stream_depth("deep")
