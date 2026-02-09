# API Endpoints Specification

## Overview

This specification defines new REST API endpoints under `/ai/*` for AI-powered chat interactions. These endpoints are **additive** - no existing Phase II endpoints are modified.

## Endpoint Summary

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| POST | `/ai/chat` | Send message to AI assistant | JWT |
| WebSocket | `/ai/chat/stream` | Streaming chat responses | JWT |
| GET | `/ai/health` | Health check for AI subsystem | None |

---

## 1. POST /ai/chat

### Purpose

Send a message to the AI assistant and receive a response.

### Request

**Method**: `POST`

**Headers**:
```
Content-Type: application/json
Authorization: Bearer <jwt_token>
```

**Body**:
```json
{
  "message": "string (required, 1-2000 chars)",
  "conversation_id": "string (optional, UUID)"
}
```

**Example**:
```json
{
  "message": "Show me my pending tasks"
}
```

### Response

**Status**: `200 OK`

**Body**:
```json
{
  "response": "string (agent's response)",
  "tool_calls": [
    {
      "name": "string (tool name)",
      "args": {
        "key": "value"
      },
      "result": {
        "key": "value"
      }
    }
  ],
  "conversation_id": "string (UUID)"
}
```

**Example**:
```json
{
  "response": "Here are your pending tasks:\n○ Buy groceries\n○ Write report\n○ Call dentist",
  "tool_calls": [
    {
      "name": "list_tasks",
      "args": {
        "completed": false
      },
      "result": [
        {
          "id": 1,
          "title": "Buy groceries",
          "description": "",
          "completed": false,
          "created_at": "2026-02-09T10:00:00Z",
          "updated_at": "2026-02-09T10:00:00Z"
        },
        {
          "id": 2,
          "title": "Write report",
          "description": "",
          "completed": false,
          "created_at": "2026-02-09T11:00:00Z",
          "updated_at": "2026-02-09T11:00:00Z"
        }
      ]
    }
  ],
  "conversation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

### Error Responses

#### 400 Bad Request
```json
{
  "detail": "Message is required"
}
```

#### 401 Unauthorized
```json
{
  "detail": "Invalid or missing authentication token"
}
```

#### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded. Please wait a moment."
}
```

#### 500 Internal Server Error
```json
{
  "detail": "AI service unavailable"
}
```

### Implementation

```python
# src/interfaces/ai_routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.auth.temp_auth import get_current_user_id_temp
from src.db.database import get_session
from src.ai.agent import create_todo_agent
from src.config import settings
from pydantic import BaseModel, Field

router = APIRouter(prefix="/ai", tags=["ai"])

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: str | None = None

class ToolCall(BaseModel):
    name: str
    args: dict
    result: dict

class ChatResponse(BaseModel):
    response: str
    tool_calls: list[ToolCall]
    conversation_id: str

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
            tool_calls=result["tool_calls"],
            conversation_id=result["conversation_id"]
        )

    except openai.RateLimitError:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please wait a moment.")
    except openai.AuthenticationError:
        raise HTTPException(status_code=500, detail="AI service configuration error")
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail="AI service unavailable")
```

---

## 2. WebSocket /ai/chat/stream

### Purpose

Establish WebSocket connection for streaming chat responses in real-time.

### Connection

**Protocol**: WebSocket

**URL**: `ws://localhost:8000/ai/chat/stream?token=<jwt_token>`

**Query Parameters**:
- `token`: JWT authentication token (required)

### Message Flow

#### 1. Client → Server (User Message)

```json
{
  "type": "message",
  "content": "Show me my tasks",
  "conversation_id": "optional-uuid"
}
```

#### 2. Server → Client (Streaming Chunks)

**Text Chunk**:
```json
{
  "type": "text",
  "content": "Here are "
}
```

```json
{
  "type": "text",
  "content": "your tasks:\n"
}
```

**Tool Call**:
```json
{
  "type": "tool_call",
  "tool_name": "list_tasks"
}
```

**Tool Result**:
```json
{
  "type": "tool_result",
  "tool_name": "list_tasks",
  "result": [
    {
      "id": 1,
      "title": "Buy groceries",
      "completed": false
    }
  ]
}
```

**End of Stream**:
```json
{
  "type": "done",
  "conversation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

### Error Messages

```json
{
  "type": "error",
  "message": "Failed to list tasks: Task not found",
  "code": 404
}
```

### Implementation

```python
# src/interfaces/ai_routes.py

from fastapi import WebSocket, WebSocketDisconnect
from jose import jwt, JWTError
import json

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

                # Send done signal
                await websocket.send_json({
                    "type": "done",
                    "conversation_id": conversation_id
                })

            except Exception as e:
                logger.error(f"Agent stream error: {e}")
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
        logger.error(f"WebSocket error: {e}")
        await websocket.close()

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
```

---

## 3. GET /ai/health

### Purpose

Health check endpoint for AI subsystem. Used to verify AI services are configured and operational.

### Request

**Method**: `GET`

**Headers**: None required (public endpoint)

### Response

**Status**: `200 OK`

**Body**:
```json
{
  "status": "ok" | "degraded" | "down",
  "mcp_enabled": true,
  "ai_chat_enabled": true,
  "model": "gpt-4-turbo-preview",
  "openai_configured": true
}
```

**Example (Healthy)**:
```json
{
  "status": "ok",
  "mcp_enabled": true,
  "ai_chat_enabled": true,
  "model": "gpt-4-turbo-preview",
  "openai_configured": true
}
```

**Example (Degraded)**:
```json
{
  "status": "degraded",
  "mcp_enabled": true,
  "ai_chat_enabled": false,
  "model": "gpt-4-turbo-preview",
  "openai_configured": false,
  "error": "OPENAI_API_KEY not set"
}
```

### Implementation

```python
# src/interfaces/ai_routes.py

