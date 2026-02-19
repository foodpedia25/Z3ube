import requests
import json
import time

BASE_URL = "https://z3ube.vercel.app/api"

def test_health():
    print("🔍 Testing System Health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Health Check Passed")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Health Check Failed: {response.text}")
    except Exception as e:
        print(f"❌ Health Check Error: {e}")

def test_system_status():
    print("\n🔍 Testing Neural Dashboard Stats...")
    try:
        response = requests.get(f"{BASE_URL}/system/status")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ System Status Passed")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ System Status Failed: {response.text}")
    except Exception as e:
        print(f"❌ System Status Error: {e}")

def test_chat():
    print("\n🔍 Testing Reasoning Engine (Chat)...")
    payload = {
        "message": "Explain the concept of self-learning AI in one sentence.",
        "depth": "quick",
        "model": "auto"
    }
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Chat API Passed")
            data = response.json()
            print(f"AI Response: {data.get('response')}")
            steps = data.get('thinking_steps', [])
            print(f"Thinking Steps: {len(steps)}")
            for s in steps:
                print(f"  Step {s.get('step')}: {s.get('reasoning')}")
        else:
            print(f"❌ Chat API Failed: {response.text}")
    except Exception as e:
        print(f"❌ Chat API Error: {e}")

def test_robotics():
    print("\n🔍 Testing Robotics Project Generation...")
    payload = {
        "description": "A basic ROS2 node that publishes 'Hello World' every second.",
        "language": "ros2_python"
    }
    try:
        response = requests.post(f"{BASE_URL}/code/project", json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Robotics API Passed")
            data = response.json()
            files = data.get('files', {})
            print(f"Files Generated: {list(files.keys())}")
            if 'error.txt' in files:
                print(f"  Error Content: {files['error.txt']}")
        else:
            print(f"❌ Robotics API Failed: {response.text}")
    except Exception as e:
        print(f"❌ Robotics API Error: {e}")

if __name__ == "__main__":
    print(f"🚀 Starting Production Verification for {BASE_URL}\n")
    test_health()
    test_system_status()
    test_chat()
    test_robotics()
