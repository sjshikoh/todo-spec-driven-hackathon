# Stateless Chat API Specification

**Version:** 1.0.0
**Status:** Implemented
**Last Updated:** 2026-02-09

## Overview

This specification defines the stateless chat API for natural language task management. All endpoints are **stateless** - no conversation history is maintained server-side.

## Architecture

### Stateless Request/Response Model

```
Client → POST /ai/chat → Create Agent → Process → Return → Destroy Agent
```

**Key Principles:**
1. **No server-side sessions:** Each request is independent
2. **No conversation storage:** Messages not persisted
3. **Stateless authentication:** JWT token per request
4. **Idempotent operations:** Same input → Same output (via database state)

## Endpoints

### 1. POST /ai/chat

**Purpose:** Send a message to the AI assistant and receive a response

**Stateless Properties:**
- No conversation history loaded
- No session state maintained
- Fresh agent instance per request
- conversation_id is generated but not used (placeholder for future)

#### Request

**Method:** `POST`

**URL:** `/ai/chat`

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <jwt_token>
```

**Body:**
```json
{
  "message": "string (required, 1-2000 chars)",
  "conversation_id": "string (optional, unused)"
}
```

**Example:**
```json
{
  "message": "Show me my pending tasks"
}
```

**Validation:**
- `message`: Required, 1-2000 characters
- `conversation_id`: Optional, ignored (placeholder for Phase IV)

#### Response

**Status:** `200 OK`

**Body:**
```json
{
  "response": "string",
  "tool_calls": [
    {
      "name": "string",
      "args": {},
      "result": {}
    }
  ],
  "conversation_id": "string (UUID)"
}
```

**Example:**
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

**Response Fields:**
- `response`: Agent's natural language response
- `tool_calls`: Array of tools executed (name, args, result)
- `conversation_id`: UUID (currently unused, for future conversation persistence)

#### Implementation

```python
@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id_temp),
    session: Session = Depends(get_session)
):
    """
    Stateless chat endpoint.

    Each request:
    1. Creates fresh agent instance
    2. Processes single message (no history)
    3. Returns response
    4. Destroys agent instance
    """
    # 1. Create agent (stateless)
    agent = await create_todo_agent(user_id, session)

    # 2. Process message (no conversation history loaded)
    result = await agent.run(
        message=request.message,
        conversation_id=request.conversation_id  # Ignored
    )

    # 3. Return response
    return ChatResponse(
        response=result["response"],
        tool_calls=[
            ToolCall(name=tc["name"], args=tc["args"], result=tc["result"])
            for tc in result["tool_calls"]
        ],
        conversation_id=result["conversation_id"]
    )
    # Agent instance destroyed here
```

#### Error Responses

**400 Bad Request:**
```json
{
  "detail": "Message is required"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Invalid or missing authentication token"
}
```

**429 Too Many Requests:**
```json
{
  "detail": "Rate limit exceeded. Please wait a moment."
}
```

**500 Internal Server Error:**
```json
{
  "detail": "AI service unavailable"
}
```

**503 Service Unavailable:**
```json
{
  "detail": "AI chat is disabled"
}
```

---

### 2. WebSocket /ai/chat/stream

**Purpose:** Streaming chat responses in real-time

**Stateless Properties:**
- No conversation history loaded
- Connection established per-message
- Each message processed independently

#### Connection

**Protocol:** WebSocket

**URL:** `ws://localhost:8000/ai/chat/stream?token=<jwt_token>`

**Query Parameters:**
- `token`: JWT authentication token (required)

**Authentication:**
```python
# Extract user_id from JWT token in query parameter
user_id = verify_token_from_query(token)
```

#### Message Flow

**1. Client → Server (User Message):**
```json
{
  "type": "message",
  "content": "Show me my tasks",
  "conversation_id": "optional-uuid"
}
```

**2. Server → Client (Streaming Chunks):**

**Text Chunk:**
```json
{
  "type": "text",
  "content": "Here are "
}
```

**Tool Call:**
```json
{
  "type": "tool_call",
  "tool_name": "list_tasks"
}
```

**Tool Result:**
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

