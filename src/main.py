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


# ============ Configuration ============

app = FastAPI(
    title="Todo API",
    description="REST API for Todo Application - Phase II",
    version="1.0.0"
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


# ============ Database Initialization ============

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    init_db()
    print("Database initialized successfully")


# ============ Main Entry Point ============

def main():
    """Run the FastAPI server."""
    import uvicorn
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))

    print(f"Starting Todo API server at http://{host}:{port}")
    print("Endpoints:")
    print("  - GET    /tasks          - List all tasks (requires JWT)")
    print("  - GET    /tasks/{id}     - Get a task (requires JWT)")
    print("  - POST   /tasks          - Create a task (requires JWT)")
    print("  - PUT    /tasks/{id}     - Update a task (requires JWT)")
    print("  - DELETE /tasks/{id}     - Delete a task (requires JWT)")
    print("  - POST   /tasks/{id}/complete   - Mark complete (requires JWT)")
    print("  - POST   /tasks/{id}/incomplete - Mark incomplete (requires JWT)")
    print()
    print("Authentication: Bearer token from Better Auth (RS256, JWKS)")

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
