
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.code_generator import CodeGenerator

async def test_code_generator():
    print("🤖 Initializing Code Generator...")
    generator = CodeGenerator()
    
    # Test Python Generation
    print("\n🧪 Testing Python Code Generation...")
    try:
        result = await generator.generate_code(
            description="Write a function to calculate Fibonacci numbers",
            language="python",
            include_tests=True
        )
        print(f"✅ Language: {result.language}")
        print(f"✅ Code Length: {len(result.code)}")
        print(f"✅ Tests Generated: {result.tests is not None}")
        print(f"✅ Quality Score: {result.quality_score}")
    except Exception as e:
        print(f"❌ Python Generation Failed: {e}")
        import traceback
        traceback.print_exc()

    # Test Robotics Generation (ROS2)
    print("\n🧪 Testing ROS2 Code Generation...")
    try:
        result = await generator.generate_code(
            description="Create a ROS2 node that publishes camera data",
            language="ros2_python",
            include_tests=False
        )
        print(f"✅ Language: {result.language}")
        print(f"✅ Code Length: {len(result.code)}")
    except Exception as e:
        print(f"❌ ROS2 Generation Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_code_generator())
