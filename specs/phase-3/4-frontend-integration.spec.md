# Frontend Integration Specification

## Overview

This specification defines the frontend chat interface for Phase III using Vercel AI SDK. The UI provides a conversational interface for task management powered by the AI agent.

## Architecture

### Tech Stack

- **Framework**: Next.js 14 (App Router)
- **UI Library**: Vercel AI SDK (`@ai-sdk/react`)
- **Styling**: Tailwind CSS (existing)
- **API Communication**: Fetch API with streaming support

### Component Structure

```
frontend/
├── app/
│   └── chat/
│       └── page.tsx                 # Chat page route
├── components/
│   ├── ChatInterface.tsx            # Main chat component
│   └── ChatMessage.tsx              # Individual message component
└── lib/
    └── ai-client.ts                 # AI API client utilities
```

---

## 1. Chat Interface Component

### File: `frontend/components/ChatInterface.tsx`

```typescript
'use client';

import { useChat } from '@ai-sdk/react';
import { useState } from 'react';
import ChatMessage from './ChatMessage';

interface ChatInterfaceProps {
  token: string;  // JWT token from auth context
}

export default function ChatInterface({ token }: ChatInterfaceProps) {
  const { messages, input, handleInputChange, handleSubmit, isLoading, error } = useChat({
    api: '/api/ai/chat',
    headers: {
      Authorization: `Bearer ${token}`
    },
    onError: (error) => {
      console.error('Chat error:', error);
    }
  });

  return (
    <div className="flex flex-col h-[600px] w-full max-w-3xl mx-auto border border-gray-200 rounded-lg shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
          <h2 className="text-lg font-semibold">AI Task Assistant</h2>
        </div>
        <span className="text-sm text-gray-500">
          {isLoading ? 'Thinking...' : 'Ready'}
        </span>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <p className="text-lg mb-2">👋 Hi! I'm your task assistant.</p>
            <p className="text-sm">Ask me to:</p>
            <ul className="text-sm mt-2 space-y-1">
              <li>• "Add a task to buy groceries"</li>
              <li>• "Show me my pending tasks"</li>
              <li>• "Mark my first task as done"</li>
              <li>• "Delete the groceries task"</li>
            </ul>
          </div>
        )}

        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
            Error: {error.message}
          </div>
        )}
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="border-t border-gray-200 p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={handleInputChange}
            placeholder="Ask me to manage your tasks..."
            disabled={isLoading}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </form>
    </div>
  );
}
```

---

## 2. Chat Message Component

### File: `frontend/components/ChatMessage.tsx`

```typescript
import { Message } from '@ai-sdk/react';

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-2 ${
          isUser
            ? 'bg-blue-500 text-white'
            : 'bg-gray-100 text-gray-900'
        }`}
      >
        {/* Message content */}
        <div className="prose prose-sm max-w-none">
          {message.content.split('\n').map((line, i) => (
            <p key={i} className="mb-1 last:mb-0">
              {line}
            </p>
          ))}
        </div>

        {/* Timestamp */}
        <div
          className={`text-xs mt-1 ${
            isUser ? 'text-blue-100' : 'text-gray-500'
          }`}
        >
          {new Date(message.createdAt).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}
```

---

## 3. Chat Page

### File: `frontend/app/chat/page.tsx`

```typescript
import { redirect } from 'next/navigation';
import { cookies } from 'next/headers';
import ChatInterface from '@/components/ChatInterface';

