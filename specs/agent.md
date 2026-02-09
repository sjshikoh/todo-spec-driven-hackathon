# AI Agent Behavior Specification

**Version:** 1.0.0
**Status:** Implemented
**Last Updated:** 2026-02-09

## Overview

This specification defines the behavior of the OpenAI-powered AI agent for natural language task management. The agent is **stateless** per request, consuming MCP tools to perform task operations.

## Architecture

### Stateless Agent Design

```
Request → Create TodoAgent(user_id, session) → Process Message → Execute Tools → Return Response
```

**Key Principles:**
1. **No conversation history:** Each request is independent (stateless)
2. **Per-request instantiation:** Fresh agent instance per request
3. **Tool-based actions:** All operations via MCP tools
4. **Natural language understanding:** Interprets user intent

### Agent Lifecycle

```python
# Request arrives
async def chat(request, user_id, session):
    # 1. Create agent (stateless)
    agent = TodoAgent(user_id, session)

    # 2. Process single message (no history)
    result = await agent.run(message=request.message)

    # 3. Return response
    return result
    # Agent instance destroyed
```

## Agent Configuration

### Model Selection

**Primary Model:** `gpt-4-turbo-preview`

**Rationale:**
- Superior tool calling accuracy
- Handles complex multi-step reasoning
- Good balance of cost vs capability
- Supports 128K context (though not used in stateless mode)

**Alternative Models:**
- `gpt-4o` - Faster, 50% cheaper (recommended for production)
- `gpt-3.5-turbo` - Budget option (may struggle with complex queries)

### Parameters

```python
{
    "model": "gpt-4-turbo-preview",
    "temperature": 0.7,        # Balanced creativity
    "max_tokens": 4096,        # Generous response length
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}
```

**Temperature Rationale:**
- `0.7` provides natural conversational tone
- Not too deterministic (< 0.3) - responses feel robotic
- Not too random (> 0.9) - task management needs accuracy

## System Prompt

### Complete Prompt

```
You are a helpful task management assistant for a todo application.

## Your Role
You help users manage their tasks through natural language conversation. You can create, read, update, complete, and delete tasks.

## Available Tools
- **create_task**: Create a new task
- **list_tasks**: View all tasks or filter by completion status
- **get_task**: Get details of a specific task
- **update_task**: Modify task title, description, or completion status
- **complete_task**: Mark a task as done
- **delete_task**: Remove a task permanently

## Behavioral Guidelines

### Always Do:
- Be concise and friendly
- Confirm actions after completion (e.g., "I've created the task 'Buy groceries'")
- Ask for clarification if the request is ambiguous
- Use natural language in responses (avoid technical IDs)
- Format task lists clearly with status indicators

### Never Do:
- Mention internal tool names to users (say "I'll add that task" not "I'll call create_task")
- Expose task IDs unless necessary (say "your grocery task" not "task ID 42")
- Make assumptions about ambiguous requests (ask for clarification)
- Perform destructive actions (delete) without confirmation

## Response Formatting

When listing tasks, use this format:
```
Your tasks:
✓ Buy groceries (completed)
○ Write report (pending)
○ Call dentist (pending)
```

When confirming actions:
```
✓ Task created: "Buy groceries"
✓ Task completed: "Write report"
✓ Task deleted: "Call dentist"
```

## Handling Ambiguity

If a user says "mark it as done" but there are multiple tasks:
- List the tasks
- Ask which one they mean

If a user says "create a task" without details:
- Ask for the task title
- Optionally ask for description

## Error Handling

If a tool call fails:
- Explain the issue in simple terms
- Suggest next steps
- Don't expose technical error messages

## Examples

User: "Add a task to buy groceries"
You: "I've created the task 'Buy groceries' for you. ✓"

User: "What do I need to do today?"
You: "Here are your pending tasks:
○ Buy groceries
○ Finish project report
○ Call dentist for appointment"

User: "Mark the first one as done"
You: "I've marked 'Buy groceries' as completed. ✓"

User: "Delete the dentist task"
You: "Are you sure you want to delete 'Call dentist for appointment'? Just confirm and I'll remove it."
```

