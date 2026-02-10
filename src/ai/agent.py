"""
OpenAI agent with MCP tools for task management.
"""

import json
import uuid
from typing import Dict, Any, List, Optional, AsyncIterator
from openai import OpenAI
from sqlmodel import Session
from src.mcp.server import create_mcp_tools, get_tools
from src.ai.prompts import SYSTEM_PROMPT
from src.config import settings
import logging

logger = logging.getLogger(__name__)


class TodoAgent:
    """
    OpenAI agent with MCP tools for task management.

    Creates a per-user agent instance with MCP tools bound to user context.
    """

    def __init__(self, user_id: str, session: Session):
        """
        Initialize agent with user context.

        Args:
            user_id: Authenticated user ID
            session: Database session
        """
        self.user_id = user_id
        self.session = session
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.tools = create_mcp_tools(user_id, session)

    async def run(self, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Run agent with a single message.

        Args:
            message: User's message
            conversation_id: Optional conversation ID for context (future)

        Returns:
            {
                "response": "Agent's text response",
                "tool_calls": [{"name": "create_task", "args": {...}, "result": {...}}],
                "conversation_id": "abc123"
            }
        """
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ]

        tool_calls_result = []

        try:
            # Initial completion with tools
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                tools=get_tools(),
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens
            )

            assistant_message = response.choices[0].message

            # If agent wants to call tools
            if assistant_message.tool_calls:
                # Add assistant message to history
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })

                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    try:
                        # Execute tool via TaskTools
                        tool_result = self.tools.execute_tool(tool_name, tool_args)

                        tool_calls_result.append({
                            "name": tool_name,
                            "args": tool_args,
                            "result": tool_result
                        })

                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(tool_result)
                        })

                    except Exception as e:
                        logger.error(f"Tool execution error: {e}")
                        # Add error to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps({"error": str(e)})
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
                # No tool calls, just return the response
                final_message = assistant_message.content

            return {
                "response": final_message,
                "tool_calls": tool_calls_result,
                "conversation_id": conversation_id or str(uuid.uuid4())
            }

        except Exception as e:
            logger.error(f"Agent run error: {e}")
            raise

    async def stream(
        self, message: str, conversation_id: Optional[str] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream agent responses token-by-token.

        Yields:
            {
                "type": "text" | "tool_call" | "tool_result" | "done",
                "content": "...",
                "tool_name": "..." (if type=tool_call/tool_result)
            }
        """
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ]

        try:
            stream = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                tools=get_tools(),
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens,
                stream=True
            )

            tool_calls_buffer = []
            current_tool_call = None

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
                    for tool_call_delta in delta.tool_calls:
                        # Initialize new tool call
                        if tool_call_delta.function and tool_call_delta.function.name:
                            current_tool_call = {
                                "id": tool_call_delta.id,
                                "name": tool_call_delta.function.name,
                                "arguments": ""
                            }
                            tool_calls_buffer.append(current_tool_call)

                            yield {
                                "type": "tool_call",
                                "tool_name": tool_call_delta.function.name
                            }

                        # Accumulate arguments
                        if tool_call_delta.function and tool_call_delta.function.arguments:
                            if current_tool_call:
                                current_tool_call["arguments"] += tool_call_delta.function.arguments

            # Execute tools if any
            for tool_call in tool_calls_buffer:
                tool_name = tool_call["name"]
                tool_args = json.loads(tool_call["arguments"])

                try:
                    tool_result = self.tools.execute_tool(tool_name, tool_args)

                    yield {
                        "type": "tool_result",
                        "tool_name": tool_name,
                        "result": tool_result
                    }
                except Exception as e:
                    logger.error(f"Tool execution error: {e}")
                    yield {
                        "type": "error",
                        "message": str(e),
                        "tool_name": tool_name
                    }

            # Done signal
            yield {
                "type": "done",
                "conversation_id": conversation_id or str(uuid.uuid4())
            }

        except Exception as e:
            logger.error(f"Agent stream error: {e}")
            yield {
                "type": "error",
                "message": str(e)
            }


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
