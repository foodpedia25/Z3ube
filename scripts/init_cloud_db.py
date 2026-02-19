import os
import sys
from sqlalchemy import create_engine, text

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.storage import Base

def init_db():
    print("🚀 Initializing Cloud Database...")
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ Error: DATABASE_URL environment variable not set.")
        print("   Please start this script with: DATABASE_URL=... python3 scripts/init_cloud_db.py")
        sys.exit(1)
        
    print(f"📡 Connecting to: {db_url.split('://')[0]}://***")
    
    try:
        engine = create_engine(db_url)
        
        # 1. Enable pgvector
        if 'postgresql' in db_url:
            print("   - Enabling pgvector extension...")
            with engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
        
        # 2. Create Tables
        print("   - Creating tables (interactions, patterns)...")
        Base.metadata.create_all(engine)
        
        print("\n✅ Database initialized successfully!")
        
    except Exception as e:
        print(f"\n❌ Initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_db()
