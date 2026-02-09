"""
MCP tools for task management.
Provides function definitions and handlers for task operations.
"""

from typing import Optional, List, Dict, Any
from sqlmodel import Session
from src.services.task_service import TaskService
from src.models.task import Task


def get_tool_definitions() -> List[Dict[str, Any]]:
    """
    Get OpenAI function call tool definitions for task management.

    Returns:
        List of tool definitions in OpenAI function calling format
    """
    return [
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
        },
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
        },
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
        },
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
        },
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
        },
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
    ]


def task_to_dict(task: Task) -> Dict[str, Any]:
    """
    Convert Task model to dictionary for JSON serialization.

    Args:
        task: Task model instance

    Returns:
        Dictionary representation of task
    """
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None
    }


class TaskTools:
    """
    Task management tools for MCP/OpenAI function calling.
    All methods are bound to a specific user and session.
    """

    def __init__(self, user_id: str, session: Session):
        """
        Initialize task tools with user context.

        Args:
            user_id: Authenticated user ID
            session: Database session
        """
        self.user_id = user_id
        self.session = session

    def create_task(self, title: str, description: str = "") -> Dict[str, Any]:
        """
        Create a new task for the user.

        Args:
            title: Task title
            description: Optional task description

        Returns:
            Dictionary representation of created task
        """
        task = TaskService.create_task(self.session, self.user_id, title, description)
        return task_to_dict(task)

    def list_tasks(self, completed: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        List all tasks for the user, optionally filtered by completion status.

        Args:
            completed: Filter by completion status (None = all tasks)

        Returns:
            List of task dictionaries
        """
        tasks = TaskService.get_user_tasks(self.session, self.user_id)

        # Filter by completion status if specified
        if completed is not None:
            tasks = [task for task in tasks if task.completed == completed]

        return [task_to_dict(task) for task in tasks]

    def get_task(self, task_id: int) -> Dict[str, Any]:
        """
        Get a specific task by ID.

        Args:
            task_id: The task ID

        Returns:
            Dictionary representation of task

        Raises:
            ValueError: If task not found or doesn't belong to user
        """
        task = TaskService.get_task(self.session, task_id, self.user_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found or access denied")

        return task_to_dict(task)

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        completed: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Update task fields.

        Args:
            task_id: The task ID
            title: New title (optional)
            description: New description (optional)
            completed: New completion status (optional)

        Returns:
            Dictionary representation of updated task

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

    def complete_task(self, task_id: int) -> Dict[str, Any]:
        """
        Mark a task as completed.

        Args:
            task_id: The task ID

        Returns:
            Dictionary representation of updated task

        Raises:
            ValueError: If task not found
        """
        task = TaskService.mark_complete(self.session, task_id, self.user_id)

        if task is None:
            raise ValueError(f"Task {task_id} not found or access denied")

        return task_to_dict(task)

    def delete_task(self, task_id: int) -> Dict[str, str]:
        """
        Delete a task permanently.

        Args:
            task_id: The task ID

        Returns:
            Success message dictionary

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

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute a tool by name with given arguments.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments

        Returns:
            Tool execution result

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
