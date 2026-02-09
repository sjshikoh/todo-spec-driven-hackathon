# MCP Tools Specification

**Version:** 1.0.0
**Status:** Implemented
**Last Updated:** 2026-02-09

## Overview

This specification defines the Model Context Protocol (MCP) tools for task management. All tools are **stateless** and persist data in PostgreSQL via the existing TaskService layer.

## Architecture

### Stateless Design

```
Request → JWT Auth → Extract user_id → Create TaskTools(user_id, session)
   ↓
Execute Tool → TaskService → PostgreSQL → Return Result
   ↓
Destroy TaskTools instance
```

**Key Principles:**
1. **No in-memory state:** Each request creates a fresh TaskTools instance
2. **Database as source of truth:** All data persisted in PostgreSQL
3. **User isolation:** Tools bound to user_id at instantiation
4. **Transactional:** Each tool call is atomic (commit or rollback)

### Per-Request Instantiation

```python
# NOT a singleton - created per request
tools = TaskTools(user_id="user123", session=db_session)
result = tools.create_task(title="Buy groceries")
# Instance destroyed after request completes
```

## Tool Definitions

### 1. create_task

**Purpose:** Create a new task for the authenticated user

**OpenAI Function Schema:**
```json
{
  "type": "function",
  "function": {
    "name": "create_task",
    "description": "Create a new task for the user",
    "parameters": {
      "type": "object",
      "properties": {
        "title": {
          "type": "string",
          "description": "The task title (1-255 characters)"
        },
        "description": {
          "type": "string",
          "description": "Optional task description"
        }
      },
      "required": ["title"]
    }
  }
}
```

**Implementation:**
```python
def create_task(self, title: str, description: str = "") -> Dict[str, Any]:
    """
    Create a new task for the user.

    Persistence:
    - Calls TaskService.create_task(session, user_id, title, description)
    - Commits to PostgreSQL immediately
    - Returns serialized task object

    Args:
        title: Task title (1-255 chars)
        description: Optional description (default: "")

    Returns:
        {
            "id": int,
            "title": str,
            "description": str,
            "completed": false,
            "created_at": ISO 8601,
            "updated_at": ISO 8601
        }

    Raises:
        ValueError: If title is empty or too long
    """
    task = TaskService.create_task(self.session, self.user_id, title, description)
    return task_to_dict(task)
```

**Database Changes:**
- INSERT INTO tasks (user_id, title, description, completed, created_at, updated_at)
- Auto-commit via session.commit()

**Stateless Properties:**
- No instance variables modified
- No caching of results
- Fresh database query for ID generation

---

### 2. list_tasks

**Purpose:** List all tasks for the authenticated user with optional filtering

**OpenAI Function Schema:**
```json
{
  "type": "function",
  "function": {
    "name": "list_tasks",
    "description": "List all tasks for the user, optionally filtered by completion status",
    "parameters": {
      "type": "object",
      "properties": {
        "completed": {
          "type": "boolean",
          "description": "Filter by completion status. If not provided, returns all tasks."
        }
      },
      "required": []
    }
  }
}
```

**Implementation:**
```python
def list_tasks(self, completed: Optional[bool] = None) -> List[Dict[str, Any]]:
    """
    List all tasks for the user, optionally filtered by completion status.

    Persistence:
    - Queries PostgreSQL via TaskService.get_user_tasks(session, user_id)
    - Filters in-memory if completed parameter provided
    - No state cached

    Args:
        completed: Filter by completion status (None = all tasks)

    Returns:
        [
            {
                "id": int,
                "title": str,
                "description": str,
                "completed": bool,
                "created_at": ISO 8601,
                "updated_at": ISO 8601
            },
            ...
        ]
    """
    tasks = TaskService.get_user_tasks(self.session, self.user_id)

    # Filter by completion status if specified
    if completed is not None:
        tasks = [task for task in tasks if task.completed == completed]

    return [task_to_dict(task) for task in tasks]
```

**Database Queries:**
- SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC

**Stateless Properties:**
- Fresh query on every call
- No result caching
- Filtering done in-memory (stateless)

---

### 3. get_task

**Purpose:** Retrieve a specific task by ID

