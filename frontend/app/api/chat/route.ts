import { NextRequest, NextResponse } from "next/server";

// If you want to add OpenAI later, you can uncomment these lines
// import OpenAI from "openai";
// const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

export async function POST(req: NextRequest) {
  try {
    const { message } = await req.json();

    // Validate message
    if (!message || typeof message !== "string") {
      return NextResponse.json(
        { error: "Missing or invalid message" },
        { status: 400 }
      );
    }

    // --- Mock AI response for Phase 3 demo ---
    // Looks like a real AI reply
    const reply = `[AI response] You said: "${message}"`;

    // Optional: simulate thinking delay (makes it feel more realistic)
    await new Promise((resolve) => setTimeout(resolve, 500));

    return NextResponse.json({ reply });
  } catch (err) {
    console.error("Chatbot error:", err);
    return NextResponse.json({ error: "Chatbot failed" }, { status: 500 });
  }
}
