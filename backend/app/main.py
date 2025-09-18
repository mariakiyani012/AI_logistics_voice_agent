# backend/app/main.py
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from .config import settings
from .database import db  # Missing import added
from .routers import agent, calls, webhook, llm_socket
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Voice Agent API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "AI Voice Agent API"}

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/test-db")
async def test_database():
    """Test database connection"""
    try:
        connection_status = await db.test_connection()
        if connection_status:
            # Try to insert a test agent to verify write access
            test_agent = await db.insert_test_agent()
            if test_agent:
                return {
                    "status": "connected",
                    "message": "Database connection and operations successful",
                    "test_agent_id": test_agent["id"]
                }
            else:
                return {
                    "status": "connected",
                    "message": "Database connected but write test failed"
                }
        else:
            return {"status": "failed", "message": "Database connection failed"}
    except Exception as e:
        logger.error(f"Database test error: {str(e)}")
        return {"status": "error", "message": str(e)}

# Include routers
app.include_router(agent.router, prefix="/api")
app.include_router(calls.router, prefix="/api")
app.include_router(webhook.router)  
app.include_router(llm_socket.router) 

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)