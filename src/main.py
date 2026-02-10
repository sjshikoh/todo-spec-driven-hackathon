#!/usr/bin/env python3
"""
Main entry point for the Todo Application.
Phase II: FastAPI server with JWT verification via JWKS.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.db.database import init_db
from src.interfaces.task_routes import router as task_router
from src.interfaces.auth_routes import router as auth_router
from src.interfaces.ai_routes import router as ai_router
from src.interfaces.chat_routes import router as chat_router
from src.config import settings
import logging


# ============ Configuration ============

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Todo API",
    description="REST API for Todo Application - Phase II & III",
    version="3.0.0"
)


# ============ CORS Middleware ============

# Get allowed origins from environment variable
allowed_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000")
# Split comma-separated string into list
origins_list = [origin.strip() for origin in allowed_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["Content-Length", "Content-Type"],
)


# ============ Root Endpoint ============

class MessageResponse(BaseModel):
    """Response model for root endpoint."""
    message: str


@app.get("/", response_model=MessageResponse)
async def root():
    """Root endpoint - API health check."""
    return MessageResponse(message="Todo API is running")


# ============ Auth Routes ============
app.include_router(auth_router)

# ============ Task Routes ============

app.include_router(task_router)

# ============ Chat Route ============
app.include_router(chat_router)

# ============ AI Routes (Phase III) ============

if settings.enable_ai_chat:
    app.include_router(ai_router)
    logger.info("✓ AI chat endpoints enabled")
else:
    logger.info("⊗ AI chat endpoints disabled")


# ============ Database Initialization ============

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    init_db()
    logger.info("Database initialized successfully")

    # Validate AI configuration
    warnings = settings.validate_ai_config()
    for warning in warnings:
        logger.warning(warning)

    # Log feature flags
    if settings.enable_ai_chat:
        logger.info(f"  Model: {settings.openai_model}")
        logger.info(f"  MCP: {'enabled' if settings.enable_mcp else 'disabled'}")
        logger.info(f"  Streaming: {'enabled' if settings.ai_stream_enabled else 'disabled'}")


# ============ Main Entry Point ============

def main():
    """Run the FastAPI server."""
    import uvicorn
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))

    logger.info(f"Starting Todo API server at http://{host}:{port}")
    logger.info("Endpoints:")
    logger.info("  - GET    /tasks          - List all tasks (requires JWT)")
    logger.info("  - GET    /tasks/{id}     - Get a task (requires JWT)")
    logger.info("  - POST   /tasks          - Create a task (requires JWT)")
    logger.info("  - PUT    /tasks/{id}     - Update a task (requires JWT)")
    logger.info("  - DELETE /tasks/{id}     - Delete a task (requires JWT)")
    logger.info("  - POST   /tasks/{id}/complete   - Mark complete (requires JWT)")
    logger.info("  - POST   /tasks/{id}/incomplete - Mark incomplete (requires JWT)")

    if settings.enable_ai_chat:
        logger.info("")
        logger.info("Phase III AI Endpoints:")
        logger.info("  - POST   /ai/chat        - Chat with AI assistant (requires JWT)")
        logger.info("  - WS     /ai/chat/stream - Streaming chat (requires JWT)")
        logger.info("  - GET    /ai/health      - AI health check")

    logger.info("")
    logger.info("Authentication: Bearer token from Better Auth (RS256, JWKS)")

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