from src.config import settings

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
```

---

## Router Registration

### File: `src/main.py` (Modification)

```python
# Existing imports
from fastapi import FastAPI
from src.interfaces.auth_routes import router as auth_router
from src.interfaces.task_routes import router as task_router

# NEW: Phase III import
from src.interfaces.ai_routes import router as ai_router
from src.config import settings

app = FastAPI()

# Existing routers (Phase II)
app.include_router(auth_router)
app.include_router(task_router)

# NEW: Phase III router
if settings.enable_ai_chat:
    app.include_router(ai_router)
    print("✓ AI chat endpoints enabled")
else:
    print("⊗ AI chat endpoints disabled")
```

**This is the ONLY modification to existing Phase II code.**

---

## Authentication

### JWT Verification

All AI endpoints (except `/ai/health`) require JWT authentication via the existing `get_current_user_id_temp` dependency.

**HTTP Endpoints**: Use `Authorization: Bearer <token>` header

**WebSocket Endpoints**: Use `token` query parameter

### Example cURL

```bash
# Get JWT token (Phase II endpoint)
TOKEN=$(curl -X POST http://localhost:8000/auth/sign-in \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}' \
  | jq -r '.access_token')

# Chat with AI
curl -X POST http://localhost:8000/ai/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Show me my tasks"}'

# Health check
curl http://localhost:8000/ai/health
```

---

## Error Handling

### Error Response Format

All endpoints use FastAPI's standard error format:

```json
{
  "detail": "Error message here"
}
```

### Status Codes

| Code | Meaning | When |
|------|---------|------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid input (missing message, etc.) |
| 401 | Unauthorized | Missing or invalid JWT token |
| 429 | Too Many Requests | OpenAI rate limit exceeded |
| 500 | Internal Server Error | Unexpected error |
| 503 | Service Unavailable | AI chat disabled in config |

---

## Rate Limiting

### OpenAI Rate Limits

OpenAI enforces rate limits on API usage. When exceeded:

**Response**:
```json
{
  "detail": "Rate limit exceeded. Please wait a moment."
}
```

**Status**: `429 Too Many Requests`

**Client Behavior**: Implement exponential backoff (wait 1s, 2s, 4s, etc.)

### Application-Level Rate Limiting (Future)

Phase III MVP does not implement application-level rate limiting. Future versions could add per-user rate limits using Redis.

---

## CORS Configuration

If frontend is served from different origin, add CORS middleware:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Phase III Decision**: CORS not configured (frontend served from same origin).

---

## Testing

### Manual Testing with cURL

```bash
# 1. Sign in and get token
TOKEN=$(curl -X POST http://localhost:8000/auth/sign-in \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}' \
  | jq -r '.access_token')

# 2. Create task via AI
curl -X POST http://localhost:8000/ai/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Add a task to buy groceries"}' | jq

# 3. List tasks via AI
curl -X POST http://localhost:8000/ai/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Show me my tasks"}' | jq

# 4. Complete task via AI
curl -X POST http://localhost:8000/ai/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Mark the groceries task as done"}' | jq

# 5. Health check
curl http://localhost:8000/ai/health | jq
```

### WebSocket Testing with `wscat`

```bash
# Install wscat
npm install -g wscat

# Get token first
TOKEN="your-jwt-token-here"

# Connect to WebSocket
wscat -c "ws://localhost:8000/ai/chat/stream?token=$TOKEN"

# Send message
> {"type":"message","content":"Show me my tasks"}

# Receive streaming responses
< {"type":"text","content":"Here are "}
< {"type":"text","content":"your tasks:\n"}
< {"type":"tool_call","tool_name":"list_tasks"}
< {"type":"tool_result","tool_name":"list_tasks","result":[...]}
< {"type":"done","conversation_id":"..."}
```

### Integration Tests

```python
# tests/interfaces/test_ai_routes.py

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_chat_endpoint_requires_auth():
    """Test that /ai/chat requires authentication"""
    response = client.post("/ai/chat", json={"message": "Hello"})
    assert response.status_code == 401

def test_chat_endpoint_success(auth_token):
    """Test successful chat interaction"""
    response = client.post(
        "/ai/chat",
        json={"message": "Add a task to buy groceries"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "tool_calls" in data
    assert len(data["tool_calls"]) > 0

def test_chat_endpoint_invalid_message(auth_token):
    """Test chat with invalid message"""
    response = client.post(
        "/ai/chat",
        json={"message": ""},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 422

def test_health_endpoint():
    """Test AI health check"""
    response = client.get("/ai/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model" in data
```

---

## Documentation

### OpenAPI/Swagger

FastAPI automatically generates OpenAPI documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

All AI endpoints will appear under the `ai` tag.

---

## Success Criteria

✅ POST /ai/chat endpoint handles natural language messages
✅ WebSocket /ai/chat/stream provides real-time streaming
✅ GET /ai/health returns correct status
✅ All endpoints require JWT authentication (except health)
✅ Error handling returns appropriate status codes
✅ Integration tests pass
✅ OpenAPI documentation is accurate
✅ No modifications to Phase II endpoints
