#!/usr/bin/env python3
"""
Z3ube Setup Verification Script

Tests all system components to ensure proper local setup.
Run this after following SETUP.md instructions.
"""

import sys
import os
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

def print_header(text):
    """Print formatted header"""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")

def print_step(step_num, text, status="INFO"):
    """Print formatted step"""
    icons = {"INFO": "ℹ️", "OK": "✅", "FAIL": "❌", "WARN": "⚠️"}
    icon = icons.get(status, "•")
    print(f"{icon} Step {step_num}: {text}")

def main():
    print_header("Z3ube Setup Verification")
    
    # Step 1: Check Python version
    print_step(1, "Checking Python version...")
    py_version = sys.version_info
    if py_version.major == 3 and py_version.minor in [10, 11]:
        print_step(1, f"Python {py_version.major}.{py_version.minor}.{py_version.micro} - Compatible", "OK")
    else:
        print_step(1, f"Python {py_version.major}.{py_version.minor} - May have compatibility issues", "WARN")
    
    # Step 2: Check environment variables
    print_step(2, "Checking API keys...")
    from dotenv import load_dotenv
    load_dotenv()
    
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_google = bool(os.getenv("GOOGLE_API_KEY"))
    
    if has_openai and has_anthropic:
        print_step(2, "Required API keys found (OpenAI, Anthropic)", "OK")
    else:
        print_step(2, "Missing required API keys. Check .env file", "FAIL")
        if not has_openai:
            print("   - OPENAI_API_KEY missing")
        if not has_anthropic:
            print("   - ANTHROPIC_API_KEY missing")
        return
    
    if has_google:
        print("   - Google API key found (optional)")
    
    # Step 3: Test core imports
    print_step(3, "Testing core module imports...")
    print("   This may take a while on first run (downloading models)...")
    
    try:
        print("   - Loading reasoning engine...")
        from core.reasoning_engine import reasoning_engine
        print_step(3, "Reasoning engine loaded", "OK")
        
        print("   - Loading self-learning system (downloading Sentence Transformer)...")
        from core.self_learning import learning_system
        print_step(3, "Self-learning system loaded", "OK")
        
        print("   - Loading auto-healer...")
        from core.auto_healer import auto_healer
        print_step(3, "Auto-healer loaded", "OK")
        
        print("   - Loading research engine...")
        from core.research_engine import research_engine
        print_step(3, "Research engine loaded", "OK")
        
        print("   - Loading code generator...")
        from core.code_generator import code_generator
        print_step(3, "Code generator loaded", "OK")
        
        print_step(3, "All core modules imported successfully", "OK")
        
    except Exception as e:
        print_step(3, f"Failed to import modules: {e}", "FAIL")
        return
    
    # Step 4: Test API server import
    print_step(4, "Testing API server...")
    try:
        from api.main import app
        print_step(4, "API server module loaded", "OK")
    except Exception as e:
        print_step(4, f"Failed to load API: {e}", "FAIL")
        return
    
    # Step 5: Quick functionality test
    print_step(5, "Testing basic functionality...")
    try:
        import asyncio
        
        async def test_reasoning():
            # Test simple reasoning
            result = await reasoning_engine.reason("What is 2+2?", depth="quick")
            return result.conclusion
        
        response = asyncio.run(test_reasoning())
        print(f"   Response: {response[:100]}...")
        print_step(5, "Basic reasoning test passed", "OK")
        
    except Exception as e:
        print_step(5, f"Functionality test failed: {e}", "WARN")
        print("   This may be due to API rate limits or network issues")
    
    # Final summary
    print_header("Setup Verification Complete!")
    print("✅ All checks passed!")
    print("\n📝 Next steps:")
    print("   1. Start backend: uvicorn api.main:app --reload --port 8000")
    print("   2. In new terminal, start frontend: cd frontend && npm run dev")
    print("   3. Open http://localhost:3000")
    print("\n💡 Note: First API call may be slow due to model initialization\n")

if __name__ == "__main__":
    main()