**End of Stream:**
```json
{
  "type": "done",
  "conversation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

**Error:**
```json
{
  "type": "error",
  "message": "Failed to list tasks: Database error",
  "code": 500
}
```

#### Implementation

```python
@router.websocket("/chat/stream")
async def chat_stream(
    websocket: WebSocket,
    token: str,
    session: Session = Depends(get_session)
):
    """
    Stateless streaming chat endpoint.

    Each message:
    1. Creates fresh agent instance
    2. Streams response chunks
    3. Destroys agent instance
    """
    await websocket.accept()

    try:
        # Verify JWT
        user_id = verify_token_from_query(token)

        # Create agent (stateless)
        agent = await create_todo_agent(user_id, session)

        # Listen for messages
        while True:
            # Receive message
            data = await websocket.receive_json()
            message = data.get("content", "")

            # Stream response (no history)
            async for chunk in agent.stream(message):
                await websocket.send_json(chunk)

            # Agent processes one message, then waits for next
            # No conversation state maintained

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
```

**Stateless Behavior:**
- Each message processed independently
- No context from previous messages
- Connection stays open, but no state accumulated

---

### 3. GET /ai/health

**Purpose:** Health check for AI subsystem

**Stateless Properties:**
- No authentication required
- No state dependencies
- Returns configuration status only

#### Request

**Method:** `GET`

**URL:** `/ai/health`

**Headers:** None required

#### Response

**Status:** `200 OK`

**Body:**
```json
{
  "status": "ok" | "degraded" | "down",
  "mcp_enabled": true,
  "ai_chat_enabled": true,
  "model": "gpt-4-turbo-preview",
  "openai_configured": true
}
```

**Status Values:**
- `ok`: All systems operational
- `degraded`: AI chat enabled but OpenAI key not configured
- `down`: AI chat disabled

**Example (Healthy):**
```json
{
  "status": "ok",
  "mcp_enabled": true,
  "ai_chat_enabled": true,
  "model": "gpt-4-turbo-preview",
  "openai_configured": true
}
```

**Example (Degraded):**
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

#### Implementation

```python
@router.get("/health")
async def ai_health():
    """
    Stateless health check.
    No database queries, no state dependencies.
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

## Authentication

### JWT Token Verification

**HTTP Endpoints:**
```python
# Extract from Authorization header
token = request.headers.get("Authorization").replace("Bearer ", "")
user_id = verify_jwt(token)
```

**WebSocket Endpoints:**
```python
# Extract from query parameter
token = query_params.get("token")
user_id = verify_token_from_query(token)
```

**Token Verification:**
```python
def verify_token_from_query(token: str) -> str:
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

**Stateless Authentication:**
- No session tokens
- No server-side session storage
- JWT validated per request

---

## Request/Response Models

### Pydantic Schemas

**ChatRequest:**
```python
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None  # Unused (placeholder)
```

**ChatResponse:**
```python
class ChatResponse(BaseModel):
    response: str
    tool_calls: List[ToolCall]
    conversation_id: str
```

**ToolCall:**
```python
class ToolCall(BaseModel):
    name: str
    args: dict
    result: dict
```

---

## Stateless Design Details

### No Conversation History

**Current Behavior:**
```python
# Request 1
POST /ai/chat
{"message": "Add a task to buy groceries"}
# Agent processes with no history

# Request 2
POST /ai/chat
{"message": "Mark it as done"}
# Agent processes with no history
# Cannot reference "it" from previous request
```

**User Experience:**
- Users must be explicit in each request
- Cannot use pronouns referencing previous messages
- Each request is self-contained

**Example Conversation:**
```
❌ Cannot do:
User: "Show my tasks"
Response: [lists tasks]
User: "Mark the first one as done"
Response: "I need more context. Which task?"

✓ Can do:
User: "Show my tasks and mark task 1 as done"
Response: [executes both in one request]
```

### No Server-Side Sessions

**No Session Storage:**
- No Redis/Memcached sessions
- No in-memory session cache
- No session cookies

**Benefits:**
- Horizontally scalable
- No session affinity needed
- Simpler infrastructure

**Trade-offs:**
- Less natural conversations
- User must repeat context

### conversation_id Field

**Current Status:** Placeholder

**Purpose:** Reserved for future conversation persistence (Phase IV)

**Current Behavior:**
- Generated as UUID per request
- Returned in response
- Not stored anywhere
- Not used by agent

**Future Use:**
```python
# Phase IV: Load conversation history
conversation = db.get_conversation(conversation_id)
messages = conversation.messages
agent = TodoAgent(user_id, session, history=messages)
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | When |
|------|---------|------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid input (missing message, etc.) |
| 401 | Unauthorized | Missing or invalid JWT token |
| 429 | Too Many Requests | OpenAI rate limit exceeded |
| 500 | Internal Server Error | Unexpected error |
| 503 | Service Unavailable | AI chat disabled in config |

### Error Response Format

**Standard Format:**
```json
{
  "detail": "Error message here"
}
```

**Examples:**
```json
{"detail": "Message is required"}
{"detail": "Invalid or missing authentication token"}
{"detail": "Rate limit exceeded. Please wait a moment."}
{"detail": "AI service unavailable"}
```

### Error Handling Flow

```python
try:
    agent = await create_todo_agent(user_id, session)
    result = await agent.run(message=request.message)
    return ChatResponse(...)

except openai.RateLimitError:
    raise HTTPException(status_code=429, detail="Rate limit exceeded")

except openai.AuthenticationError:
    raise HTTPException(status_code=500, detail="AI service configuration error")

except Exception as e:
    logger.error(f"Chat endpoint error: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="AI service error")
```

---

## Rate Limiting

### OpenAI Rate Limits

**GPT-4 Turbo Limits:**
- 10,000 requests per minute (RPM)
- 2,000,000 tokens per minute (TPM)

**Handling:**
```python
except openai.RateLimitError:
    raise HTTPException(
        status_code=429,
        detail="Rate limit exceeded. Please wait a moment."
    )
```

**Client Behavior:**
- Implement exponential backoff
- Retry after delay (1s, 2s, 4s, etc.)

### Application-Level Rate Limiting

**Future Enhancement (Phase IV):**
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@router.post("/chat")
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def chat(...):
    pass
```

---

## Testing

### Manual Testing

**Test Stateless Behavior:**
```bash
# Get token
TOKEN=$(curl -X POST http://localhost:8000/auth/sign-in \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password"}' \
  | jq -r '.access_token')

# Request 1: Create task
curl -X POST http://localhost:8000/ai/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Add a task to buy groceries"}' | jq

# Request 2: Reference previous (should fail context)
curl -X POST http://localhost:8000/ai/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Mark it as done"}' | jq
# Expected: Agent asks for clarification (no context)
```

**Test Health Endpoint:**
```bash
curl http://localhost:8000/ai/health | jq
```

### Integration Tests

```python
def test_chat_endpoint_stateless(client, auth_token):
    """Test that chat endpoint is stateless"""
    # Request 1
    response1 = client.post(
        "/ai/chat",
        json={"message": "Add a task to buy groceries"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response1.status_code == 200

    # Request 2 (no context from request 1)
    response2 = client.post(
        "/ai/chat",
        json={"message": "Mark it as done"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    # Should ask for clarification
    assert "which" in response2.json()["response"].lower()
```

---

## Performance

### Latency Targets

**Non-Streaming:**
- Total response time: < 2 seconds
- Agent creation: < 10ms
- Tool execution: < 100ms per tool
- OpenAI API: ~1-1.5 seconds

**Streaming:**
- First token: < 500ms
- Token streaming: ~50 tokens/second
- Total time: ~1-2 seconds

### Scalability

**Stateless Benefits:**
- No session affinity required
- Horizontal scaling possible
- Load balancer can route freely
- No shared state to synchronize

**Bottlenecks:**
- OpenAI API rate limits
- Database connections
- Network latency

---

## Security

### Input Validation

**Message Length:**
```python
message: str = Field(..., min_length=1, max_length=2000)
```

**JWT Validation:**
```python
user_id = verify_jwt(token)
# Raises JWTError if invalid
```

**SQL Injection:**
- Protected by SQLAlchemy ORM
- Parameterized queries
- No raw SQL

### Authorization

**User Isolation:**
- All tools bound to user_id
- Database queries include `WHERE user_id = ?`
- No way to access other users' data

**Token Validation:**
- JWT verified per request
- Expired tokens rejected
- Invalid signatures rejected

---

## CORS Configuration

**Current:** Not configured (frontend on same origin)

**If Needed:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Migration to Stateful (Phase IV)

### Future Conversation Persistence

**Changes Needed:**
1. Add conversation storage (see `specs/conversation-models.md`)
2. Load conversation history in agent
3. Use conversation_id to retrieve history
4. Store new messages after response

**Backward Compatibility:**
- Keep stateless mode as default
- Add `enable_conversation_history` flag
- conversation_id optional (generates if not provided)

---

## Success Criteria

- [x] POST /ai/chat endpoint implemented
- [x] WebSocket /ai/chat/stream endpoint implemented
- [x] GET /ai/health endpoint implemented
- [x] All endpoints are stateless
- [x] JWT authentication working
- [x] Error handling comprehensive
- [x] Request/response validation
- [x] No conversation history maintained
- [x] conversation_id generated but unused

## References

- **Implementation:** `src/interfaces/ai_routes.py`
- **Agent:** `specs/agent.md`
- **MCP Tools:** `specs/mcp-tools.md`
- **Future Persistence:** `specs/conversation-models.md`
