"use client";
import React from "react";
import SourceBadge from "./SourceBadge";
import DocumentUpload from "./DocumentUpload";
import DocumentList from "./DocumentList";
import { ChatSession } from "../page"; // We can just define the type locally or import it. Wait, I'll define it locally to prevent circular dependency, or use import type.

export interface ChatSessionData {
  id: string;
  title: string;
  messages: any[];
  createdAt: number;
}

interface SidebarProps {
  sidebarOpen: boolean;
  userId: string;
  documents: string[];
  isUploading: boolean;
  setIsUploading: (v: boolean) => void;
  onDocumentUploaded: (filename: string, chunks: number) => void;
  onDocumentDeleted: (filename: string) => void;
  
  sessions: ChatSessionData[];
  activeChatId: string | null;
  onSelectChat: (id: string) => void;
  onNewChat: () => void;
  onDeleteChat: (id: string) => void;
}

export default function Sidebar({
  sidebarOpen,
  userId,
  documents,
  isUploading,
  setIsUploading,
  onDocumentUploaded,
  onDocumentDeleted,
  sessions,
  activeChatId,
  onSelectChat,
  onNewChat,
  onDeleteChat,
}: SidebarProps) {
  return (
    <aside
      className={`flex flex-col shrink-0 overflow-hidden transition-all duration-300 ease-out bg-bg-surface border-r border-border ${
        sidebarOpen ? "w-[280px] min-w-[280px] md:w-[320px] md:min-w-[320px]" : "w-0 min-w-0 border-r-0"
      }`}
    >
      {/* ── Top Section: Logo & New Chat ─────────────────────────────────────── */}
      <div className="p-4 border-b border-border bg-bg-base/50 flex flex-col gap-4 shrink-0">
        <div className="flex items-center gap-2.5">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center text-[16px] shrink-0 shadow-glow text-white"
            style={{ background: "linear-gradient(135deg, var(--color-accent-primary), #6366f1)" }}
          >
            ✦
          </div>
          <div>
            <h1 className="glow-text text-[16px] font-bold leading-tight">
              Cortex
            </h1>
            <p className="text-[10px] text-text-muted">Agentic RAG System</p>
          </div>
        </div>

        <button
          onClick={onNewChat}
          className="w-full flex items-center justify-center gap-2 py-2 px-4 rounded-md border border-border-hover bg-bg-elevated hover:bg-bg-overlay hover:border-accent-primary/50 transition-all duration-200 text-sm font-medium text-text-primary"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          New Chat
        </button>
      </div>

      {/* ── Middle Section: Chat Sessions (Scrollable) ───────────────────────── */}
      <div className="flex-1 overflow-y-auto flex flex-col p-3 gap-1">
        <p className="text-[11px] font-semibold text-text-muted uppercase tracking-[0.08em] px-2 mb-1 mt-2">
          Chat History
        </p>
        
        {sessions.length === 0 ? (
          <div className="px-2 py-4 text-xs text-text-muted text-center italic">
            No past chats yet.
          </div>
        ) : (
          sessions.map((session) => {
            const isActive = session.id === activeChatId;
            return (
              <div
                key={session.id}
                onClick={() => onSelectChat(session.id)}
                className={`group relative flex items-center gap-2.5 px-3 py-2.5 rounded-md cursor-pointer transition-colors duration-200 ${
                  isActive 
                    ? "bg-accent-soft border border-border-accent/40 text-text-primary" 
                    : "hover:bg-bg-elevated text-text-secondary hover:text-text-primary border border-transparent"
                }`}
              >
                <svg className="shrink-0 text-text-muted" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
                <span className="text-[13px] font-medium truncate flex-1">
                  {session.title}
                </span>

                {/* Delete Button (visible on hover) */}
                <button
                  onClick={(e) => {
                    e.stopPropagation(); // Prevent selecting the chat when clicking delete
                    onDeleteChat(session.id);
                  }}
                  className={`opacity-0 group-hover:opacity-100 p-1.5 rounded-md hover:bg-red-500/20 hover:text-red-400 text-text-muted transition-all shrink-0 ${isActive ? 'opacity-100' : ''}`}
                  title="Delete chat"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                  </svg>
                </button>
              </div>
            );
          })
        )}
      </div>

      {/* ── Bottom Section: Global Knowledge Base ────────────────────────────── */}
      <div className="border-t border-border bg-bg-base/30 p-4 shrink-0 flex flex-col gap-4">
        <div>
          <p className="text-[11px] font-semibold text-text-muted uppercase tracking-[0.08em] mb-2.5 flex items-center justify-between">
            <span>Global Knowledge Base</span>
            <span className="bg-bg-elevated px-1.5 py-0.5 rounded text-[10px]">{documents.length}</span>
          </p>
          <DocumentUpload
            sessionId={userId}
            onUploaded={onDocumentUploaded}
            isUploading={isUploading}
            setIsUploading={setIsUploading}
          />
        </div>
        
        {documents.length > 0 && (
          <div className="max-h-[160px] overflow-y-auto pr-1">
            <DocumentList
              documents={documents}
              sessionId={userId}
              onDeleted={onDocumentDeleted}
            />
          </div>
        )}
      </div>

      {/* Profile info */}
      <div className="px-4 py-3 border-t border-border bg-bg-base/80 flex justify-between items-center shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-full bg-bg-elevated border border-border flex items-center justify-center text-[10px]">
            👤
          </div>
          <p className="text-[11px] text-text-secondary font-medium">
            Local Profile
          </p>
        </div>
        <p className="text-[9px] text-text-muted font-mono opacity-50">
          ID: {userId.slice(0, 6)}
        </p>
      </div>
    </aside>
  );
}