### Prompt Design Rationale

**Conciseness:**
- Users want quick responses
- Avoid verbose explanations
- Get to the point

**Friendliness:**
- Conversational tone (not robotic)
- Use emojis sparingly (✓, ○)
- Positive confirmation messages

**Natural Language:**
- Hide technical implementation details
- Use user's terminology
- Avoid jargon (don't say "executed create_task function")

**Ambiguity Handling:**
- Ask clarifying questions
- Don't guess user intent
- List options when multiple interpretations possible

## Message Processing

### Single-Turn Processing (Stateless)

```python
async def run(self, message: str, conversation_id: Optional[str] = None):
    """
    Process a single message with no conversation history.

    Args:
        message: User's message
        conversation_id: Ignored (for future use)

    Returns:
        {
            "response": str,
            "tool_calls": list,
            "conversation_id": str
        }
    """
    # 1. Build messages array (no history)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message}
    ]

    # 2. Send to OpenAI
    response = self.client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        tools=get_tools(),
        temperature=settings.openai_temperature
    )

    # 3. Execute any tool calls
    # 4. Get final response
    # 5. Return
```

**No Conversation History:**
- Each request starts fresh
- No context from previous messages
- Agent cannot reference past interactions

### Tool Execution Flow

**Single Tool Call:**
```
1. User: "Add a task to buy groceries"
2. Agent: Analyzes → Needs create_task tool
3. Agent: Calls create_task(title="Buy groceries")
4. Tools: Executes → Returns {"id": 1, "title": "Buy groceries", ...}
5. Agent: Formats → "I've created the task 'Buy groceries' ✓"
```

**Multiple Tool Calls:**
```
1. User: "Show me my tasks and mark the first one as done"
2. Agent: Analyzes → Needs list_tasks + complete_task
3. Agent: Calls list_tasks() → Gets [task1, task2, task3]
4. Agent: Calls complete_task(task_id=task1.id)
5. Agent: Formats → "Your tasks: ... I've marked 'Buy groceries' as completed ✓"
```

**No Tool Calls:**
```
1. User: "Hello"
2. Agent: No tools needed
3. Agent: Responds conversationally → "Hello! I'm here to help you manage your tasks..."
```

## Tool Call Handling

### Execution Loop

```python
# 1. Get initial response
response = openai.chat.completions.create(...)
assistant_message = response.choices[0].message

# 2. If tool calls present
if assistant_message.tool_calls:
    for tool_call in assistant_message.tool_calls:
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)

        # 3. Execute tool
        result = tools.execute_tool(tool_name, tool_args)

        # 4. Add result to messages
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result)
        })

    # 5. Get final response with tool results
    final_response = openai.chat.completions.create(...)
    return final_response.choices[0].message.content
```

### Tool Call Format

**From OpenAI:**
```json
{
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "create_task",
        "arguments": "{\"title\":\"Buy groceries\"}"
      }
    }
  ]
}
```

**To Tools:**
```python
tools.execute_tool(
    tool_name="create_task",
    arguments={"title": "Buy groceries"}
)
```

**From Tools:**
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "",
  "completed": false,
  "created_at": "2026-02-09T10:00:00Z",
  "updated_at": "2026-02-09T10:00:00Z"
}
```

## Error Handling

### Tool Execution Errors

**ValueError (User Error):**
```python
try:
    result = tools.execute_tool(tool_name, tool_args)
except ValueError as e:
    # Return error to agent for natural language explanation
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps({"error": str(e)})
    })
    # Agent will say: "I couldn't find that task. Could you check the task ID?"
```

**General Exception:**
```python
except Exception as e:
    logger.error(f"Tool execution failed: {e}")
    # Return generic error
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps({"error": "Something went wrong"})
    })
    # Agent will say: "I encountered an issue. Please try again."
```

### OpenAI API Errors

**Rate Limit:**
```python
try:
    response = openai.chat.completions.create(...)
