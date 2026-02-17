#!/usr/bin/env python3
"""
Test Gemini AI Integration

This script tests if the Google Gemini API is working correctly.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
import asyncio

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

def test_gemini():
    print("\n" + "="*60)
    print("  Z3ube Gemini AI Verification")
    print("="*60 + "\n")
    
    # Load env
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in .env")
        return False
        
    print(f"✅ Found GOOGLE_API_KEY: {api_key[:5]}...{api_key[-5:]}")
    
    try:
        # Configure
        genai.configure(api_key=api_key)
        
        # List models to verify access
        print("\nChecking available models...")
        models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                models.append(m.name)
                print(f"  • {m.name}")
        
        # Test generation with Gemini 2.0 Flash (fast and capable)
        model_name = "gemini-2.0-flash"
        print(f"\nTesting generation with {model_name}...")
        
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Explain quantum entanglement in one sentence.")
        
        print("\n✅ Generation Successful!")
        print(f"Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"\n❌ Gemini API Error: {e}")
        return False

if __name__ == "__main__":
    if test_gemini():
        print("\n✅ Gemini AI is ready to be integrated!")
        sys.exit(0)
    else:
        print("\n⚠️ Gemini AI setup needs attention.")
        sys.exit(1)
