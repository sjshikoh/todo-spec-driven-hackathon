"""
Simple chatbot endpoint.
Uses OpenAI if API key is configured, otherwise returns a mock response.
"""

import logging
import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


class ChatInput(BaseModel):
    message: str = Field(..., min_length=1)


class ChatOutput(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatOutput)
async def chat(body: ChatInput):
    """Simple chat endpoint. Always returns a valid JSON reply."""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()

    if api_key:
        return await _openai_reply(api_key, body.message)

    # No API key — return a mock response
    logger.info("No OPENAI_API_KEY set, using mock response")
    return ChatOutput(reply=f"[mock] You said: {body.message}")


async def _openai_reply(api_key: str, message: str) -> ChatOutput:
    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=[{"role": "user", "content": message}],
            max_tokens=256,
        )
        text = response.choices[0].message.content or ""
        return ChatOutput(reply=text.strip())
    except Exception as e:
        logger.error(f"/chat OpenAI error: {e}")
        raise HTTPException(status_code=502, detail="LLM request failed")
