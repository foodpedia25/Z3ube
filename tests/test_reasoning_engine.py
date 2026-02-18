
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.reasoning_engine import ReasoningEngine

async def test_reasoning_engine():
    print("🤖 Initializing Reasoning Engine...")
    engine = ReasoningEngine()
    
    # Test Synchronous Reason
    print("\n🧪 Testing Synchronous Reason (depth='quick')...")
    try:
        result = await engine.reason("Explain quantum entanglement briefly", depth="quick")
        print(f"✅ Conclusion: {result.conclusion[:100]}...")
        print(f"✅ Steps: {len(result.steps)}")
        print(f"✅ Confidence: {result.confidence}")
    except Exception as e:
        print(f"❌ Synchronous Reason Failed: {e}")
        import traceback
        traceback.print_exc()

    # Test Streaming Reason
    print("\n🧪 Testing Streaming Reason (depth='quick')...")
    try:
        async for chunk in engine.reason_stream("Explain quantum entanglement briefly", depth="quick"):
            print(f"chunk: {chunk.strip()}")
        print("\n✅ Streaming Completed")
    except Exception as e:
        print(f"❌ Streaming Reason Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_reasoning_engine())