**OpenAI Function Schema:**
```json
{
  "type": "function",
  "function": {
    "name": "get_task",
    "description": "Get a specific task by ID",
    "parameters": {
      "type": "object",
      "properties": {
        "task_id": {
          "type": "integer",
          "description": "The task ID"
        }
      },
      "required": ["task_id"]
    }
  }
}
```

**Implementation:**
```python
def get_task(self, task_id: int) -> Dict[str, Any]:
    """
    Get a specific task by ID.

    Persistence:
    - Queries PostgreSQL via TaskService.get_task(session, task_id, user_id)
    - Enforces ownership check (user_id match)

    Args:
        task_id: The task ID

    Returns:
        {
            "id": int,
            "title": str,
            "description": str,
            "completed": bool,
            "created_at": ISO 8601,
            "updated_at": ISO 8601
        }

    Raises:
        ValueError: If task not found or doesn't belong to user
    """
    task = TaskService.get_task(self.session, task_id, self.user_id)
    if task is None:
        raise ValueError(f"Task {task_id} not found or access denied")

    return task_to_dict(task)
```

**Database Queries:**
- SELECT * FROM tasks WHERE id = ? AND user_id = ?

**Stateless Properties:**
- No caching of task objects
- Fresh query on every call
- User ownership verified in database query

---

### 4. update_task

**Purpose:** Update one or more fields of a task

**OpenAI Function Schema:**
```json
{
  "type": "function",
  "function": {
    "name": "update_task",
    "description": "Update task fields (title, description, or completion status)",
    "parameters": {
      "type": "object",
      "properties": {
        "task_id": {
          "type": "integer",
          "description": "The task ID"
        },
        "title": {
          "type": "string",
          "description": "New task title"
        },
        "description": {
          "type": "string",
          "description": "New task description"
        },
        "completed": {
          "type": "boolean",
          "description": "New completion status"
        }
      },
      "required": ["task_id"]
    }
  }
}
```

**Implementation:**
```python
def update_task(
    self,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    completed: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Update task fields.

    Persistence:
    - Calls TaskService.update_task(session, task_id, user_id, **updates)
    - Updates PostgreSQL immediately
    - Returns fresh task object from database

    Args:
        task_id: The task ID
        title: New title (optional)
        description: New description (optional)
        completed: New completion status (optional)

    Returns:
        Updated task object (same schema as get_task)

    Raises:
        ValueError: If task not found or no fields provided
    """
    if title is None and description is None and completed is None:
        raise ValueError("At least one field must be provided")

    task = TaskService.update_task(
        self.session, task_id, self.user_id, title, description, completed
    )

    if task is None:
        raise ValueError(f"Task {task_id} not found or access denied")

    return task_to_dict(task)
```

**Database Changes:**
- UPDATE tasks SET ... WHERE id = ? AND user_id = ?
- Updates updated_at timestamp automatically
- Auto-commit via session.commit()

**Stateless Properties:**
- No cached task state
- Fresh SELECT after UPDATE to return latest data
- Partial updates supported (only provided fields updated)

---

### 5. complete_task

**Purpose:** Convenience method to mark a task as completed

**OpenAI Function Schema:**
```json
{
  "type": "function",
  "function": {
    "name": "complete_task",
    "description": "Mark a task as completed",
    "parameters": {
      "type": "object",
      "properties": {
        "task_id": {
          "type": "integer",
          "description": "The task ID"
        }
      },
      "required": ["task_id"]
    }
  }
}
```

**Implementation:**
```python
def complete_task(self, task_id: int) -> Dict[str, Any]:
    """
    Mark a task as completed.

    Persistence:
    - Wrapper around TaskService.mark_complete(session, task_id, user_id)
    - Updates completed=true in PostgreSQL

    Args:
        task_id: The task ID

    Returns:
        Updated task object with completed=true

    Raises:
        ValueError: If task not found
    """
    task = TaskService.mark_complete(self.session, task_id, self.user_id)

    if task is None:
        raise ValueError(f"Task {task_id} not found or access denied")

    return task_to_dict(task)
```

**Database Changes:**
- UPDATE tasks SET completed = true, updated_at = NOW() WHERE id = ? AND user_id = ?

**Stateless Properties:**
- Convenience wrapper (no additional state)
- Delegates to update_task logic

---

### 6. delete_task

