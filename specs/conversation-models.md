# Conversation Persistence Specification

**Version:** 1.0.0
**Status:** Future (Phase IV)
**Last Updated:** 2026-02-09

## Overview

This specification defines the database models and persistence layer for conversation history. This is a **future enhancement** for Phase IV - not currently implemented in Phase III.

**Current State (Phase III):** All chat interactions are stateless with no conversation history.

**Future State (Phase IV):** Conversations persisted in PostgreSQL with message history.

## Motivation

### Problems with Stateless Design (Phase III)

1. **No Context Retention:**
   - User: "Show my tasks"
   - Agent: [lists tasks]
   - User: "Mark the first one as done"
   - Agent: "I need more context" ❌

2. **Repetitive User Input:**
   - User must be explicit in every message
   - Cannot use pronouns ("it", "that", "the first one")
   - Less natural conversation flow

3. **No Multi-Turn Planning:**
   - Cannot break complex tasks into steps
   - Cannot ask follow-up questions
   - All information needed upfront

### Benefits of Conversation Persistence

1. **Natural Context:**
   - Agent remembers previous messages
   - Pronoun resolution works
   - Multi-turn conversations possible

2. **Better UX:**
   - More natural dialogue
   - Less typing for users
   - Context-aware responses

3. **Complex Workflows:**
   - Multi-step task creation
   - Clarification questions
   - Iterative refinement

## Database Schema

### Conversations Table

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL REFERENCES users(id),
    title VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    archived BOOLEAN NOT NULL DEFAULT false,

    INDEX idx_conversations_user_id (user_id),
    INDEX idx_conversations_archived (archived),
    INDEX idx_conversations_updated_at (updated_at)
);
```

**Fields:**
- `id`: UUID primary key
- `user_id`: Foreign key to users table
- `title`: Optional conversation title (auto-generated or user-set)
- `created_at`: Conversation creation timestamp
- `updated_at`: Last message timestamp
- `archived`: Soft delete flag

**Indexes:**
- `user_id`: Fast user conversation lookups
- `archived`: Filter out archived conversations
- `updated_at`: Sort by recency

### Messages Table

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system', 'tool')),
    content TEXT,
    tool_call_id VARCHAR(255),
    tool_calls JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    INDEX idx_messages_conversation_id (conversation_id),
    INDEX idx_messages_created_at (created_at)
);
```

**Fields:**
- `id`: UUID primary key
- `conversation_id`: Foreign key to conversations table
- `role`: Message role (user, assistant, system, tool)
- `content`: Message text content (null for tool-only messages)
- `tool_call_id`: ID for tool result messages
- `tool_calls`: JSON array of tool calls (for assistant messages)
- `created_at`: Message timestamp

**Indexes:**
- `conversation_id`: Fast message retrieval for conversations
- `created_at`: Chronological ordering

**Cascading Delete:**
- Deleting conversation deletes all messages

### Tool Calls Storage

**JSONB Format:**
```json
[
  {
    "id": "call_abc123",
    "type": "function",
    "function": {
      "name": "create_task",
      "arguments": "{\"title\":\"Buy groceries\"}"
    }
  }
]
```

## SQLModel Models

### Conversation Model

```python
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional, List
import uuid

class Conversation(SQLModel, table=True):
    """
    Conversation model for storing chat conversations.
    Each conversation belongs to a user and contains multiple messages.
    """
    __tablename__ = "conversations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True, nullable=False)
    title: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    archived: bool = Field(default=False, nullable=False)

    # Relationship
    messages: List["Message"] = Relationship(back_populates="conversation")

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, user_id={self.user_id}, title={self.title})>"
```

### Message Model

```python
from sqlmodel import Field, SQLModel, Relationship, Column
from sqlalchemy import JSON
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

class Message(SQLModel, table=True):
    """
    Message model for storing chat messages within conversations.
    Supports user, assistant, system, and tool messages.
    """
    __tablename__ = "messages"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversations.id", index=True, nullable=False)
    role: str = Field(nullable=False, max_length=20)
    content: Optional[str] = Field(default=None)
    tool_call_id: Optional[str] = Field(default=None, max_length=255)
    tool_calls: Optional[List[Dict[str, Any]]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship
    conversation: Conversation = Relationship(back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role}, conversation_id={self.conversation_id})>"

    def to_openai_format(self) -> Dict[str, Any]:
        """Convert message to OpenAI chat format"""
        msg = {"role": self.role}

        if self.content:
            msg["content"] = self.content

        if self.tool_calls:
            msg["tool_calls"] = self.tool_calls

        if self.tool_call_id:
            msg["tool_call_id"] = self.tool_call_id

        return msg
```

