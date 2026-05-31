"use client";
import { useState, useEffect, useRef, useCallback } from "react";
import ChatMessage, { Message } from "./components/ChatMessage";
import ChatInput from "./components/ChatInput";
import Sidebar from "./components/Sidebar";

export interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  createdAt: number;
}

// ── Persistent State ────────────────────────────────────────────────────────
function getOrCreateUserId(): string {
  if (typeof window === "undefined") return "ssr";
  const key = "cortex_user_id";
  let id = localStorage.getItem(key);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(key, id);
  }
  return id;
}

function loadSessions(): ChatSession[] {
  if (typeof window === "undefined") return [];
  const stored = localStorage.getItem("cortex_sessions");
  return stored ? JSON.parse(stored) : [];
}

function saveSessions(sessions: ChatSession[]) {
  if (typeof window !== "undefined") {
    localStorage.setItem("cortex_sessions", JSON.stringify(sessions));
  }
}

// ── Main page ─────────────────────────────────────────────────────────────────
export default function Home() {
  const [userId, setUserId] = useState("ssr");
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [documents, setDocuments] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize on mount
  useEffect(() => {
    setUserId(getOrCreateUserId());
    const loaded = loadSessions();
    setSessions(loaded);
    if (loaded.length > 0) {
      setActiveChatId(loaded[0].id);
    }
  }, []);

  // Load documents for this user (global knowledge base)
  useEffect(() => {
    if (userId === "ssr") return;
    fetch(`http://localhost:8000/api/documents?session_id=${userId}`)
      .then((r) => r.json())
      .then((d) => setDocuments(d.documents || []))
      .catch(() => { });
  }, [userId]);

  // Derived active messages
  const activeSession = sessions.find(s => s.id === activeChatId);
  const messages = activeSession ? activeSession.messages : [];

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Session state updates
  const setMessages = useCallback((newMessages: Message[] | ((prev: Message[]) => Message[])) => {
    setSessions((prevSessions) => {
      let activeIdx = prevSessions.findIndex((s) => s.id === activeChatId);
      
      let updatedSession: ChatSession;
      if (activeIdx === -1) {
        // Create new session lazily
        const initialMsgs = typeof newMessages === "function" ? newMessages([]) : newMessages;
        updatedSession = {
          id: crypto.randomUUID(),
          title: initialMsgs.length > 0 ? initialMsgs[0].content.slice(0, 30) + "..." : "New Chat",
          messages: initialMsgs,
          createdAt: Date.now(),
        };
        const updated = [updatedSession, ...prevSessions];
        saveSessions(updated);
        setTimeout(() => setActiveChatId(updatedSession.id), 0); // Async update to avoid render conflict
        return updated;
      } else {
        const session = prevSessions[activeIdx];
        const updatedMsgs = typeof newMessages === "function" ? newMessages(session.messages) : newMessages;
        updatedSession = { ...session, messages: updatedMsgs };
        
        // Update title if first message
        if (session.messages.length === 0 && updatedMsgs.length > 0 && updatedMsgs[0].role === "user") {
          updatedSession.title = updatedMsgs[0].content.slice(0, 30) + "...";
        }
        
        const updated = [...prevSessions];
        updated[activeIdx] = updatedSession;
        saveSessions(updated);
        return updated;
      }
    });
  }, [activeChatId]);

  const createNewChat = useCallback(() => {
    const newId = crypto.randomUUID();
    const newSession: ChatSession = {
      id: newId,
      title: "New Chat",
      messages: [],
      createdAt: Date.now(),
    };
    const updated = [newSession, ...sessions];
    setSessions(updated);
    saveSessions(updated);
    setActiveChatId(newId);
  }, [sessions]);

  const deleteChat = useCallback((id: string) => {
    const updated = sessions.filter(s => s.id !== id);
    setSessions(updated);
    saveSessions(updated);
    if (activeChatId === id) {
      setActiveChatId(updated.length > 0 ? updated[0].id : null);
    }
  }, [sessions, activeChatId]);

  const handleSend = useCallback(async (customInput?: string) => {
    const question = (typeof customInput === "string" ? customInput : input).trim();
    if (!question || isLoading) return;

    // If there is no active chat and user sends a message, activeChatId might be null.
    // The setMessages logic handles lazy creation.

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
        // Passing userId as session_id allows backend to access the global knowledge base!
        body: JSON.stringify({ message: question, session_id: userId }),
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
  }, [input, isLoading, userId, setMessages]);

  const handleDocumentUploaded = useCallback((filename: string, chunks: number) => {
    setDocuments((prev) => prev.includes(filename) ? prev : [...prev, filename]);
    const notice: Message = {
      id: crypto.randomUUID(),
      role: "assistant",
      content: `✅ **"${filename}"** has been indexed to your global knowledge base.`,
      source: "rag",
      citations: [],
    };
    setMessages((prev) => [...prev, notice]);
  }, [setMessages]);

  const handleDocumentDeleted = useCallback((filename: string) => {
    setDocuments((prev) => prev.filter((d) => d !== filename));
    const notice: Message = {
      id: crypto.randomUUID(),
      role: "assistant",
      content: `🗑️ **"${filename}"** has been removed from your global knowledge base.`,
      source: "llm",
      citations: [],
    };
    setMessages((prev) => [...prev, notice]);
  }, [setMessages]);

  return (
    <div className="flex h-screen overflow-hidden bg-bg-base">
      <Sidebar
        sidebarOpen={sidebarOpen}
        userId={userId}
        documents={documents}
        isUploading={isUploading}
        setIsUploading={setIsUploading}
        onDocumentUploaded={handleDocumentUploaded}
        onDocumentDeleted={handleDocumentDeleted}
        
        sessions={sessions}
        activeChatId={activeChatId}
        onSelectChat={setActiveChatId}
        onNewChat={createNewChat}
        onDeleteChat={deleteChat}
      />

      {/* ── Main chat area ────────────────────────────────────────────────── */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="flex items-center gap-3 px-5 py-3.5 bg-bg-surface border-b border-border shrink-0">
          <button
            id="toggle-sidebar"
            onClick={() => setSidebarOpen((o) => !o)}
            aria-label="Toggle sidebar"
            className="group flex items-center p-1 rounded-sm bg-transparent border-none text-text-muted cursor-pointer transition-colors hover:text-text-primary"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <line x1="3" y1="12" x2="21" y2="12" />
              <line x1="3" y1="6" x2="21" y2="6" />
              <line x1="3" y1="18" x2="21" y2="18" />
            </svg>
          </button>

          <div className="flex-1">
            <h2 className="text-[14px] font-semibold text-text-primary">
              {activeSession ? activeSession.title : "New Chat"}
            </h2>
            <p className="text-[11px] text-text-muted">
              {documents.length > 0
                ? `${documents.length} document${documents.length > 1 ? "s" : ""} globally indexed`
                : "No documents indexed — AI will use general knowledge"}
            </p>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-5 pt-6 pb-2 flex flex-col relative">
          <div className="flex-1 max-w-[760px] w-full mx-auto relative z-10 flex flex-col justify-start">
            {messages.length === 0 ? (
              <div className="flex-1 flex flex-col items-center justify-start pt-12 md:pt-20 px-4 py-8 fade-in select-none">
                {/* Visual Header */}
                <div className="w-14 h-14 rounded-2xl bg-accent-primary flex items-center justify-center text-[26px] text-white shadow-glow mb-6 animate-pulse">
                  ✦
                </div>

                <h2 className="glow-text text-3xl md:text-4xl font-extrabold text-center tracking-tight mb-2">
                  Cortex
                </h2>
                <p className="text-text-secondary text-sm md:text-base text-center max-w-[500px] mb-10 leading-relaxed">
                  Your premium multi-agent assistant for document analysis, general knowledge, and real-time web search.
                </p>

                {/* Responsive 3-Column Glassmorphic Feature Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full mb-10">
                  <div className="glass p-5 rounded-md flex flex-col items-center text-center transition-all duration-300 hover:border-border-accent hover:scale-[1.02]">
                    <div className="text-3xl mb-3 text-emerald-400">📄</div>
                    <h3 className="text-text-primary text-[15px] font-semibold mb-1.5">Document RAG</h3>
                    <p className="text-text-muted text-[12px] leading-relaxed">
                      Upload PDFs to your knowledge base to query their contents.
                    </p>
                  </div>
                  <div className="glass p-5 rounded-md flex flex-col items-center text-center transition-all duration-300 hover:border-border-accent hover:scale-[1.02]">
                    <div className="text-3xl mb-3 text-purple-400">🧠</div>
                    <h3 className="text-text-primary text-[15px] font-semibold mb-1.5">General Knowledge</h3>
                    <p className="text-text-muted text-[12px] leading-relaxed">
                      Ask questions, debug code, or brainstorm ideas using LLMs.
                    </p>
                  </div>
                  <div className="glass p-5 rounded-md flex flex-col items-center text-center transition-all duration-300 hover:border-border-accent hover:scale-[1.02]">
                    <div className="text-3xl mb-3 text-amber-400">🌐</div>
                    <h3 className="text-text-primary text-[15px] font-semibold mb-1.5">Real-Time Search</h3>
                    <p className="text-text-muted text-[12px] leading-relaxed">
                      Search the web automatically to fetch live info.
                    </p>
                  </div>
                </div>

                {/* Clickable Quick-Start Prompts */}
                <div className="w-full max-w-[640px]">
                  <p className="text-[11px] font-semibold text-text-muted uppercase tracking-[0.08em] text-center mb-3">
                    Suggested Starter Prompts
                  </p>
                  <div className="flex flex-wrap gap-2.5 justify-center">
                    {[
                      "Explain how multi-agent RAG architectures work",
                      "What are some interesting use cases for AI?",
                      "Search the web for the latest artificial intelligence headlines",
                    ].map((promptText, idx) => (
                      <button
                        key={idx}
                        onClick={() => {
                          handleSend(promptText);
                        }}
                        className="px-4 py-2 bg-bg-elevated/40 hover:bg-accent-soft/30 hover:text-text-primary hover:border-border-accent border border-border text-[12px] text-text-secondary rounded-full cursor-pointer transition-all duration-200"
                      >
                        {promptText} →
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <>
                {messages.map((msg) => (
                  <ChatMessage key={msg.id} message={msg} />
                ))}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>
        </div>

        {/* Input area */}
        <div className="px-5 pt-2 pb-5 bg-bg-base shrink-0">
          <div className="max-w-[760px] mx-auto">
            <ChatInput
              value={input}
              onChange={setInput}
              onSend={handleSend}
              isLoading={isLoading}
              hasDocuments={documents.length > 0}
              placeholder="Ask anything..."
            />
            <p className="mt-2 text-[11px] text-text-muted text-center">
              Enter to send · Shift+Enter for newline
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
