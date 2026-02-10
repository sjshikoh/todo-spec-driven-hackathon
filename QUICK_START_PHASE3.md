# Phase III Quick Start Guide – AI-Powered Todo Chatbot

## Phase III Summary

Phase III implements an AI-powered Todo Chatbot fully on top of Phase II without touching existing code. All features were designed using **Spec-Kit Plus** before coding, including MCP tools, AI agent behavior, stateless chat API, and conversation persistence. The backend is stateless, database-driven, and scalable, with **OpenAI Agents SDK integration** and streaming responses. Graceful degradation is handled if the OpenAI API key is not set. Full documentation, quick start instructions, and specifications are included in `/specs/phase-3/`, `PHASE3_COMPLETE.md`, and `PHASE3_IMPLEMENTATION.md`.

---

## Prerequisites

- Phase II implementation complete and working
- Python 3.10+ with pip
- Node.js 18+ with npm (for frontend)
- Optional: OpenAI API key ([get one here](https://platform.openai.com/api-keys))  
  > Note: If `OPENAI_API_KEY` is not set, the AI chatbot endpoints will return degraded responses. MCP tools and task management still function normally.

---

## Backend Setup (5 minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.txt