export default async function ChatPage() {
  // Get JWT token from cookies (assumes Phase II auth sets this)
  const cookieStore = await cookies();
  const token = cookieStore.get('token')?.value;

  // Redirect to sign-in if not authenticated
  if (!token) {
    redirect('/sign-in');
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">AI Task Assistant</h1>
        <p className="text-gray-600">
          Manage your tasks through natural conversation
        </p>
      </div>

      <ChatInterface token={token} />

      {/* Feature hints */}
      <div className="mt-6 max-w-3xl mx-auto">
        <details className="text-sm text-gray-600">
          <summary className="cursor-pointer font-medium">
            What can the AI assistant do?
          </summary>
          <ul className="mt-2 space-y-1 pl-4">
            <li>✓ Create new tasks with natural language</li>
            <li>✓ List all your tasks or filter by status</li>
            <li>✓ Update task titles and descriptions</li>
            <li>✓ Mark tasks as completed</li>
            <li>✓ Delete tasks you no longer need</li>
          </ul>
        </details>
      </div>
    </div>
  );
}
```

---

## 4. AI API Client

### File: `frontend/lib/ai-client.ts`

```typescript
/**
 * Client-side utilities for interacting with AI endpoints.
 */

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  response: string;
  tool_calls: ToolCall[];
  conversation_id: string;
}

export interface ToolCall {
  name: string;
  args: Record<string, any>;
  result: Record<string, any>;
}

/**
 * Send a message to the AI chat endpoint (non-streaming).
 */
export async function sendChatMessage(
  request: ChatRequest,
  token: string
): Promise<ChatResponse> {
  const response = await fetch('/api/ai/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(request)
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Failed to send message');
  }

  return response.json();
}

/**
 * Check AI service health.
 */
export async function checkAIHealth(): Promise<{
  status: 'ok' | 'degraded' | 'down';
  mcp_enabled: boolean;
  ai_chat_enabled: boolean;
  model: string;
}> {
  const response = await fetch('/api/ai/health');

  if (!response.ok) {
    throw new Error('Health check failed');
  }

  return response.json();
}
```

---

## 5. Navigation Integration

### Modify: `frontend/app/layout.tsx` (or navigation component)

Add link to chat page in navigation:

```typescript
// Add to existing navigation
<nav className="flex gap-4">
  <Link href="/tasks">Tasks</Link>
  <Link href="/chat">AI Assistant</Link>
  <Link href="/settings">Settings</Link>
</nav>
```

---

## 6. API Route Proxy (Next.js)

### File: `frontend/app/api/ai/chat/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const token = request.headers.get('authorization');

    const response = await fetch(`${BACKEND_URL}/ai/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: token })
      },
      body: JSON.stringify(body)
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('AI chat proxy error:', error);
    return NextResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    );
  }
}
```

### File: `frontend/app/api/ai/health/route.ts`

```typescript
import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/ai/health`);
    const data = await response.json();

    return NextResponse.json(data);
  } catch (error) {
    console.error('AI health check error:', error);
    return NextResponse.json(
      { status: 'down', error: 'Cannot reach backend' },
      { status: 503 }
    );
  }
}
```

**Rationale**: Proxying through Next.js API routes prevents CORS issues and keeps backend URL hidden from client.

---

## 7. Streaming Support (Advanced)

### WebSocket Integration (Optional)

For real-time streaming, use WebSocket directly:

```typescript
'use client';

import { useEffect, useState, useRef } from 'react';

export function useStreamingChat(token: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(
      `ws://localhost:8000/ai/chat/stream?token=${token}`
    );

    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'text') {
        // Append text chunk to current message
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last && last.role === 'assistant') {
            return [
              ...prev.slice(0, -1),
              { ...last, content: last.content + data.content }
            ];
          } else {
            return [...prev, { role: 'assistant', content: data.content }];
          }
        });
      } else if (data.type === 'done') {
        console.log('Stream complete');
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    };

    wsRef.current = ws;

    return () => {
      ws.close();
    };
  }, [token]);

  const sendMessage = (content: string) => {
    if (wsRef.current && isConnected) {
      wsRef.current.send(
        JSON.stringify({
          type: 'message',
          content
        })
      );

      // Add user message to UI
      setMessages((prev) => [...prev, { role: 'user', content }]);
    }
  };

  return { messages, sendMessage, isConnected };
}
```

**Phase III Decision**: Start with non-streaming POST endpoint for simplicity. Add streaming in future iteration if needed.

---

## 8. Environment Variables

### File: `frontend/.env.local`

```bash
# Backend API URL
BACKEND_URL=http://localhost:8000

