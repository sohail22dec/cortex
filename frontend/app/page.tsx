"use client";

import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import { Sidebar } from "@/components/sidebar/Sidebar";
import { ChatHeader } from "@/components/chat/ChatHeader";
import { MessageList } from "@/components/chat/MessageList";
import { ChatComposer } from "@/components/chat/ChatComposer";
import { DocumentsDrawer } from "@/components/documents/DocumentsDrawer";
import { MessageData } from "@/components/chat/AssistantMessage";
import { ConversationData } from "@/components/sidebar/ConversationItem";
import { DocumentInfo } from "@/components/documents/DocumentPreview";
import { toast } from "sonner";

export interface ChatSession {
  id: string;
  title: string;
  messages: MessageData[];
  createdAt: number;
  timestampStr?: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function generateSafeId(): string {
  if (typeof window !== "undefined" && window.crypto && typeof window.crypto.randomUUID === "function") {
    try {
      return window.crypto.randomUUID();
    } catch {
      // fallback
    }
  }
  return "id-" + Date.now().toString(36) + "-" + Math.random().toString(36).substring(2, 9);
}

function getOrCreateUserId(): string {
  if (typeof window === "undefined") return "ssr";
  const key = "coretext_user_id";
  try {
    let id = localStorage.getItem(key);
    if (!id) {
      id = generateSafeId();
      localStorage.setItem(key, id);
    }
    return id;
  } catch {
    return generateSafeId();
  }
}

// Initial mock conversations matching the design mockup for high-fidelity demonstration
const INITIAL_DEMO_SESSIONS: ChatSession[] = [
  {
    id: "demo-rag-1",
    title: "What is RAG and how does it work?",
    createdAt: Date.now() - 1000 * 60 * 5, // 5 min ago
    timestampStr: "2:31 PM",
    messages: [
      {
        id: "msg-user-1",
        role: "user",
        content: "What is RAG and how does it work?",
        timestamp: "2:31 PM",
      },
      {
        id: "msg-assistant-1",
        role: "assistant",
        content: `RAG (Retrieval-Augmented Generation) is a technique that combines the power of information retrieval and large language models to generate more accurate and up-to-date responses.

Here's how it works:

1. **Retrieval**: When a user asks a question, the system first retrieves relevant documents or passages from a knowledge base.
2. **Augmentation**: These retrieved documents are then provided as context to the language model.
3. **Generation**: The language model uses this context to generate a response that is more informed, accurate, and less likely to hallucinate.

This approach helps in grounding the model's responses in real data, making it ideal for enterprise applications and domain-specific knowledge.`,
        source: "rag",
        citations: [
          "RAG Paper (2020).pdf",
          "https://python.langchain.com/docs/concepts/rag",
          "https://docs.llamaindex.ai/en/stable/getting_started/concepts/",
          "Supabase pgvector Guide.pdf",
          "https://groq.com/docs",
        ],
        timestamp: "2:31 PM",
        chunksCount: 5,
      },
    ],
  },
  {
    id: "demo-rag-2",
    title: "Explain LangGraph with example",
    createdAt: Date.now() - 1000 * 60 * 60 * 24, // Yesterday
    timestampStr: "Yesterday",
    messages: [],
  },
  {
    id: "demo-rag-3",
    title: "Best practices for chunking documents",
    createdAt: Date.now() - 1000 * 60 * 60 * 24 * 4,
    timestampStr: "May 26",
    messages: [],
  },
  {
    id: "demo-rag-4",
    title: "How to evaluate RAG systems?",
    createdAt: Date.now() - 1000 * 60 * 60 * 24 * 6,
    timestampStr: "May 24",
    messages: [],
  },
  {
    id: "demo-rag-5",
    title: "Difference between RAG and Fine-tuning",
    createdAt: Date.now() - 1000 * 60 * 60 * 24 * 7,
    timestampStr: "May 23",
    messages: [],
  },
  {
    id: "demo-rag-6",
    title: "Agentic RAG Architecture",
    createdAt: Date.now() - 1000 * 60 * 60 * 24 * 9,
    timestampStr: "May 21",
    messages: [],
  },
  {
    id: "demo-rag-7",
    title: "Vector DB comparison",
    createdAt: Date.now() - 1000 * 60 * 60 * 24 * 10,
    timestampStr: "May 20",
    messages: [],
  },
];

const INITIAL_DOCUMENTS: DocumentInfo[] = [
  {
    filename: "RAG_Research_Paper.pdf",
    chunks: 128,
    sizeMb: "2.4 MB",
    uploadDate: "May 28, 2025",
  },
  {
    filename: "LangChain_Documentation.pdf",
    chunks: 256,
    sizeMb: "3.1 MB",
    uploadDate: "May 27, 2025",
  },
  {
    filename: "LlamaIndex_Guide.pdf",
    chunks: 198,
    sizeMb: "2.7 MB",
    uploadDate: "May 25, 2025",
  },
  {
    filename: "Vector_Databases_Overview.pdf",
    chunks: 96,
    sizeMb: "1.8 MB",
    uploadDate: "May 20, 2025",
  },
  {
    filename: "AI_Agents_The_Complete_Guide.pdf",
    chunks: 310,
    sizeMb: "4.2 MB",
    uploadDate: "May 18, 2025",
  },
];

function loadSavedSessions(): ChatSession[] {
  if (typeof window === "undefined") return INITIAL_DEMO_SESSIONS;
  try {
    const stored = localStorage.getItem("coretext_sessions");
    if (stored) {
      const parsed = JSON.parse(stored);
      if (Array.isArray(parsed) && parsed.length > 0) return parsed;
    }
    return INITIAL_DEMO_SESSIONS;
  } catch {
    return INITIAL_DEMO_SESSIONS;
  }
}

function saveSessionsToStorage(sessions: ChatSession[]) {
  if (typeof window !== "undefined") {
    try {
      localStorage.setItem("coretext_sessions", JSON.stringify(sessions));
    } catch {
      // ignore
    }
  }
}

export default function Home() {
  const [userId, setUserId] = useState<string>("ssr");
  const [sessions, setSessions] = useState<ChatSession[]>(INITIAL_DEMO_SESSIONS);
  const [activeChatId, setActiveChatId] = useState<string | null>("demo-rag-1");
  const activeChatIdRef = useRef(activeChatId);

  useEffect(() => {
    activeChatIdRef.current = activeChatId;
  }, [activeChatId]);

  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [documents, setDocuments] = useState<DocumentInfo[]>(INITIAL_DOCUMENTS);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [documentsDrawerOpen, setDocumentsDrawerOpen] = useState(false);

  // Initialize persistent state after hydration using microtask to avoid cascading renders
  useEffect(() => {
    const id = getOrCreateUserId();
    const loadedSessions = loadSavedSessions();
    queueMicrotask(() => {
      setUserId(id);
      setSessions(loadedSessions);
      if (loadedSessions.length > 0) {
        setActiveChatId(loadedSessions[0].id);
      }
    });
  }, []);

  // Sync documents from backend
  useEffect(() => {
    if (userId === "ssr") return;
    fetch(`${API_URL}/api/documents?session_id=${userId}`)
      .then((r) => r.json())
      .then((data) => {
        if (data.documents && Array.isArray(data.documents) && data.documents.length > 0) {
          const backendDocs: DocumentInfo[] = data.documents.map((name: string) => {
            const existing = INITIAL_DOCUMENTS.find((d) => d.filename === name);
            return {
              filename: name,
              chunks: existing?.chunks || 128,
              sizeMb: existing?.sizeMb || "2.4 MB",
              uploadDate: existing?.uploadDate || "Today",
            };
          });
          setDocuments(backendDocs);
        }
      })
      .catch(() => {});
  }, [userId]);

  // Active session and messages
  const activeSession = useMemo(
    () => sessions.find((s) => s.id === activeChatId),
    [sessions, activeChatId]
  );
  const messages = useMemo(
    () => (activeSession ? activeSession.messages : []),
    [activeSession]
  );

  // Update session helper
  const setMessages = useCallback(
    (newMessages: MessageData[] | ((prev: MessageData[]) => MessageData[])) => {
      setSessions((prevSessions) => {
        const activeIdx = prevSessions.findIndex((s) => s.id === activeChatIdRef.current);

        if (activeIdx === -1) {
          const initialMsgs = typeof newMessages === "function" ? newMessages([]) : newMessages;
          const newSession: ChatSession = {
            id: generateSafeId(),
            title: initialMsgs.length > 0 ? initialMsgs[0].content.slice(0, 32) : "New Chat",
            messages: initialMsgs,
            createdAt: Date.now(),
          };
          const updated = [newSession, ...prevSessions];
          saveSessionsToStorage(updated);
          setTimeout(() => setActiveChatId(newSession.id), 0);
          return updated;
        } else {
          const session = prevSessions[activeIdx];
          const updatedMsgs =
            typeof newMessages === "function" ? newMessages(session.messages) : newMessages;
          const updatedSession: ChatSession = { ...session, messages: updatedMsgs };

          if (session.messages.length === 0 && updatedMsgs.length > 0 && updatedMsgs[0].role === "user") {
            updatedSession.title =
              updatedMsgs[0].content.length > 32
                ? updatedMsgs[0].content.slice(0, 32) + "..."
                : updatedMsgs[0].content;
          }

          const updated = [...prevSessions];
          updated[activeIdx] = updatedSession;
          saveSessionsToStorage(updated);
          return updated;
        }
      });
    },
    []
  );

  const createNewChat = useCallback(() => {
    const newId = generateSafeId();
    const newSession: ChatSession = {
      id: newId,
      title: "New Chat",
      messages: [],
      createdAt: Date.now(),
    };
    setSessions((prev) => {
      const updated = [newSession, ...prev];
      saveSessionsToStorage(updated);
      return updated;
    });
    setActiveChatId(newId);
  }, []);

  const deleteChat = useCallback((id: string) => {
    setSessions((prev) => {
      const updated = prev.filter((s) => s.id !== id);
      saveSessionsToStorage(updated);
      return updated;
    });
    if (activeChatIdRef.current === id) {
      setSessions((prev) => {
        const remaining = prev.filter((s) => s.id !== id);
        setActiveChatId(remaining.length > 0 ? remaining[0].id : null);
        return remaining;
      });
    }
  }, []);

  const renameChat = useCallback((id: string, newTitle: string) => {
    setSessions((prev) => {
      const updated = prev.map((s) => (s.id === id ? { ...s, title: newTitle } : s));
      saveSessionsToStorage(updated);
      return updated;
    });
    toast.success("Chat renamed");
  }, []);

  const handleSend = useCallback(
    async (customInput?: string) => {
      const question = (typeof customInput === "string" ? customInput : input).trim();
      if (!question || isLoading) return;

      const currentTime = new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });

      const userMsg: MessageData = {
        id: generateSafeId(),
        role: "user",
        content: question,
        timestamp: currentTime,
      };

      const loadingMsg: MessageData = {
        id: generateSafeId(),
        role: "assistant",
        content: "",
        isLoading: true,
        timestamp: currentTime,
      };

      setMessages((prev) => [...prev, userMsg, loadingMsg]);
      setInput("");
      setIsLoading(true);

      try {
        const res = await fetch(`${API_URL}/api/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: question, session_id: userId }),
        });

        const data = await res.json();

        const assistantMsg: MessageData = {
          id: loadingMsg.id,
          role: "assistant",
          content: data.answer || "Sorry, no answer could be synthesized.",
          source: (data.source as "rag" | "llm" | "web_search") || "llm",
          citations: data.citations || [],
          suggest_web_search: data.suggest_web_search || false,
          question: question,
          timestamp: currentTime,
          chunksCount: data.source === "rag" ? 5 : undefined,
        };

        setMessages((prev) =>
          prev.map((m) => (m.id === loadingMsg.id ? assistantMsg : m))
        );
      } catch {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === loadingMsg.id
              ? {
                  ...m,
                  isLoading: false,
                  content: "⚠️ Failed to connect to the Coretext backend service. Please check that FastAPI is running on port 8000.",
                  source: "llm" as const,
                }
              : m
          )
        );
      } finally {
        setIsLoading(false);
      }
    },
    [input, isLoading, userId, setMessages]
  );

  const handleWebSearchFallback = useCallback(
    (question: string) => {
      handleSend(`Search the web for ${question}`);
    },
    [handleSend]
  );

  const handleDocumentUploaded = useCallback(
    (filename: string, chunks: number, sizeMb: string) => {
      setDocuments((prev) => {
        if (prev.some((d) => d.filename === filename)) return prev;
        return [
          {
            filename,
            chunks: chunks || 120,
            sizeMb: sizeMb || "2.0 MB",
            uploadDate: "Today",
          },
          ...prev,
        ];
      });
    },
    []
  );

  const handleDocumentDeleted = useCallback((filename: string) => {
    setDocuments((prev) => prev.filter((d) => d.filename !== filename));
  }, []);

  const handleUseInChat = useCallback(
    (filename: string) => {
      setInput(`Summarize and explain the key findings in ${filename}`);
    },
    []
  );

  // Map sessions to ConversationData
  const conversations: ConversationData[] = useMemo(
    () =>
      sessions.map((s) => ({
        id: s.id,
        title: s.title,
        createdAt: s.createdAt,
        timestampStr: s.timestampStr,
      })),
    [sessions]
  );

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#080b11] text-zinc-100 antialiased">
      {/* ── Left Sidebar ──────────────────────────────────────────────────────── */}
      <Sidebar
        conversations={conversations}
        activeChatId={activeChatId}
        userId={userId}
        onSelectChat={setActiveChatId}
        onNewChat={createNewChat}
        onDeleteChat={deleteChat}
        onRenameChat={renameChat}
        isOpen={sidebarOpen}
      />

      {/* ── Main Chat Area ───────────────────────────────────────────────────── */}
      <main className="flex-1 flex flex-col min-w-0 h-full overflow-hidden relative">
        <ChatHeader
          title={activeSession?.title || "What is RAG and how does it work?"}
          docCount={documents.length}
          onOpenDocuments={() => setDocumentsDrawerOpen(true)}
          onToggleSidebar={() => setSidebarOpen((prev) => !prev)}
          sidebarOpen={sidebarOpen}
        />

        <MessageList
          messages={messages}
          onSelectPrompt={(prompt) => handleSend(prompt)}
          onOpenDocuments={() => setDocumentsDrawerOpen(true)}
          onWebSearchFallback={handleWebSearchFallback}
        />

        <ChatComposer
          value={input}
          onChange={setInput}
          onSend={handleSend}
          isLoading={isLoading}
          onOpenDocuments={() => setDocumentsDrawerOpen(true)}
          hasDocuments={documents.length > 0}
        />
      </main>

      {/* ── Right Documents Drawer (Sheet) ───────────────────────────────────── */}
      <DocumentsDrawer
        open={documentsDrawerOpen}
        onOpenChange={setDocumentsDrawerOpen}
        documents={documents}
        sessionId={userId}
        onDocumentUploaded={handleDocumentUploaded}
        onDocumentDeleted={handleDocumentDeleted}
        onUseInChat={handleUseInChat}
      />
    </div>
  );
}
