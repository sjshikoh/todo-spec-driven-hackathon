# MCP Server Specification

## Overview

The Model Context Protocol (MCP) server provides standardized tools for task management operations. It acts as the bridge between the OpenAI agent and the existing Phase II task service layer.

## Architecture

### Design Pattern: Per-Request Instantiation

```
Request → JWT Auth → Extract user_id → Create MCP Server(user_id, session) → Register Tools → Use Tools → Destroy
```

**Key Design Decision**: MCP server is **not a singleton**. Each authenticated request creates a new MCP server instance with user context bound. This ensures proper user isolation and simplifies auth integration.

## MCP Tools

### 1. create_task

**Purpose**: Create a new task for the authenticated user

**Input Schema**:
```json
{
  "title": "string (required, 1-200 chars)",
  "description": "string (optional, max 2000 chars)"
}
```

**Output Schema**:
```json
{
  "id": "integer",
  "title": "string",
  "description": "string",
  "completed": false,
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime"
}
```

**Business Logic**:
- Validates title length (1-200 chars)
- Sets `completed=false` by default
- Associates task with authenticated user via bound `user_id`
- Calls `TaskService.create_task(user_id, title, description)`

**Error Cases**:
- Missing title → `400 Bad Request`
- Title too long → `400 Bad Request`
- Database error → `500 Internal Server Error`

---

### 2. list_tasks

**Purpose**: List all tasks for authenticated user with optional filtering

**Input Schema**:
```json
{
  "completed": "boolean | null (optional)"
}
```

**Output Schema**:
```json
[
  {
    "id": "integer",
    "title": "string",
    "description": "string",
    "completed": "boolean",
    "created_at": "ISO 8601 datetime",
    "updated_at": "ISO 8601 datetime"
  }
]
```

**Business Logic**:
- If `completed` is `null` or omitted → return all tasks
- If `completed=true` → return only completed tasks
- If `completed=false` → return only incomplete tasks
- Calls `TaskService.list_tasks(user_id, completed)`
- Returns empty array if no tasks found

**Error Cases**:
- Database error → `500 Internal Server Error`

---

### 3. get_task

**Purpose**: Retrieve a specific task by ID

**Input Schema**:
```json
{
  "task_id": "integer (required)"
}
```

**Output Schema**:
```json
{
  "id": "integer",
  "title": "string",
  "description": "string",
  "completed": "boolean",
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime"
}
```

**Business Logic**:
- Retrieves task by ID from database
- Verifies task belongs to authenticated user
- Calls `TaskService.get_task(user_id, task_id)`

**Error Cases**:
- Task not found → `404 Not Found`
- Task belongs to different user → `403 Forbidden`
- Database error → `500 Internal Server Error`

---

### 4. update_task

**Purpose**: Update task fields (title, description, completion status)

**Input Schema**:
```json
{
  "task_id": "integer (required)",
  "title": "string (optional, 1-200 chars)",
  "description": "string (optional, max 2000 chars)",
  "completed": "boolean (optional)"
}
```

**Output Schema**:
```json
{
  "id": "integer",
  "title": "string",
  "description": "string",
  "completed": "boolean",
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime"
}
```

**Business Logic**:
- At least one field (title, description, or completed) must be provided
- Only updates provided fields (partial update)
- Verifies task belongs to authenticated user
- Updates `updated_at` timestamp automatically
- Calls `TaskService.update_task(user_id, task_id, **updates)`

**Error Cases**:
- Task not found → `404 Not Found`
- Task belongs to different user → `403 Forbidden`
- No fields provided → `400 Bad Request`
- Title too long → `400 Bad Request`
- Database error → `500 Internal Server Error`

---

### 5. complete_task

**Purpose**: Convenience method to mark task as completed

**Input Schema**:
```json
{
  "task_id": "integer (required)"
}
```

**Output Schema**:
```json
{
  "id": "integer",
  "title": "string",
  "description": "string",
  "completed": true,
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime"
}
```

