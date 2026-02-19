import os
from sqlalchemy import create_engine, text

db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("❌ DATABASE_URL is not set")
else:
    print(f"📡 Found DATABASE_URL: {db_url.split('://')[0]}://***")
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