## Conversation Service

### CRUD Operations

```python
from sqlmodel import Session, select
from typing import Optional, List
import uuid
from datetime import datetime

class ConversationService:
    """Service for conversation persistence operations"""

    @staticmethod
    def create_conversation(
        session: Session,
        user_id: str,
        title: Optional[str] = None
    ) -> Conversation:
        """
        Create a new conversation.

        Args:
            session: Database session
            user_id: User ID
            title: Optional conversation title

        Returns:
            Created conversation
        """
        conversation = Conversation(
            user_id=user_id,
            title=title or "New Conversation"
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return conversation

    @staticmethod
    def get_conversation(
        session: Session,
        conversation_id: uuid.UUID,
        user_id: str
    ) -> Optional[Conversation]:
        """
        Get a conversation by ID, ensuring it belongs to the user.

        Args:
            session: Database session
            conversation_id: Conversation UUID
            user_id: User ID

        Returns:
            Conversation if found and belongs to user, None otherwise
        """
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
            Conversation.archived == False
        )
        return session.exec(statement).first()

    @staticmethod
    def list_conversations(
        session: Session,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Conversation]:
        """
        List user's conversations, ordered by most recent.

        Args:
            session: Database session
            user_id: User ID
            limit: Max conversations to return
            offset: Pagination offset

        Returns:
            List of conversations
        """
        statement = (
            select(Conversation)
            .where(
                Conversation.user_id == user_id,
                Conversation.archived == False
            )
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(session.exec(statement))

    @staticmethod
    def update_conversation_title(
        session: Session,
        conversation_id: uuid.UUID,
        user_id: str,
        title: str
    ) -> Optional[Conversation]:
        """
        Update conversation title.

        Args:
            session: Database session
            conversation_id: Conversation UUID
            user_id: User ID
            title: New title

        Returns:
            Updated conversation or None if not found
        """
        conversation = ConversationService.get_conversation(
            session, conversation_id, user_id
        )
        if conversation:
            conversation.title = title
            conversation.updated_at = datetime.utcnow()
            session.commit()
            session.refresh(conversation)
        return conversation

    @staticmethod
    def archive_conversation(
        session: Session,
        conversation_id: uuid.UUID,
        user_id: str
    ) -> bool:
        """
        Archive a conversation (soft delete).

        Args:
            session: Database session
            conversation_id: Conversation UUID
            user_id: User ID

        Returns:
            True if archived, False if not found
        """
        conversation = ConversationService.get_conversation(
            session, conversation_id, user_id
        )
        if conversation:
            conversation.archived = True
            conversation.updated_at = datetime.utcnow()
            session.commit()
            return True
        return False

    @staticmethod
    def delete_conversation(
        session: Session,
        conversation_id: uuid.UUID,
        user_id: str
    ) -> bool:
        """
        Permanently delete a conversation and all its messages.

        Args:
            session: Database session
            conversation_id: Conversation UUID
            user_id: User ID

        Returns:
            True if deleted, False if not found
        """
        conversation = ConversationService.get_conversation(
            session, conversation_id, user_id
        )
        if conversation:
            session.delete(conversation)
            session.commit()
            return True
        return False
```

## Message Service

### Message Operations