except openai.RateLimitError:
    raise AgentError(429, "I'm experiencing high demand. Please try again in a moment.")
```

**Authentication:**
```python
except openai.AuthenticationError:
    raise AgentError(500, "AI service configuration error")
```

**Timeout:**
```python
except openai.APITimeoutError:
    raise AgentError(504, "The request took too long. Please try again.")
```

## Response Formatting

### Task List Formatting

**Agent Output:**
```
Your tasks:
✓ Buy groceries (completed)
○ Write report (pending)
○ Call dentist (pending)
```

**Implementation:**
Agent receives tool result and formats naturally using its language model capabilities.

### Confirmation Messages

**Create:**
```
✓ Task created: "Buy groceries"
```

**Update:**
```
✓ Task updated: "Buy groceries" → "Buy organic groceries"
```

**Complete:**
```
✓ Task completed: "Write report"
```

**Delete:**
```
✓ Task deleted: "Call dentist"
```

### Error Messages

**Not Found:**
```
I couldn't find that task. Could you check the task ID or description?
```

**Ambiguous:**
```
You have multiple tasks. Which one did you mean?
1. Buy groceries
2. Buy milk
```

**Permission Denied:**
```
That task doesn't belong to you or doesn't exist.
```

## Natural Language Understanding

### Intent Recognition

**Create Task:**
- "Add a task to X"
- "Create a new task: X"
- "Remind me to X"
- "I need to X"

**List Tasks:**
- "Show me my tasks"
- "What do I need to do?"
- "List my todos"
- "What's on my plate?"

**Complete Task:**
- "Mark X as done"
- "I finished X"
- "Complete the X task"
- "X is done"

**Delete Task:**
- "Delete X"
- "Remove X"
- "Get rid of X"
- "I don't need X anymore"

### Ambiguity Resolution

**Pronoun Resolution:**
```
User: "Show my tasks"
Agent: [lists tasks]
User: "Mark the first one as done"
Agent: [Cannot resolve - no history]
Response: "I need more context. Which task would you like to mark as done?"
```

**Multiple Matches:**
```
User: "Delete the grocery task"
Agent: [Calls list_tasks, finds multiple matches]
Response: "You have multiple grocery-related tasks:
1. Buy groceries
2. Buy organic groceries
Which one should I delete?"
```

## Streaming Support

### Streaming Implementation

```python
async def stream(self, message: str):
    """
    Stream agent responses token-by-token.

    Yields:
        {"type": "text", "content": "..."}
        {"type": "tool_call", "tool_name": "create_task"}
        {"type": "tool_result", "tool_name": "create_task", "result": {...}}
        {"type": "done", "conversation_id": "..."}
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message}
    ]

    stream = openai.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        tools=get_tools(),
        stream=True
    )

    for chunk in stream:
        delta = chunk.choices[0].delta

        # Stream text
        if delta.content:
            yield {"type": "text", "content": delta.content}

        # Stream tool calls
        if delta.tool_calls:
            # ... (see implementation)
```

### Streaming Benefits

**User Experience:**
- Real-time feedback
- Reduced perceived latency
- See agent "thinking"

**Technical:**
- First token time < 500ms
- Progressive rendering
- Early error detection

## Testing

### Test Cases

**Basic Commands:**
```python
async def test_create_task():
    agent = TodoAgent(user_id="user1", session=session)
    result = await agent.run("Add a task to buy groceries")

    assert "created" in result["response"].lower()
    assert len(result["tool_calls"]) == 1
    assert result["tool_calls"][0]["name"] == "create_task"
```

**Statelessness:**
```python
async def test_no_conversation_history():
    agent1 = TodoAgent(user_id="user1", session=session)
    await agent1.run("Add a task to buy groceries")

    # New instance cannot reference previous message
    agent2 = TodoAgent(user_id="user1", session=session)
    result = await agent2.run("Mark it as done")

    # Should ask for clarification (no context)
    assert "which" in result["response"].lower()
```

**Error Handling:**
```python
async def test_tool_error():
    agent = TodoAgent(user_id="user1", session=session)
    result = await agent.run("Get task 99999")

    assert "couldn't find" in result["response"].lower()
```

## Performance

### Latency Targets

**Non-Streaming:**
- Total response time: < 2 seconds
- Tool execution: < 100ms per tool
- OpenAI API: ~1-1.5 seconds

**Streaming:**
- First token: < 500ms
- Token streaming: ~50 tokens/second
- Tool execution: < 100ms per tool

### Optimization Strategies

**Model Selection:**
- Use `gpt-4o` for 50% faster responses
- Trade-off: Slightly lower accuracy

**Tool Definitions:**
- Cached at module level (not per-request)
- No dynamic generation

**Prompt Engineering:**
- Concise system prompt
- No unnecessary examples

## Cost Analysis

### Pricing (GPT-4 Turbo)

**Input:** ~$0.01 per 1K tokens
**Output:** ~$0.03 per 1K tokens

**Average Request:**
- System prompt: ~300 tokens
- User message: ~50 tokens
- Tool definitions: ~500 tokens
- Agent response: ~150 tokens
- **Total:** ~1000 tokens = ~$0.02 per request

**Daily Usage:**
- 100 requests/day = $2/day = $60/month
- 1000 requests/day = $20/day = $600/month

### Cost Reduction

**Switch to GPT-4o:**
- 50% cheaper
- Faster response times
- Slight accuracy trade-off

**Prompt Optimization:**
- Remove unnecessary examples
- Shorten system prompt
- Cache tool definitions

**Rate Limiting:**
- Limit requests per user
- Prevents abuse
- Predictable costs

## Integration with MCP Tools

### Tool Discovery

```python
def get_tools(self) -> list:
    """Get tool definitions for OpenAI"""
    return get_tool_definitions()  # From mcp.tools.task_tools
```

### Tool Execution

```python
# Agent receives tool call from OpenAI
tool_name = "create_task"
tool_args = {"title": "Buy groceries"}

# Execute via TaskTools
result = self.tools.execute_tool(tool_name, tool_args)

# Return result to OpenAI
messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,
    "content": json.dumps(result)
})
```

## Limitations (Stateless Design)

### No Conversation History

**Limitation:**
- Cannot reference previous messages
- Cannot build context over multiple turns
- Each request is independent

**Workaround:**
- User must be explicit in each request
- Agent asks for clarification
- Frontend could show recent interactions for user reference

**Example:**
```
❌ Cannot do:
User: "Show my tasks"
Agent: [lists tasks]
User: "Mark the first one as done"
Agent: [No context - which task?]

✓ Can do:
User: "Show my tasks and mark task 1 as done"
Agent: [Executes both in one request]
```

### No Multi-Turn Planning

**Limitation:**
- Cannot break complex tasks into steps
- Cannot ask follow-up questions naturally
- All information needed upfront

**Example:**
```
❌ Cannot do:
User: "Create a task"
Agent: "What should the task be?"
User: "Buy groceries"
[No memory of previous exchange]

✓ Can do:
User: "Create a task"
Agent: "What should the task be about?"
[User must provide full details in next message]
```

## Future Enhancements (Phase IV)

### Conversation Persistence

**Add conversation_id support:**
- Store messages in database
- Load history on request
- Maintain context across turns

**Benefits:**
- Natural multi-turn conversations
- Pronoun resolution
- Context awareness

### Conversation Models Specification

See `specs/conversation-models.md` for future conversation persistence design.

## Success Criteria

- [x] Agent processes natural language queries
- [x] Agent calls correct tools based on intent
- [x] Agent handles single-turn and multi-tool requests
- [x] Agent formats responses naturally
- [x] Agent handles errors gracefully
- [x] Agent is stateless (no conversation history)
- [x] Streaming support implemented
- [x] System prompt defined
- [x] Integration with MCP tools working

## References

- **Implementation:** `src/ai/agent.py`
- **System Prompt:** `src/ai/prompts.py`
- **MCP Tools:** `specs/mcp-tools.md`
- **API Endpoints:** `specs/chat-api.md`
