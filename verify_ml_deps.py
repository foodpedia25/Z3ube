
try:
    print("Attempting to import numpy...")
    import numpy as np
    print(f"NumPy version: {np.__version__}")
except Exception as e:
    print(f"Failed to import numpy: {e}")

try:
    print("\nAttempting to import sentence_transformers...")
    from sentence_transformers import SentenceTransformer
    print("Successfully imported SentenceTransformer")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Failed to import sentence_transformers: {e}")
