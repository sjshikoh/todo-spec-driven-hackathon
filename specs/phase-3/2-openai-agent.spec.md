# OpenAI Agent Specification

## Overview

The OpenAI Agent acts as the natural language interface for task management. It consumes MCP tools, handles conversation context, and translates user intent into tool calls.

## Architecture

### Agent Flow

```
User Message → OpenAI Agent → Analyze Intent → Select MCP Tools → Execute Tools → Format Response → Return
```

### Key Components

1. **OpenAI Client**: API connection to OpenAI
2. **Agent Configuration**: Model, temperature, instructions
3. **MCP Integration**: Tool discovery and execution
4. **Context Management**: Conversation history (handled by SDK)
5. **Response Formatting**: Natural language output

---

## Agent Configuration

### Model Selection

**Primary Model**: `gpt-4-turbo-preview`

**Rationale**:
- Excellent tool-calling performance
- Handles complex multi-step reasoning
- Good balance of cost vs capability
- Supports MCP tool schemas

**Alternative Models**:
- `gpt-4o` - Faster, lower cost (recommended for production)
- `gpt-3.5-turbo` - Budget option (may struggle with complex queries)

### Parameters

```python
{
    "model": "gpt-4-turbo-preview",
    "temperature": 0.7,  # Balanced creativity
    "max_tokens": 4096,  # Generous response length
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}
```

**Temperature Rationale**:
- `0.7` provides natural conversational tone
- Not too random (0.9+) - task management needs accuracy
- Not too deterministic (0.2-) - responses shouldn't feel robotic

---

## System Prompt

### Prompt Design

```markdown
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

### Prompt File: `src/ai/prompts.py`

```python
SYSTEM_PROMPT = """You are a helpful task management assistant for a todo application.

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
"""
```

---

## Implementation

### File: `src/ai/agent.py`

```python
from openai import OpenAI
from sqlalchemy.orm import Session
from src.mcp.server import create_mcp_server
from src.ai.prompts import SYSTEM_PROMPT
from src.config import settings

class TodoAgent:
    """
    OpenAI agent with MCP tools for task management.

    Creates a per-user agent instance with MCP tools bound to user context.
    """

    def __init__(self, user_id: str, session: Session):
        self.user_id = user_id
        self.session = session
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.mcp_server = create_mcp_server(user_id, session)

    def get_tools(self) -> list[dict]:
        """Get MCP tools in OpenAI function format"""
        tools = []
        for tool in self.mcp_server.list_tools():
            tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema
                }
            })
        return tools

    async def run(self, message: str, conversation_id: str | None = None) -> dict:
        """
        Run agent with a single message.

        Args:
            message: User's message
            conversation_id: Optional conversation ID for context (future)

        Returns:
            {
                "response": "Agent's text response",
                "tool_calls": [{"name": "create_task", "args": {...}}],
                "conversation_id": "abc123"
            }
        """
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ]

        # Initial completion with tools
        response = self.client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            tools=self.get_tools(),
            temperature=settings.openai_temperature,
            max_tokens=settings.openai_max_tokens
        )

        assistant_message = response.choices[0].message
        tool_calls = []

        # If agent wants to call tools
        if assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                # Execute tool via MCP server
                tool_result = await self.mcp_server.call_tool(tool_name, tool_args)

                tool_calls.append({
                    "name": tool_name,
                    "args": tool_args,
                    "result": tool_result
                })

                # Add tool result to messages
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call]
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                })

            # Get final response after tool execution
            final_response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens
            )

            final_message = final_response.choices[0].message.content
        else:
            final_message = assistant_message.content

        return {
            "response": final_message,
            "tool_calls": tool_calls,
            "conversation_id": conversation_id or self._generate_conversation_id()
        }

    async def stream(self, message: str, conversation_id: str | None = None):
        """
        Stream agent responses token-by-token.

        Yields:
            {
                "type": "text" | "tool_call" | "tool_result",
                "content": "...",
                "tool_name": "..." (if type=tool_call)
            }
        """
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ]

        stream = self.client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            tools=self.get_tools(),
            temperature=settings.openai_temperature,
            max_tokens=settings.openai_max_tokens,
            stream=True
        )

        tool_calls_buffer = []

        for chunk in stream:
            delta = chunk.choices[0].delta

            # Text content
            if delta.content:
                yield {
                    "type": "text",
                    "content": delta.content
                }

            # Tool calls
            if delta.tool_calls:
                for tool_call in delta.tool_calls:
                    if tool_call.function.name:
                        yield {
                            "type": "tool_call",
                            "tool_name": tool_call.function.name
                        }
                    tool_calls_buffer.append(tool_call)

        # Execute tools if any
        if tool_calls_buffer:
            for tool_call in tool_calls_buffer:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                tool_result = await self.mcp_server.call_tool(tool_name, tool_args)

                yield {
                    "type": "tool_result",
                    "tool_name": tool_name,
                    "result": tool_result
                }

    def _generate_conversation_id(self) -> str:
        """Generate unique conversation ID"""
        import uuid
        return str(uuid.uuid4())