**Purpose:** Permanently delete a task

**OpenAI Function Schema:**
```json
{
  "type": "function",
  "function": {
    "name": "delete_task",
    "description": "Delete a task permanently",
    "parameters": {
      "type": "object",
      "properties": {
        "task_id": {
          "type": "integer",
          "description": "The task ID"
        }
      },
      "required": ["task_id"]
    }
  }
}
```

**Implementation:**
```python
def delete_task(self, task_id: int) -> Dict[str, str]:
    """
    Delete a task permanently.

    Persistence:
    - Calls TaskService.delete_task(session, task_id, user_id)
    - Removes row from PostgreSQL
    - Cascading deletes handled by database

    Args:
        task_id: The task ID

    Returns:
        {
            "success": true,
            "message": "Task deleted successfully",
            "task_id": int
        }

    Raises:
        ValueError: If task not found
    """
    success = TaskService.delete_task(self.session, task_id, self.user_id)

    if not success:
        raise ValueError(f"Task {task_id} not found or access denied")

    return {
        "success": True,
        "message": "Task deleted successfully",
        "task_id": task_id
    }
```

**Database Changes:**
- DELETE FROM tasks WHERE id = ? AND user_id = ?

**Stateless Properties:**
- No cached references to deleted task
- Immediate commit to database
- Boolean return indicates success

---

## Tool Execution

### Execute Tool Method

```python
def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
    """
    Execute a tool by name with given arguments.

    This method is called by the OpenAI agent when a tool call is made.

    Args:
        tool_name: Name of the tool to execute
        arguments: Tool arguments from OpenAI function call

    Returns:
        Tool execution result (varies by tool)

    Raises:
        ValueError: If tool name is unknown
    """
    tool_map = {
        "create_task": self.create_task,
        "list_tasks": self.list_tasks,
        "get_task": self.get_task,
        "update_task": self.update_task,
        "complete_task": self.complete_task,
        "delete_task": self.delete_task
    }

    if tool_name not in tool_map:
        raise ValueError(f"Unknown tool: {tool_name}")

    return tool_map[tool_name](**arguments)
```

## Data Serialization

### task_to_dict Function

```python
def task_to_dict(task: Task) -> Dict[str, Any]:
    """
    Convert Task model to dictionary for JSON serialization.

    Stateless conversion - no caching or modification of input.

    Args:
        task: Task model instance from database

    Returns:
        {
            "id": int,
            "title": str,
            "description": str,
            "completed": bool,
            "created_at": ISO 8601 string,
            "updated_at": ISO 8601 string
        }
    """
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None
    }
```

## User Isolation

### Security Model

**Per-Request User Binding:**
```python
# Request arrives with JWT token
user_id = extract_from_jwt(token)  # e.g., "user123"

# Create tools instance with user context
tools = TaskTools(user_id=user_id, session=session)

# All tool calls are scoped to this user
task = tools.create_task(title="Buy milk")
# task.user_id == "user123" (enforced by TaskService)
```

**Database-Level Enforcement:**
- All queries include `WHERE user_id = ?`
- TaskService enforces ownership checks
- No way for tools to access other users' data

**No Cross-User Contamination:**
- Tools instance destroyed after request
- No shared state between requests
- Each user gets isolated TaskTools instance

## Database Persistence

### Transaction Boundaries

**Create/Update/Delete:**
```python
# Transaction starts
task = Task(user_id=user_id, title=title)
session.add(task)
session.commit()  # ← Persisted to PostgreSQL
# Transaction ends
```

**Read Operations:**
```python
# No transaction needed (read-only)
tasks = session.query(Task).filter_by(user_id=user_id).all()
```

### Auto-Commit Behavior

All tools use auto-commit via TaskService:
- `session.commit()` called after each write operation
- No manual transaction management needed
- Rollback on exception (handled by FastAPI)

### Database Schema

**Tasks Table:**
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    completed BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id)
);
```

## Error Handling

### Tool-Level Errors

**Validation Errors:**
```python
if not title or len(title) > 255:
    raise ValueError("Title must be 1-255 characters")
```

**Not Found Errors:**
```python
if task is None:
    raise ValueError(f"Task {task_id} not found or access denied")