**Business Logic**:
- Wrapper around `update_task(task_id, completed=true)`
- Verifies task belongs to authenticated user
- Sets `completed=true`

**Error Cases**:
- Same as `update_task`

---

### 6. delete_task

**Purpose**: Delete a task permanently

**Input Schema**:
```json
{
  "task_id": "integer (required)"
}
```

**Output Schema**:
```json
{
  "success": true,
  "message": "Task deleted successfully",
  "task_id": "integer"
}
```

**Business Logic**:
- Verifies task belongs to authenticated user
- Permanently deletes task from database
- Calls `TaskService.delete_task(user_id, task_id)`

**Error Cases**:
- Task not found → `404 Not Found`
- Task belongs to different user → `403 Forbidden`
- Database error → `500 Internal Server Error`

---

## Implementation Structure

### File: `src/mcp/server.py`

```python
from mcp import Server
from sqlalchemy.orm import Session
from src.mcp.tools.task_tools import register_task_tools

def create_mcp_server(user_id: str, session: Session) -> Server:
    """
    Create MCP server instance with user context bound.

    Args:
        user_id: Authenticated user ID from JWT
        session: SQLAlchemy database session

    Returns:
        Configured MCP Server instance with task tools registered
    """
    server = Server("todo-mcp-server")

    # Register tools with user context
    register_task_tools(server, user_id, session)

    return server
```

### File: `src/mcp/tools/task_tools.py`

```python
from mcp import Server, Tool
from sqlalchemy.orm import Session
from src.services.task_service import TaskService

def register_task_tools(server: Server, user_id: str, session: Session):
    """
    Register all task management tools with the MCP server.

    Args:
        server: MCP Server instance
        user_id: Authenticated user ID (bound to all tools)
        session: Database session (bound to all tools)
    """

    task_service = TaskService(session)

    # Tool 1: create_task
    @server.tool(
        name="create_task",
        description="Create a new task for the user",
        input_schema={
            "type": "object",
            "properties": {
                "title": {"type": "string", "minLength": 1, "maxLength": 200},
                "description": {"type": "string", "maxLength": 2000}
            },
            "required": ["title"]
        }
    )
    async def create_task(title: str, description: str = ""):
        task = task_service.create_task(user_id, title, description)
        return task.to_dict()

    # Tool 2: list_tasks
    @server.tool(
        name="list_tasks",
        description="List all tasks for the user, optionally filtered by completion status",
        input_schema={
            "type": "object",
            "properties": {
                "completed": {"type": ["boolean", "null"]}
            }
        }
    )
    async def list_tasks(completed: bool | None = None):
        tasks = task_service.list_tasks(user_id, completed)
        return [task.to_dict() for task in tasks]

    # Tool 3: get_task
    @server.tool(
        name="get_task",
        description="Get a specific task by ID",
        input_schema={
            "type": "object",
            "properties": {
                "task_id": {"type": "integer"}
            },
            "required": ["task_id"]
        }
    )
    async def get_task(task_id: int):
        task = task_service.get_task(user_id, task_id)
        return task.to_dict()

    # Tool 4: update_task
    @server.tool(
        name="update_task",
        description="Update task fields (title, description, or completion status)",
        input_schema={
            "type": "object",
            "properties": {
                "task_id": {"type": "integer"},
                "title": {"type": "string", "minLength": 1, "maxLength": 200},
                "description": {"type": "string", "maxLength": 2000},
                "completed": {"type": "boolean"}
            },
            "required": ["task_id"]
        }
    )
    async def update_task(
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        completed: bool | None = None
    ):
        updates = {}
        if title is not None:
            updates["title"] = title
        if description is not None:
            updates["description"] = description
        if completed is not None:
            updates["completed"] = completed

        if not updates:
            raise ValueError("At least one field must be provided")

        task = task_service.update_task(user_id, task_id, **updates)
        return task.to_dict()

    # Tool 5: complete_task
    @server.tool(
        name="complete_task",
        description="Mark a task as completed",
        input_schema={
            "type": "object",
            "properties": {
                "task_id": {"type": "integer"}
            },
            "required": ["task_id"]
        }
    )
    async def complete_task(task_id: int):
        task = task_service.update_task(user_id, task_id, completed=True)
        return task.to_dict()

    # Tool 6: delete_task
    @server.tool(
        name="delete_task",
        description="Delete a task permanently",
        input_schema={
            "type": "object",
            "properties": {
                "task_id": {"type": "integer"}
            },
            "required": ["task_id"]
        }
    )
    async def delete_task(task_id: int):
        task_service.delete_task(user_id, task_id)
        return {
            "success": True,
            "message": "Task deleted successfully",
            "task_id": task_id
        }
```

