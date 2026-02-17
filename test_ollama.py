#!/usr/bin/env python3
"""
Test Ollama Integration with Z3ube

This script tests the Ollama Llama 3.1 70B integration.
"""

import sys
import os
import subprocess
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

def print_status(message, status="INFO"):
    """Print formatted status message"""
    icons = {"INFO": "ℹ️", "OK": "✅", "FAIL": "❌", "WARN": "⚠️"}
    print(f"{icons.get(status, '•')} {message}")

def check_ollama_running():
    """Check if Ollama service is running"""
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/tags"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False

def check_model_downloaded(model_name="llama3.1:70b"):
    """Check if specified model is downloaded"""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True
        )
        return model_name in result.stdout
    except:
        return False

def test_ollama_chat():
    """Test Ollama with a simple query"""
    try:
        result = subprocess.run(
            ["ollama", "run", "llama3.2:3b", "What is 2+2? Answer briefly."],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0 and result.stdout.strip()
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  Z3ube Ollama Integration Verification")
    print("="*60 + "\n")
    
    # Check 1: Ollama installed
    print_status("Checking if Ollama is installed...")
    try:
        result = subprocess.run(["which", "ollama"], capture_output=True)
        if result.returncode == 0:
            print_status("Ollama is installed", "OK")
        else:
            print_status("Ollama is NOT installed", "FAIL")
            print("\n  Install with: brew install ollama")
            return
    except:
        print_status("Could not check Ollama installation", "FAIL")
        return
    
    # Check 2: Ollama service running
    print_status("Checking if Ollama service is running...")
    if check_ollama_running():
        print_status("Ollama service is running", "OK")
    else:
        print_status("Ollama service is NOT running", "WARN")
        print("  Start with: ollama serve")
    
    # Check 3: Model downloaded
    print_status("Checking if Llama 3.2 3B is downloaded...")
    if check_model_downloaded("llama3.2:3b"):
        print_status("Llama 3.2 3B model is downloaded", "OK")
    else:
        print_status("Llama 3.2 3B is NOT fully downloaded yet", "WARN")
        print("  Check download progress with: ollama list")
        print("  Download with: ollama pull llama3.2:3b")
        
        # Check download progress
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            if "llama3.2" in result.stdout:
                print("\n  Download in progress:")
                for line in result.stdout.split('\n'):
                    if 'llama3.2' in line:
                        print(f"  {line}")
        except:
            pass
    
    # Check 4: Environment configuration
    print_status("Checking Z3ube configuration...")
    from dotenv import load_dotenv
    load_dotenv()
    
    use_ollama = os.getenv("USE_OLLAMA", "false").lower()
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    
    print(f"  USE_OLLAMA: {use_ollama}")
    print(f"  OLLAMA_MODEL: {ollama_model}")
    
    if use_ollama == "true":
        print_status("Ollama is ENABLED in Z3ube config", "OK")
    else:
        print_status("Ollama is DISABLED in Z3ube config", "WARN")
        print("  Enable in .env: USE_OLLAMA=true")
    
    # Check 5: Test integration (only if model is ready)
    if check_model_downloaded("llama3.2:3b") and check_ollama_running():
        print_status("Testing Ollama integration with Z3ube...")
        try:
            from core.reasoning_engine import reasoning_engine
            
            if reasoning_engine.use_ollama:
                print_status("Ollama integration is active in reasoning engine", "OK")
                print(f"  Model: {reasoning_engine.ollama_model}")
            else:
                print_status("Ollama not initialized in reasoning engine", "WARN")
                
        except Exception as e:
            print_status(f"Could not test integration: {e}", "WARN")
    
    # Summary
    print("\n" + "="*60)
    print("  Summary")
    print("="*60 + "\n")
    
    if check_model_downloaded("llama3.1:70b"):
        print("✅ Ollama Llama 3.1 70B is ready to use!")
        print("\n  Your Z3ube will now use:")
        print("  • Llama 3.1 70B (local) - every 3rd reasoning step")
        print("  • OpenAI GPT-4 - even numbered steps")
        print("  • Anthropic Claude - odd numbered steps")
        print("\n  This provides diverse AI perspectives while keeping data local!")
    else:
        print("⏳ Llama 3.1 70B is still downloading...")
        print("\n  What's happening:")
        print("  • Download is ~42 GB and takes 1-2 hours")
        print("  • Z3ube will use cloud APIs only until download completes")
        print("  • Once complete, restart the backend server to enable Ollama")
        print("\n  To check progress: ollama list")
    
    print()

if __name__ == "__main__":
    main()
