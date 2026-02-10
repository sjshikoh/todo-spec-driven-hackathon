"use client";

import { useState } from "react";

type Message = {
  id?: string;
  role: "user" | "ai";
  content: string;
};

export default function ChatbotPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");

  // Handles sending a message and mock AI response
  const sendMessage = async (message: string) => {
    if (!message.trim()) return;

    // Add user message
    setMessages((prev) => [...prev, { role: "user", content: message }]);
    setInput("");

    // Add temporary "AI is typing..." message
    const typingId = Math.random().toString(36).substring(2, 9);
    setMessages((prev) => [
      ...prev,
      { id: typingId, role: "ai", content: "AI is typing..." },
    ]);

    try {
      // Call your API route (mock will handle response)
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });
      const data = await res.json();

      // Replace typing message with AI reply
      setMessages((prev) =>
        prev.map((m) =>
          m.id === typingId ? { ...m, content: data.reply } : m
        )
      );
    } catch (err) {
      console.error(err);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === typingId ? { ...m, content: "Chatbot failed" } : m
        )
      );
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  return (
    <div className="max-w-md mx-auto mt-10 p-4 border rounded shadow">
      <h1 className="text-xl font-bold mb-4">Chatbot</h1>
      <div className="space-y-2 mb-4 h-64 overflow-y-auto border p-2 rounded bg-gray-50">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`p-2 rounded ${
              msg.role === "user" ? "bg-blue-100 text-blue-800 self-end" : "bg-gray-200 text-gray-900"
            }`}
          >
            {msg.content}
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 p-2 border rounded"
          placeholder="Type your message..."
        />
        <button type="submit" className="p-2 bg-blue-600 text-white rounded">
          Send
        </button>
      </form>
    </div>
  );
}