```

**Permission Errors:**
```python
# Handled implicitly by user_id filter in queries
# No explicit permission checking needed (database enforces)
```

### Error Propagation

```python
try:
    result = tools.execute_tool(tool_name, arguments)
except ValueError as e:
    # Return error to agent
    return {"error": str(e)}
except Exception as e:
    # Log and return generic error
    logger.error(f"Tool execution failed: {e}")
    return {"error": "Internal server error"}
```

## Testing

### Unit Tests

**Test Stateless Behavior:**
```python
def test_tools_are_stateless():
    """Verify tools don't cache state between calls"""
    tools = TaskTools(user_id="user1", session=session)

    # Create task
    task1 = tools.create_task(title="Task 1")

    # Create another instance (simulating new request)
    tools2 = TaskTools(user_id="user1", session=session)

    # Should see task1 in database
    tasks = tools2.list_tasks()
    assert any(t["id"] == task1["id"] for t in tasks)
```

**Test User Isolation:**
```python
def test_user_isolation():
    """Verify users cannot access each other's tasks"""
    tools1 = TaskTools(user_id="user1", session=session)
    tools2 = TaskTools(user_id="user2", session=session)

    # User1 creates task
    task = tools1.create_task(title="User1 task")

    # User2 cannot see it
    with pytest.raises(ValueError):
        tools2.get_task(task["id"])
```

**Test Persistence:**
```python
def test_persistence():
    """Verify all operations persist to database"""
    tools = TaskTools(user_id="user1", session=session)

    # Create
    task = tools.create_task(title="Test")
    assert task["id"] is not None

    # Verify in database
    db_task = session.query(Task).filter_by(id=task["id"]).first()
    assert db_task is not None
    assert db_task.title == "Test"
```

## Performance Considerations

### Query Optimization

**Indexed Queries:**
- All queries use `user_id` index
- Primary key lookups for get_task
- Ordered by created_at (indexed)

**Batch Operations:**
- list_tasks returns all tasks in one query
- No N+1 query problems

### Stateless Benefits

**Memory Efficiency:**
- No cached data in memory
- Tools instance destroyed after request
- Database handles caching (PostgreSQL)

**Scalability:**
- No shared state between requests
- Horizontal scaling possible
- No session affinity required

## Integration with TaskService

### Dependency

```python
from src.services.task_service import TaskService

class TaskTools:
    def __init__(self, user_id: str, session: Session):
        self.user_id = user_id
        self.session = session
        # No TaskService instance - all methods are static
```

### Delegation Pattern

All tools delegate to TaskService:
```python
# Tools layer (MCP interface)
def create_task(self, title: str, description: str = ""):
    task = TaskService.create_task(self.session, self.user_id, title, description)
    return task_to_dict(task)

# Service layer (business logic + persistence)
@staticmethod
def create_task(session, user_id, title, description):
    task = Task(user_id=user_id, title=title, description=description)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

## OpenAI Integration

### Function Calling Format

Tools are exported as OpenAI function definitions:
```python
def get_tool_definitions() -> List[Dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "create_task",
                "description": "...",
                "parameters": {...}
            }
        },
        # ... other tools
    ]
```

### Tool Call Flow

```
1. User: "Add a task to buy groceries"
2. OpenAI Agent: Analyzes intent → Decides to call create_task
3. Agent: Generates function call:
   {
     "name": "create_task",
     "arguments": {"title": "Buy groceries"}
   }
4. Backend: tools.execute_tool("create_task", {"title": "Buy groceries"})
5. TaskService: INSERT INTO tasks ...
6. Backend: Returns {"id": 1, "title": "Buy groceries", ...}
7. Agent: Formats response: "I've created the task 'Buy groceries' ✓"
```

## Success Criteria

- [x] 6 tools implemented (create, list, get, update, complete, delete)
- [x] All tools are stateless (no instance state)
- [x] All data persisted in PostgreSQL
- [x] User isolation enforced
- [x] Per-request instantiation
- [x] OpenAI function calling format
- [x] Integration with TaskService
- [x] Error handling implemented
- [x] Unit tests passing

## References

- **Implementation:** `src/mcp/tools/task_tools.py`
- **Server:** `src/mcp/server.py`
- **Service Layer:** `src/services/task_service.py`
- **Database Models:** `src/models/task.py`
