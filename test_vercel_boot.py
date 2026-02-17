import sys
import os
from unittest.mock import MagicMock

# 1. Simulate Missing ML Dependencies
# Remove them from sys.modules if present
for module in ['sentence_transformers', 'sentence_transformers.SentenceTransformer', 'numpy', 'faiss', 'torch']:
    if module in sys.modules:
        del sys.modules[module]

# Mock them to simulate missing modules
for module in ['sentence_transformers', 'numpy', 'faiss', 'torch']:
    sys.modules[module] = None  # Verify if None works for triggering ImportError or use a dummy


print("🔒 Simulated Vercel Environment (No Heavy ML Libs)")

# 2. Add root to path (mimic Vercel behavior)
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    print("🚀 Attempting to import api.main...")
    from api.main import app
    print("✅ api.main imported successfully!")
    print(f"App title: {app.title}")
    
    # Test Dependency Injection of Core Systems
    from core.self_learning import learning_system
    if learning_system.embedding_model is None:
        print("✅ Self-learning correctly initialized without embedding model")
    else:
        print("❌ Error: Embedding model initialized despite missing deps!")

except ImportError as e:
    print(f"❌ Import Error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Runtime Error: {e}")
    import traceback
    traceback.print_exc()
