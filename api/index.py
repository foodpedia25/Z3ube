import sys
import traceback
from fastapi import FastAPI, Response

try:
    from api.main import app as main_app
    
    # Mount main app at /api to handle Vercel routing
    app = FastAPI()
    app.mount("/api", main_app)
    
except Exception as e:
    # Fallback app to show startup errors
    app = FastAPI()
    error_msg = f"Startup Error:\n{traceback.format_exc()}"
    
    @app.get("/{path:path}")
    async def catch_all(path: str):
        return Response(content=error_msg, media_type="text/plain", status_code=500)