```python
class MessageService:
    """Service for message persistence operations"""

    @staticmethod
    def add_message(
        session: Session,
        conversation_id: uuid.UUID,
        role: str,
        content: Optional[str] = None,
        tool_call_id: Optional[str] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None
    ) -> Message:
        """
        Add a message to a conversation.

        Args:
            session: Database session
            conversation_id: Conversation UUID
            role: Message role (user, assistant, system, tool)
            content: Message content
            tool_call_id: Tool call ID (for tool messages)
            tool_calls: Tool calls (for assistant messages)

        Returns:
            Created message
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_call_id=tool_call_id,
            tool_calls=tool_calls
        )
        session.add(message)

        # Update conversation's updated_at
        conversation = session.get(Conversation, conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()

        session.commit()
        session.refresh(message)
        return message

    @staticmethod
    def get_messages(
        session: Session,
        conversation_id: uuid.UUID,
        limit: Optional[int] = None
    ) -> List[Message]:
        """
        Get messages for a conversation in chronological order.

        Args:
            session: Database session
            conversation_id: Conversation UUID
            limit: Optional limit (most recent N messages)

        Returns:
            List of messages in chronological order
        """
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )

        if limit:
            # Get last N messages
            statement = (
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.desc())
                .limit(limit)
            )
            messages = list(session.exec(statement))
            messages.reverse()  # Reverse to chronological order
            return messages

        return list(session.exec(statement))

    @staticmethod
    def get_messages_for_openai(
        session: Session,
        conversation_id: uuid.UUID,
        max_messages: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get messages in OpenAI chat format.

        Args:
            session: Database session
            conversation_id: Conversation UUID
            max_messages: Maximum messages to include

        Returns:
            List of messages in OpenAI format
        """
        messages = MessageService.get_messages(
            session, conversation_id, limit=max_messages
        )
        return [msg.to_openai_format() for msg in messages]
```

## Agent Integration

### Stateful Agent

```python
class TodoAgent:
    """OpenAI agent with conversation history support"""

    def __init__(
        self,
        user_id: str,
        session: Session,
        conversation_id: Optional[uuid.UUID] = None
    ):
        self.user_id = user_id
        self.session = session
        self.conversation_id = conversation_id
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.tools = create_mcp_tools(user_id, session)

    async def run(self, message: str) -> Dict[str, Any]:
        """
        Process message with conversation history.

        Args:
            message: User's message

        Returns:
            Response with tool calls
        """
        # 1. Load conversation history
        if self.conversation_id:
            history = MessageService.get_messages_for_openai(
                self.session, self.conversation_id
            )
        else:
            # Create new conversation
            conversation = ConversationService.create_conversation(
                self.session, self.user_id
            )
            self.conversation_id = conversation.id
            history = []

        # 2. Build messages array with history
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *history,
            {"role": "user", "content": message}
        ]

        # 3. Store user message
        MessageService.add_message(
            self.session,
            self.conversation_id,
            role="user",
            content=message
        )

        # 4. Get response from OpenAI
        response = self.client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            tools=get_tools()
        )

        # 5. Execute tools if needed
        # ... (tool execution logic)

        # 6. Store assistant message
        MessageService.add_message(
            self.session,
            self.conversation_id,
            role="assistant",
            content=final_response,
            tool_calls=tool_calls_data
        )

        return {
            "response": final_response,
            "tool_calls": tool_calls_result,
            "conversation_id": str(self.conversation_id)
        }
```

## API Endpoint Changes

### Updated Chat Endpoint

```python
@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id_temp),
    session: Session = Depends(get_session)
):
    """
    Chat with conversation history.

    If conversation_id provided: Load history and continue
    If not provided: Create new conversation
    """
    # Parse conversation_id if provided
    conversation_id = None
    if request.conversation_id:
        try:
            conversation_id = uuid.UUID(request.conversation_id)
        except ValueError:
            raise HTTPException(400, "Invalid conversation_id format")

    # Create agent with conversation context
    agent = await create_todo_agent(user_id, session, conversation_id)

    # Process message (with history)
    result = await agent.run(message=request.message)

    return ChatResponse(
        response=result["response"],
        tool_calls=result["tool_calls"],
        conversation_id=result["conversation_id"]
    )
```

### New Conversation Management Endpoints

