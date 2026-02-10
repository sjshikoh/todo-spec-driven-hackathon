"""
MCP server for task management.
Creates per-request MCP server instances with user context.
"""

from sqlmodel import Session
from src.mcp.tools.task_tools import TaskTools, get_tool_definitions


def create_mcp_tools(user_id: str, session: Session) -> TaskTools:
    """
    Create MCP tools instance with user context bound.

    This function creates a per-request TaskTools instance that has
    user_id and session bound to it. All tool operations will be
    scoped to this user.

    Args:
        user_id: Authenticated user ID from JWT
        session: SQLAlchemy database session

    Returns:
        TaskTools instance with user context
    """
    return TaskTools(user_id, session)


def get_tools() -> list:
    """
    Get list of available tool definitions.

    Returns:
        List of tool definitions in OpenAI function calling format
    """
    return get_tool_definitions()
