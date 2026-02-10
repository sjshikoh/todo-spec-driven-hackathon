# Phase III Specifications: AI-Powered Todo Chatbot

## Overview

Phase III adds an AI-powered conversational interface to the todo application using OpenAI Agents with Model Context Protocol (MCP). This phase is **100% additive** - no existing Phase II code is modified except for adding new router imports.

## Architecture Summary

```
User → Frontend (Vercel AI SDK)
  ↓
  FastAPI /ai/* endpoints
  ↓
  OpenAI Agent (with MCP tools)
  ↓
  MCP Server (embedded)
  ↓
  TaskService (Phase II - reused)
  ↓
  Database
```

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| MCP Server Mode | Embedded in FastAPI | Simpler deployment, easier auth |
| Agent SDK | OpenAI Agents SDK | Native MCP support, robust streaming |
| Streaming | Enabled (WebSocket) | Better UX, real-time feedback |
| Frontend SDK | Vercel AI SDK | Production-ready, excellent docs |
| Service Reuse | Direct TaskService calls | DRY principle, no duplication |

## Specification Files

1. **[1-mcp-server.spec.md](./1-mcp-server.spec.md)** - MCP server architecture and tool definitions
2. **[2-openai-agent.spec.md](./2-openai-agent.spec.md)** - OpenAI agent configuration and behavior
3. **[3-api-endpoints.spec.md](./3-api-endpoints.spec.md)** - REST API endpoints under `/ai/*`
4. **[4-frontend-integration.spec.md](./4-frontend-integration.spec.md)** - Chat UI with Vercel AI SDK
5. **[5-deployment.spec.md](./5-deployment.spec.md)** - Dependencies, Docker, environment config

## Implementation Checklist

### 1. Configuration & Dependencies
- [ ] Create `src/config.py`
- [ ] Update `requirements.txt` with Phase III dependencies
- [ ] Update `.env` with OpenAI and MCP config
- [ ] Update `frontend/package.json` with AI SDK

### 2. MCP Server
- [ ] Create `src/mcp/` directory structure
- [ ] Implement `src/mcp/server.py`
- [ ] Implement `src/mcp/tools/task_tools.py` with 6 tools
- [ ] Test MCP tools in isolation

### 3. OpenAI Agent
- [ ] Create `src/ai/` directory structure
- [ ] Implement `src/ai/prompts.py`
- [ ] Implement `src/ai/agent.py`
- [ ] Test agent locally

### 4. API Endpoints
- [ ] Create `src/interfaces/ai_routes.py`
- [ ] Implement POST `/ai/chat`
- [ ] Implement WebSocket `/ai/chat/stream`
- [ ] Implement GET `/ai/health`
- [ ] Update `src/main.py` to include router

### 5. Frontend
- [ ] Install frontend dependencies
- [ ] Create `frontend/components/ChatInterface.tsx`
- [ ] Create `frontend/components/ChatMessage.tsx`
- [ ] Create `frontend/app/chat/page.tsx`
- [ ] Create `frontend/app/api/ai/chat/route.ts` (proxy)
- [ ] Add navigation link

### 6. Testing
- [ ] Test Phase II endpoints still work
- [ ] Test AI chat endpoint
- [ ] Test natural language scenarios
- [ ] Test error handling
- [ ] Test streaming

### 7. Documentation
- [ ] Update README with Phase III features
- [ ] Document AI chat API
- [ ] Add deployment instructions

## MCP Tools

1. **create_task** - Create new task
2. **list_tasks** - List all tasks (with optional filter)
3. **get_task** - Get specific task by ID
4. **update_task** - Update task fields
5. **complete_task** - Mark task as done
6. **delete_task** - Delete task permanently

## New Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/ai/chat` | Send message to AI assistant |
| WebSocket | `/ai/chat/stream` | Streaming chat responses |
| GET | `/ai/health` | Health check for AI subsystem |

## Environment Variables (New)

```bash
# OpenAI
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0.7

# MCP
ENABLE_MCP=true

# AI Features
ENABLE_AI_CHAT=true
AI_STREAM_ENABLED=true
```

## Dependencies (New)

### Backend
```txt
openai==1.54.0
mcp==1.1.0
httpx==0.27.0
websockets==12.0
```

### Frontend
```json
{
  "@ai-sdk/openai": "^0.0.66",
  "@ai-sdk/react": "^0.0.62",
  "ai": "^3.4.0"
}
```

## Files to Create

```
specs/phase-3/                          ✓ Created
src/config.py                           → Implement
src/mcp/__init__.py                     → Implement
src/mcp/server.py                       → Implement
src/mcp/tools/__init__.py               → Implement
src/mcp/tools/task_tools.py             → Implement
src/ai/__init__.py                      → Implement
src/ai/agent.py                         → Implement
src/ai/prompts.py                       → Implement
src/interfaces/ai_routes.py             → Implement
frontend/components/ChatInterface.tsx   → Implement
frontend/components/ChatMessage.tsx     → Implement
frontend/app/chat/page.tsx              → Implement
frontend/app/api/ai/chat/route.ts       → Implement
frontend/app/api/ai/health/route.ts     → Implement
```

## Files to Modify (Minimal)

```
src/main.py                             → Add ai_router import and include
requirements.txt                        → Add Phase III dependencies
.env                                    → Add Phase III environment variables
frontend/package.json                   → Add AI SDK dependencies
```

## Files NOT to Touch (Phase II)

All existing Phase II files remain unchanged:
- `src/interfaces/task_routes.py`
- `src/interfaces/auth_routes.py`
- `src/services/task_service.py`
- `src/models/task.py`
- `src/models/user.py`
- `src/auth/temp_auth.py`

## Success Criteria

✅ All specifications written and approved
✅ MCP server provides 6 task tools
✅ OpenAI agent consumes MCP tools
✅ `/ai/chat` endpoint works
✅ Frontend chat UI functional
✅ Phase II endpoints still work
✅ JWT auth works for AI endpoints
✅ Streaming works via WebSocket
✅ Code is clean and reviewer-friendly
✅ Documentation updated

## Next Steps

1. ✅ Specifications complete
2. → Begin implementation following order in specifications
3. → Test each component in isolation
4. → Integration testing
5. → Documentation updates
6. → Deployment

## References

- [OpenAI Agents SDK](https://platform.openai.com/docs/assistants/overview)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Vercel AI SDK](https://sdk.vercel.ai/docs)
