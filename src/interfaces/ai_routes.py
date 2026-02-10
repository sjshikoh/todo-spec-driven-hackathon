"""
AI chat API endpoints for Phase III.
Provides natural language interface to task management.
"""

import json
import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlmodel import Session
from pydantic import BaseModel, Field
from jose import jwt, JWTError

from src.auth.temp_auth import get_current_user_id_temp
from src.db.database import get_session
from src.ai.agent import create_todo_agent
from src.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])


# Request/Response Models

class ChatRequest(BaseModel):
    """Request body for chat endpoint"""
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID")


class ToolCall(BaseModel):
    """Tool call information"""
    name: str
    args: dict
    result: dict


class ChatResponse(BaseModel):
    """Response from chat endpoint"""
    response: str
    tool_calls: List[ToolCall]
    conversation_id: str


# Endpoints

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id_temp),
    session: Session = Depends(get_session)
):
    """
    Chat with AI assistant about tasks.

    The assistant can help you:
    - Create new tasks
    - List your tasks
    - Update task details
    - Mark tasks as completed
    - Delete tasks

    All operations respect your authentication and only affect your tasks.
    """
    if not settings.enable_ai_chat:
        raise HTTPException(status_code=503, detail="AI chat is disabled")

    if not settings.openai_api_key:
        raise HTTPException(status_code=503, detail="OpenAI API key not configured")

    try:
        # Create agent for this user
        agent = await create_todo_agent(user_id, session)

        # Run agent with user message
        result = await agent.run(
            message=request.message,
            conversation_id=request.conversation_id
        )

        return ChatResponse(
            response=result["response"],
            tool_calls=[
                ToolCall(name=tc["name"], args=tc["args"], result=tc["result"])
                for tc in result["tool_calls"]
            ],
            conversation_id=result["conversation_id"]
        )

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="AI service error")


@router.websocket("/chat/stream")
async def chat_stream(
    websocket: WebSocket,
    token: str,
    session: Session = Depends(get_session)
):
    """
    Streaming chat endpoint for real-time AI responses.

    Query parameter:
    - token: JWT authentication token

    Messages are streamed as JSON objects with 'type' field:
    - type: "text" - Text content chunk
    - type: "tool_call" - Tool execution started
    - type: "tool_result" - Tool execution completed
    - type: "done" - Stream finished
    - type: "error" - Error occurred
    """
    await websocket.accept()

    try:
        # Verify JWT token from query parameter
        user_id = verify_token_from_query(token)

        # Create agent for this user
        agent = await create_todo_agent(user_id, session)

        # Listen for messages
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            message = data.get("content", "")
            conversation_id = data.get("conversation_id")

            if not message:
                await websocket.send_json({
                    "type": "error",
                    "message": "Message is required",
                    "code": 400
                })
                continue

            # Stream agent response
            try:
                async for chunk in agent.stream(message, conversation_id):
                    await websocket.send_json(chunk)

            except Exception as e:
                logger.error(f"Agent stream error: {e}", exc_info=True)
                await websocket.send_json({
                    "type": "error",
                    "message": "AI service error",
                    "code": 500
                })

    except JWTError:
        await websocket.send_json({
            "type": "error",
            "message": "Invalid authentication token",
            "code": 401
        })
        await websocket.close()

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")

    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        await websocket.close()


@router.get("/health")
async def ai_health():
    """
    Health check for AI subsystem.

    Returns status information about AI service configuration.
    This endpoint does not require authentication.
    """
    openai_configured = bool(settings.openai_api_key)

    status = "ok"
    error = None

    if not openai_configured:
        status = "degraded"
        error = "OPENAI_API_KEY not set"
    elif not settings.enable_ai_chat:
        status = "degraded"
        error = "AI chat is disabled"

    return {
        "status": status,
        "mcp_enabled": settings.enable_mcp,
        "ai_chat_enabled": settings.enable_ai_chat,
        "model": settings.openai_model,
        "openai_configured": openai_configured,
        **({"error": error} if error else {})
    }


# Helper Functions

def verify_token_from_query(token: str) -> str:
    """
    Verify JWT token and extract user_id.

    Args:
        token: JWT token from query parameter

    Returns:
        user_id (str)

    Raises:
        JWTError: If token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise JWTError("User ID not found in token")
        return user_id
    except JWTError as e:
        logger.error(f"JWT verification failed: {e}")
        raise
