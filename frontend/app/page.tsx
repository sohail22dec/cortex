"use client";
import React, { useState, useEffect, useRef, useCallback } from "react";
import ChatMessage, { Message } from "./components/ChatMessage";
import ChatInput from "./components/ChatInput";
import DocumentUpload from "./components/DocumentUpload";
import DocumentList from "./components/DocumentList";
import SourceBadge from "./components/SourceBadge";

// ── Session ID (persisted in localStorage) ────────────────────────────────────
function getOrCreateSessionId(): string {
  if (typeof window === "undefined") return "ssr";
  const key = "cortex_session_id";
  let id = localStorage.getItem(key);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(key, id);
  }
  return id;
}

// ── Welcome messages ──────────────────────────────────────────────────────────
const WELCOME: Message = {
  id: "welcome",
  role: "assistant",
  content:
    "Hello! I'm **Cortex**, your multi-agent AI assistant.\n\n" +
    "Here's how I work:\n" +
    "- 📄 **Upload documents** → I'll answer questions from them\n" +
    "- 🧠 **General questions** → I'll use my own knowledge\n" +
    "- 🌐 **Need current info?** → I'll search the web automatically\n\n" +
    "Start by uploading a document, or just ask me anything!",
  source: "llm",
  citations: [],
};

// ── Main page ─────────────────────────────────────────────────────────────────
export default function Home() {
  const [sessionId] = useState(() => getOrCreateSessionId());
  const [messages, setMessages] = useState<Message[]>([WELCOME]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [documents, setDocuments] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load documents list on mount
  useEffect(() => {
    fetch(`http://localhost:8000/api/documents?session_id=${sessionId}`)
      .then((r) => r.json())
      .then((d) => setDocuments(d.documents || []))
      .catch(() => {});
  }, [sessionId]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = useCallback(async () => {
    const question = input.trim();
    if (!question || isLoading) return;

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: question,
    };
    const loadingMsg: Message = {
      id: crypto.randomUUID(),
      role: "assistant",
      content: "",
      isLoading: true,
    };

    setMessages((prev) => [...prev, userMsg, loadingMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: question, session_id: sessionId }),
      });
      const data = await res.json();

      const assistantMsg: Message = {
        id: loadingMsg.id,
        role: "assistant",
        content: data.answer || "Sorry, something went wrong.",
        source: data.source,
        citations: data.citations || [],
      };

      setMessages((prev) =>
        prev.map((m) => (m.id === loadingMsg.id ? assistantMsg : m))
      );
    } catch {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === loadingMsg.id
            ? { ...m, isLoading: false, content: "⚠️ Failed to reach the backend. Is it running?", source: "llm" as const }
            : m
        )
      );
    } finally {
      setIsLoading(false);
    }
  }, [input, isLoading, sessionId]);

  const handleDocumentUploaded = useCallback((filename: string, chunks: number) => {
    setDocuments((prev) => prev.includes(filename) ? prev : [...prev, filename]);
    const notice: Message = {
      id: crypto.randomUUID(),
      role: "assistant",
      content: `✅ **"${filename}"** has been indexed successfully (${chunks} chunks). You can now ask questions about it!`,
      source: "rag",
      citations: [],
    };
    setMessages((prev) => [...prev, notice]);
  }, []);

  const handleDocumentDeleted = useCallback((filename: string) => {
    setDocuments((prev) => prev.filter((d) => d !== filename));
    const notice: Message = {
      id: crypto.randomUUID(),
      role: "assistant",
      content: `🗑️ **"${filename}"** has been removed from your session.`,
      source: "llm",
      citations: [],
    };
    setMessages((prev) => [...prev, notice]);
  }, []);

  const clearChat = () => {
    setMessages([WELCOME]);
  };

  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        overflow: "hidden",
        background: "var(--bg-base)",
      }}
    >
      {/* ── Sidebar ──────────────────────────────────────────────────────── */}
      <aside
        style={{
          width: sidebarOpen ? "300px" : "0px",
          minWidth: sidebarOpen ? "300px" : "0px",
          overflow: "hidden",
          transition: "all 0.3s ease",
          display: "flex",
          flexDirection: "column",
          background: "var(--bg-surface)",
          borderRight: "1px solid var(--border)",
          flexShrink: 0,
        }}
      >
        <div style={{ padding: "20px", flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: "20px" }}>
          {/* Logo */}
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div
              style={{
                width: "36px",
                height: "36px",
                borderRadius: "10px",
                background: "linear-gradient(135deg, var(--accent-primary), #6366f1)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "18px",
                boxShadow: "0 0 16px var(--accent-glow)",
                flexShrink: 0,
              }}
            >
              ✦
            </div>
            <div>
              <h1 className="glow-text" style={{ fontSize: "18px", fontWeight: 700, lineHeight: 1.2 }}>
                Cortex
              </h1>
              <p style={{ fontSize: "11px", color: "var(--text-muted)" }}>Multi-Agent RAG</p>
            </div>
          </div>

          {/* How it routes */}
          <div
            style={{
              padding: "12px",
              background: "var(--bg-base)",
              border: "1px solid var(--border)",
              borderRadius: "var(--radius-md)",
            }}
          >
            <p style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "10px" }}>
              Smart Routing
            </p>
            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
              {(["rag", "llm", "web_search"] as const).map((src) => (
                <div key={src} style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                  <SourceBadge source={src} small />
                  <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                    {src === "rag" ? "When you ask about docs" : src === "llm" ? "General knowledge" : "Current/live info"}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Upload section */}
          <div>
            <p style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "10px" }}>
              Documents
            </p>
            <DocumentUpload
              sessionId={sessionId}
              onUploaded={handleDocumentUploaded}
              isUploading={isUploading}
              setIsUploading={setIsUploading}
            />
          </div>

          {/* Document list */}
          <div style={{ flex: 1 }}>
            <p style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "10px" }}>
              Indexed ({documents.length})
            </p>
            <DocumentList
              documents={documents}
              sessionId={sessionId}
              onDeleted={handleDocumentDeleted}
            />
          </div>
        </div>

        {/* Session info */}
        <div
          style={{
            padding: "12px 16px",
            borderTop: "1px solid var(--border)",
            background: "var(--bg-base)",
          }}
        >
          <p style={{ fontSize: "10px", color: "var(--text-muted)", fontFamily: "monospace" }}>
            Session: {sessionId.slice(0, 8)}…
          </p>
        </div>
      </aside>

      {/* ── Main chat area ────────────────────────────────────────────────── */}
      <main style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
        {/* Header */}
        <header
          style={{
            display: "flex",
            alignItems: "center",
            gap: "12px",
            padding: "14px 20px",
            background: "var(--bg-surface)",
            borderBottom: "1px solid var(--border)",
            flexShrink: 0,
          }}
        >
          <button
            id="toggle-sidebar"
            onClick={() => setSidebarOpen((o) => !o)}
            aria-label="Toggle sidebar"
            style={{
              background: "none",
              border: "none",
              color: "var(--text-muted)",
              cursor: "pointer",
              padding: "4px",
              borderRadius: "var(--radius-sm)",
              display: "flex",
              alignItems: "center",
              transition: "color 0.2s",
            }}
            onMouseEnter={(e) => { (e.target as HTMLElement).style.color = "var(--text-primary)"; }}
            onMouseLeave={(e) => { (e.target as HTMLElement).style.color = "var(--text-muted)"; }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <line x1="3" y1="12" x2="21" y2="12" />
              <line x1="3" y1="6" x2="21" y2="6" />
              <line x1="3" y1="18" x2="21" y2="18" />
            </svg>
          </button>

          <div style={{ flex: 1 }}>
            <h2 style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)" }}>
              Chat with Cortex
            </h2>
            <p style={{ fontSize: "11px", color: "var(--text-muted)" }}>
              {documents.length > 0
                ? `${documents.length} document${documents.length > 1 ? "s" : ""} indexed · Ask anything`
                : "No documents — ask general questions or upload files"}
            </p>
          </div>

          <button
            id="clear-chat"
            onClick={clearChat}
            aria-label="Clear chat"
            style={{
              background: "var(--bg-overlay)",
              border: "1px solid var(--border)",
              color: "var(--text-muted)",
              cursor: "pointer",
              padding: "6px 12px",
              borderRadius: "var(--radius-sm)",
              fontSize: "12px",
              display: "flex",
              alignItems: "center",
              gap: "5px",
              transition: "all 0.2s",
            }}
            onMouseEnter={(e) => {
              const el = e.currentTarget as HTMLElement;
              el.style.color = "var(--text-primary)";
              el.style.borderColor = "var(--border-hover)";
            }}
            onMouseLeave={(e) => {
              const el = e.currentTarget as HTMLElement;
              el.style.color = "var(--text-muted)";
              el.style.borderColor = "var(--border)";
            }}
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
              <polyline points="1 4 1 10 7 10" />
              <path d="M3.51 15a9 9 0 1 0 .49-4.86L1 10" />
            </svg>
            Clear
          </button>
        </header>

        {/* Messages */}
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            padding: "24px 20px",
            display: "flex",
            flexDirection: "column",
          }}
        >
          {/* Background gradient blobs */}
          <div
            aria-hidden
            style={{
              position: "fixed",
              top: "20%",
              right: "10%",
              width: "400px",
              height: "400px",
              borderRadius: "50%",
              background: "radial-gradient(circle, rgba(124,58,237,0.06) 0%, transparent 70%)",
              pointerEvents: "none",
              zIndex: 0,
            }}
          />

          <div style={{ flex: 1, maxWidth: "760px", width: "100%", margin: "0 auto", position: "relative", zIndex: 1 }}>
            {messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input area */}
        <div
          style={{
            padding: "16px 20px 20px",
            background: "var(--bg-surface)",
            borderTop: "1px solid var(--border)",
            flexShrink: 0,
          }}
        >
          <div style={{ maxWidth: "760px", margin: "0 auto" }}>
            <ChatInput
              value={input}
              onChange={setInput}
              onSend={handleSend}
              isLoading={isLoading}
              placeholder={
                documents.length > 0
                  ? "Ask about your documents, or anything else…"
                  : "Ask me anything — I'll use web search for current info…"
              }
            />
            <p style={{ marginTop: "8px", fontSize: "11px", color: "var(--text-muted)", textAlign: "center" }}>
              Enter to send · Shift+Enter for newline · Powered by Groq · Qdrant · Tavily
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
