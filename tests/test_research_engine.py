
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.research_engine import ResearchEngine

async def test_research_engine():
    print("🤖 Initializing Research Engine...")
    engine = ResearchEngine()
    
    print("\n🧪 Testing Research (depth='quick')...")
    try:
        # Mocking or using simple topic
        result = await engine.conduct_research("Latest AI trends 2025", depth="quick", max_sources=2)
        print(f"✅ Topic: {result.topic}")
        print(f"✅ Summary: {result.summary[:100]}...")
        print(f"✅ Key Findings: {len(result.key_findings)}")
        print(f"✅ Sources: {len(result.sources)}")
        
        await engine.close()
    except Exception as e:
        print(f"❌ Research Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_research_engine())