# Feature flags
NEXT_PUBLIC_AI_CHAT_ENABLED=true
```

---

## 9. Dependencies

### File: `frontend/package.json` (Additions)

```json
{
  "dependencies": {
    "@ai-sdk/openai": "^0.0.66",
    "@ai-sdk/react": "^0.0.62",
    "ai": "^3.4.0"
  }
}
```

### Installation

```bash
cd frontend
npm install @ai-sdk/openai @ai-sdk/react ai
```

---

## 10. Styling

### Tailwind Configuration

Ensure Tailwind is configured (should already exist from Phase II):

```javascript
// frontend/tailwind.config.js
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {}
  },
  plugins: []
};
```

### Custom Styles (Optional)

```css
/* frontend/app/globals.css */

.chat-message-user {
  @apply bg-blue-500 text-white;
}

.chat-message-assistant {
  @apply bg-gray-100 text-gray-900;
}

.chat-input {
  @apply px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500;
}
```

---

## 11. Testing

### Manual Testing Checklist

- [ ] Chat page requires authentication (redirects if not logged in)
- [ ] Can send messages to AI assistant
- [ ] AI responses appear in chat interface
- [ ] Can create tasks via natural language
- [ ] Can list tasks via natural language
- [ ] Can complete tasks via natural language
- [ ] Can delete tasks via natural language
- [ ] Error messages display correctly
- [ ] Loading states work correctly
- [ ] Mobile responsive design works

### Test Scenarios

1. **Create Task**
   - User: "Add a task to buy groceries"
   - Expected: Task created, confirmation message displayed

2. **List Tasks**
   - User: "Show me my tasks"
   - Expected: List of tasks displayed with status indicators

3. **Complete Task**
   - User: "Mark the groceries task as done"
   - Expected: Task marked as completed, confirmation displayed

4. **Error Handling**
   - User: Invalid request
   - Expected: Error message displayed, can retry

---

## 12. Accessibility

### ARIA Labels

```typescript
<div role="log" aria-live="polite" aria-label="Chat messages">
  {messages.map(...)}
</div>

<form onSubmit={handleSubmit} aria-label="Send message">
  <input
    type="text"
    aria-label="Message input"
    placeholder="Ask me to manage your tasks..."
  />
  <button type="submit" aria-label="Send message">
    Send
  </button>
</form>
```

### Keyboard Navigation

- Enter key submits message
- Escape key clears input
- Tab navigation works correctly

---

## 13. Mobile Responsiveness

### Responsive Design

```typescript
<div className="flex flex-col h-[600px] md:h-[700px] w-full max-w-full md:max-w-3xl">
  {/* Chat interface */}
</div>
```

### Mobile Optimizations

- Touch-friendly buttons (min 44px height)
- Responsive font sizes
- Scrollable message area
- Fixed input at bottom

---

## 14. Performance

### Optimizations

1. **Lazy Loading**: Chat component only loads on `/chat` route
2. **Memoization**: Memoize message components to prevent re-renders
3. **Debouncing**: Debounce input if adding "typing" indicator
4. **Virtual Scrolling**: If message history grows large, use virtual scrolling

### Performance Targets

- First Contentful Paint: < 1s
- Time to Interactive: < 2s
- Message render time: < 50ms

---

## 15. Future Enhancements

### Phase IV Possibilities

1. **Conversation History**: Persist conversations in database
2. **Voice Input**: Add speech-to-text for hands-free interaction
3. **Rich Formatting**: Support markdown, code blocks, task cards
4. **Suggestions**: Show suggested prompts based on context
5. **Multi-turn Context**: Remember previous messages in conversation
6. **Attachments**: Support file attachments for task descriptions

---

## Success Criteria

✅ Chat interface renders correctly
✅ Can send messages and receive responses
✅ Authentication works (redirects if not logged in)
✅ Natural language task operations work
✅ Error handling displays correctly
✅ Loading states work
✅ Mobile responsive design
✅ Navigation includes link to chat page
✅ Accessible via keyboard
✅ No regressions to Phase II frontend