---

## Authentication & Authorization

### User Context Binding

**Problem**: MCP tools need to know which user is making requests.

**Solution**: MCP server is instantiated per-request with `user_id` bound:

```
1. Request arrives at /ai/chat endpoint
2. JWT middleware extracts user_id
3. create_mcp_server(user_id, session) is called
4. All tools have access to user_id via closure
5. Tools call TaskService with user_id parameter
6. TaskService enforces ownership checks
```

**Security Properties**:
- ✅ No global state - each request isolated
- ✅ User cannot access other users' tasks
- ✅ Reuses existing TaskService authorization logic
- ✅ No new auth layer needed

---

## Error Handling

### MCP Tool Error Propagation

```python
# In each tool, wrap calls with try/except
try:
    task = task_service.get_task(user_id, task_id)
    return task.to_dict()
except TaskNotFoundError:
    raise MCPError(404, "Task not found")
except TaskPermissionError:
    raise MCPError(403, "Access denied")
except Exception as e:
    logger.error(f"Unexpected error in get_task: {e}")
    raise MCPError(500, "Internal server error")
```

**Error Response Format**:
```json
{
  "error": {
    "code": 404,
    "message": "Task not found",
    "type": "not_found"
  }
}
```

---

## Testing Strategy

### Unit Tests

```python
# tests/mcp/test_task_tools.py

def test_create_task_success():
    """Test creating a task via MCP tool"""
    server = create_mcp_server(user_id="user1", session=session)
    result = server.call_tool("create_task", {
        "title": "Buy groceries",
        "description": "Milk, eggs, bread"
    })
    assert result["title"] == "Buy groceries"
    assert result["completed"] == False

def test_list_tasks_filtered():
    """Test listing tasks with completion filter"""
    server = create_mcp_server(user_id="user1", session=session)
    result = server.call_tool("list_tasks", {"completed": False})
    assert all(task["completed"] == False for task in result)

def test_update_task_unauthorized():
    """Test that user cannot update another user's task"""
    server = create_mcp_server(user_id="user1", session=session)
    with pytest.raises(MCPError) as exc:
        server.call_tool("update_task", {
            "task_id": task_owned_by_user2.id,
            "title": "Hacked"
        })
    assert exc.value.code == 403
```

---

## Performance Considerations

### Per-Request Overhead

**Question**: Is creating a new MCP server per request expensive?

**Answer**: No, because:
1. MCP server is lightweight (just tool registry)
2. No network connections established
3. No heavy initialization
4. Database session is reused from FastAPI dependency
5. Tool functions are closures (cheap)

**Benchmark Target**: MCP server creation < 1ms

---

## Dependencies

```txt
mcp==1.1.0  # Official MCP SDK
```

---

## Success Criteria

✅ MCP server provides all 6 task tools
✅ Tools enforce user isolation via bound user_id
✅ Tools reuse Phase II TaskService (no duplication)
✅ Error handling propagates correctly
✅ Unit tests pass for all tools
✅ Per-request instantiation works correctly
✅ No modifications to Phase II code