```python
@router.get("/conversations", response_model=List[ConversationSummary])
async def list_conversations(
    user_id: str = Depends(get_current_user_id_temp),
    session: Session = Depends(get_session),
    limit: int = 50,
    offset: int = 0
):
    """List user's conversations"""
    conversations = ConversationService.list_conversations(
        session, user_id, limit, offset
    )
    return [
        ConversationSummary(
            id=str(c.id),
            title=c.title,
            created_at=c.created_at,
            updated_at=c.updated_at
        )
        for c in conversations
    ]

@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id_temp),
    session: Session = Depends(get_session)
):
    """Get conversation with messages"""
    conversation = ConversationService.get_conversation(
        session, conversation_id, user_id
    )
    if not conversation:
        raise HTTPException(404, "Conversation not found")

    messages = MessageService.get_messages(session, conversation_id)

    return ConversationDetail(
        id=str(conversation.id),
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[
            MessageDetail(
                id=str(m.id),
                role=m.role,
                content=m.content,
                created_at=m.created_at
            )
            for m in messages
        ]
    )

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id_temp),
    session: Session = Depends(get_session)
):
    """Delete conversation"""
    success = ConversationService.delete_conversation(
        session, conversation_id, user_id
    )
    if not success:
        raise HTTPException(404, "Conversation not found")
    return {"success": True}
```

## Migration Path

### Phase III → Phase IV Migration

**Step 1: Add Database Tables**
```bash
# Create migration
alembic revision -m "Add conversation and message tables"

# Apply migration
alembic upgrade head
```

**Step 2: Add Models**
- Add `src/models/conversation.py`
- Add `src/models/message.py`

**Step 3: Add Services**
- Add `src/services/conversation_service.py`
- Add `src/services/message_service.py`

**Step 4: Update Agent**
- Modify `src/ai/agent.py` to accept `conversation_id`
- Load history when conversation_id provided

**Step 5: Update Endpoints**
- Modify `/ai/chat` to use conversation_id
- Add new conversation management endpoints

**Step 6: Feature Flag**
```python
# settings
enable_conversation_history: bool = False

# In agent creation
if settings.enable_conversation_history and conversation_id:
    # Load history
else:
    # Stateless mode
```

## Benefits Analysis

### User Experience

**Before (Phase III - Stateless):**
```
User: Show my tasks
Bot: [lists tasks]
User: Mark the first one as done
Bot: Which task? I don't have context.
```

**After (Phase IV - Stateful):**
```
User: Show my tasks
Bot: [lists tasks]
User: Mark the first one as done
Bot: Marked "Buy groceries" as done ✓
```

### Technical Considerations

**Storage Cost:**
- ~1KB per message
- 100 messages = 100KB
- 1000 conversations = ~100MB
- Negligible for PostgreSQL

**Query Performance:**
- Indexed by conversation_id
- Limit to last 50 messages
- Chronological order efficient

**Context Window:**
- GPT-4 Turbo: 128K tokens
- ~50 messages ≈ 5K tokens
- Plenty of room for history

## Testing Strategy

### Unit Tests

```python
def test_conversation_persistence():
    """Test conversation creation and retrieval"""
    conv = ConversationService.create_conversation(
        session, user_id="user1", title="Test"
    )
    assert conv.id is not None

    retrieved = ConversationService.get_conversation(
        session, conv.id, "user1"
    )
    assert retrieved.id == conv.id

def test_message_ordering():
    """Test messages are returned in chronological order"""
    conv = ConversationService.create_conversation(session, "user1")

    MessageService.add_message(session, conv.id, "user", "Message 1")
    MessageService.add_message(session, conv.id, "assistant", "Response 1")
    MessageService.add_message(session, conv.id, "user", "Message 2")

    messages = MessageService.get_messages(session, conv.id)
    assert len(messages) == 3
    assert messages[0].content == "Message 1"
    assert messages[1].content == "Response 1"
    assert messages[2].content == "Message 2"
```

## Success Criteria

Phase IV Implementation:
- [ ] Database schema created
- [ ] Models defined
- [ ] Services implemented
- [ ] Agent supports conversation_id
- [ ] API endpoints updated
- [ ] Migration path documented
- [ ] Tests passing
- [ ] Feature flag implemented

## References

- **Current Implementation:** Phase III (stateless)
- **Related Specs:**
  - `specs/mcp-tools.md` - Tool definitions
  - `specs/agent.md` - Agent behavior
  - `specs/chat-api.md` - Current stateless API
