# Phase III Quick Start Guide

## Prerequisites

- Phase II implementation complete and working
- OpenAI API key (get one at https://platform.openai.com/api-keys)
- Python 3.10+ with pip
- Node.js 18+ with npm (for frontend)

## Backend Setup (5 minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Edit `.env` and add your OpenAI API key:

```bash
# Add this line with your actual key
OPENAI_API_KEY=sk-proj-your-key-here
```

The following are already configured:
```bash
OPENAI_MODEL=gpt-4-turbo-preview
ENABLE_MCP=true
ENABLE_AI_CHAT=true
```

### 3. Start Backend Server

```bash
python3 -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO - ✓ AI chat endpoints enabled
INFO - Model: gpt-4-turbo-preview
INFO - MCP: enabled
INFO - Streaming: enabled
```

### 4. Test AI Health

```bash
curl http://localhost:8000/ai/health | jq
```

Expected response:
```json
{
  "status": "ok",
  "mcp_enabled": true,
  "ai_chat_enabled": true,
  "model": "gpt-4-turbo-preview",
  "openai_configured": true
}
```

## Testing AI Chat (Without Frontend)

### 1. Get Authentication Token

```bash
# Sign in (replace with your test user credentials)
TOKEN=$(curl -X POST http://localhost:8000/auth/sign-in \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password"}' \
  | jq -r '.access_token')

echo "Token: $TOKEN"
```

### 2. Chat with AI

**Create a task:**
```bash
curl -X POST http://localhost:8000/ai/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Add a task to buy groceries"}' | jq
```

**List tasks:**
```bash
curl -X POST http://localhost:8000/ai/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Show me all my tasks"}' | jq
```

**Complete a task:**
```bash
curl -X POST http://localhost:8000/ai/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Mark the groceries task as done"}' | jq
```

**Delete a task:**
```bash
curl -X POST http://localhost:8000/ai/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Delete the groceries task"}' | jq
```

## Frontend Setup (Optional)

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create/edit `frontend/.env.local`:
```bash
BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_AI_CHAT_ENABLED=true
```

### 3. Create Frontend Components

Follow the specifications in `specs/phase-3/4-frontend-integration.spec.md` to create:
- `components/ChatInterface.tsx`
- `components/ChatMessage.tsx`
- `app/chat/page.tsx`
- `app/api/ai/chat/route.ts`
- `app/api/ai/health/route.ts`

### 4. Start Frontend

```bash
npm run dev
```

Visit: http://localhost:3000/chat

## Troubleshooting

### "AI chat is disabled"

Check `.env` file:
```bash
ENABLE_AI_CHAT=true
ENABLE_MCP=true
```

### "OPENAI_API_KEY not set"

Add your OpenAI API key to `.env`:
```bash
OPENAI_API_KEY=sk-proj-...
```

### "Invalid authentication token"

Get a fresh token:
```bash
TOKEN=$(curl -X POST http://localhost:8000/auth/sign-in \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"yourpassword"}' \
  | jq -r '.access_token')
```

### Import errors

Reinstall dependencies:
```bash
pip install -r requirements.txt
```

### "Tool execution error"

Check that Phase II endpoints still work:
```bash
curl http://localhost:8000/tasks \
  -H "Authorization: Bearer $TOKEN"
```

## API Endpoints Reference

### Phase III Endpoints

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/ai/chat` | JWT | Send message to AI assistant |
| WebSocket | `/ai/chat/stream` | JWT | Streaming chat responses |
| GET | `/ai/health` | None | AI subsystem health check |

### Phase II Endpoints (Still Working)

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/tasks` | JWT | List all tasks |
| POST | `/tasks` | JWT | Create task |
| GET | `/tasks/{id}` | JWT | Get task |
| PUT | `/tasks/{id}` | JWT | Update task |
| DELETE | `/tasks/{id}` | JWT | Delete task |
| POST | `/auth/sign-in` | None | Sign in |
| POST | `/auth/sign-up` | None | Sign up |

## Natural Language Examples

The AI assistant understands various phrasings:

**Creating tasks:**
- "Add a task to buy groceries"
- "Create a new task: finish the report"
- "Remind me to call the dentist"

**Listing tasks:**
- "Show me my tasks"
- "What do I need to do?"
- "List all pending tasks"

**Completing tasks:**
- "Mark the groceries task as done"
- "Complete task 1"
- "I finished the report"

**Deleting tasks:**
- "Delete the groceries task"
- "Remove task 2"
- "Get rid of the dentist reminder"

## Cost Estimation

**GPT-4 Turbo Pricing:**
- Input: ~$0.01 per 1K tokens
- Output: ~$0.03 per 1K tokens

**Average request:**
- ~200 input tokens + 400 output tokens = $0.014 per message
- 100 messages/day ≈ $1.40/day
- 1000 messages/day ≈ $14/day

**To reduce costs:**
1. Switch to `gpt-4o` (50% cheaper)
2. Implement caching
3. Add rate limiting

## Next Steps

1. ✓ Backend implementation complete
2. ⏳ Create frontend components
3. ⏳ Test end-to-end workflow
4. ⏳ Deploy to production
5. ⏳ Add conversation history (Phase IV)

## Support

- Backend specs: `specs/phase-3/`
- Implementation summary: `PHASE3_IMPLEMENTATION.md`
- Original plan: Check conversation history for full plan

## Success Checklist

Backend:
- [x] Configuration loaded
- [x] MCP tools working
- [x] OpenAI agent responding
- [x] API endpoints accessible
- [x] JWT auth working
- [x] Phase II endpoints unchanged

Frontend:
- [ ] AI SDK installed
- [ ] Chat component created
- [ ] API proxy routes created
- [ ] Navigation updated
- [ ] End-to-end chat working