async def create_todo_agent(user_id: str, session: Session) -> TodoAgent:
    """
    Factory function to create TodoAgent instance.

    Args:
        user_id: Authenticated user ID
        session: Database session

    Returns:
        Configured TodoAgent instance
    """
    return TodoAgent(user_id, session)
```

---

## Tool Execution Flow

### Single-Turn Execution

```
1. User: "Add a task to buy groceries"
2. Agent analyzes intent → Needs create_task
3. Agent calls create_task(title="Buy groceries")
4. MCP server executes → Returns task object
5. Agent formats response → "I've created the task 'Buy groceries' ✓"
6. Return to user
```

### Multi-Turn Execution

```
1. User: "Show me my tasks and mark the first one as done"
2. Agent analyzes → Needs list_tasks + complete_task
3. Agent calls list_tasks() → Gets [task1, task2, task3]
4. Agent calls complete_task(task_id=task1.id)
5. Agent formats response → "Your tasks: ... I've marked 'Buy groceries' as completed ✓"
6. Return to user
```

---

## Context Management

### Conversation History (Future Enhancement)

For Phase III MVP, each request is **stateless**. Future versions can add:

```python
class ConversationStore:
    """Store conversation history for context"""

    def get_messages(self, conversation_id: str) -> list[dict]:
        """Retrieve message history"""
        pass

    def add_message(self, conversation_id: str, role: str, content: str):
        """Add message to history"""
        pass
```

**Phase III Decision**: Stateless for simplicity. Agent treats each message independently.

---

## Error Handling

### Tool Execution Errors

```python
try:
    tool_result = await self.mcp_server.call_tool(tool_name, tool_args)
except MCPError as e:
    # MCP tool returned error
    yield {
        "type": "error",
        "message": f"Failed to {tool_name}: {e.message}",
        "code": e.code
    }
except Exception as e:
    # Unexpected error
    logger.error(f"Agent tool execution failed: {e}")
    yield {
        "type": "error",
        "message": "Something went wrong. Please try again.",
        "code": 500
    }
```

### OpenAI API Errors

```python
try:
    response = self.client.chat.completions.create(...)
except openai.RateLimitError:
    raise AgentError(429, "Rate limit exceeded. Please wait a moment.")
except openai.AuthenticationError:
    raise AgentError(500, "OpenAI API configuration error")
except Exception as e:
    logger.error(f"OpenAI API error: {e}")
    raise AgentError(500, "AI service unavailable")
```

---

## Testing Strategy

### Unit Tests

```python
# tests/ai/test_agent.py

@pytest.mark.asyncio
async def test_agent_create_task():
    """Test agent creates task from natural language"""
    agent = TodoAgent(user_id="user1", session=session)

    result = await agent.run("Add a task to buy groceries")

    assert "created" in result["response"].lower()
    assert len(result["tool_calls"]) == 1
    assert result["tool_calls"][0]["name"] == "create_task"
    assert result["tool_calls"][0]["args"]["title"] == "Buy groceries"

@pytest.mark.asyncio
async def test_agent_list_tasks():
    """Test agent lists tasks"""
    agent = TodoAgent(user_id="user1", session=session)

    result = await agent.run("Show me my tasks")

    assert len(result["tool_calls"]) == 1
    assert result["tool_calls"][0]["name"] == "list_tasks"

@pytest.mark.asyncio
async def test_agent_handles_ambiguity():
    """Test agent asks for clarification"""
    agent = TodoAgent(user_id="user1", session=session)

    result = await agent.run("Mark it as done")

    # Should ask which task
    assert "which" in result["response"].lower()
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_agent_end_to_end():
    """Test full conversation flow"""
    agent = TodoAgent(user_id="user1", session=session)

    # Create task
    result1 = await agent.run("Add a task to buy groceries")
    assert "created" in result1["response"].lower()

    # List tasks
    result2 = await agent.run("Show me my tasks")
    assert "groceries" in result2["response"].lower()

    # Complete task
    result3 = await agent.run("Mark the groceries task as done")
    assert "completed" in result3["response"].lower()
```

---

## Performance Considerations

### Latency Targets

- **Agent response time**: < 2 seconds (non-streaming)
- **First token time** (streaming): < 500ms
- **Tool execution**: < 100ms per tool

### Optimization Strategies

1. **Streaming**: Enable streaming to reduce perceived latency
2. **Model selection**: Use `gpt-4o` for faster responses
3. **Tool batching**: Execute multiple tools in parallel when possible
4. **Caching**: Cache MCP tool definitions (don't rebuild each time)

---

## Dependencies

```txt
openai==1.54.0  # OpenAI SDK with agents support
```

---

## Configuration

### Environment Variables

```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0.7
```

---

## Success Criteria

✅ Agent successfully interprets natural language task requests
✅ Agent calls correct MCP tools based on intent
✅ Agent handles multi-step requests (list + complete)
✅ Agent asks for clarification when ambiguous
✅ Agent formats responses in friendly, natural language
✅ Agent handles errors gracefully
✅ Streaming works correctly
✅ Unit tests pass for all agent behaviors
