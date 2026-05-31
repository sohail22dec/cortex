"use client";
import React, { useRef, useEffect } from "react";

interface ChatInputProps {
  value: string;
  onChange: (v: string) => void;
  onSend: () => void;
  isLoading: boolean;
  disabled?: boolean;
  placeholder?: string;
  hasDocuments?: boolean;
}

export default function ChatInput({
  value,
  onChange,
  onSend,
  isLoading,
  disabled = false,
  placeholder = "Ask me anything...",
  hasDocuments = false,
}: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = Math.min(ta.scrollHeight, 160) + "px";
  }, [value]);

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!isLoading && !disabled && value.trim()) onSend();
    }
  };

  const canSend = value.trim().length > 0 && !isLoading && !disabled;

  return (
    <div
      className="flex items-end gap-2 pl-3 pr-3.5 py-2.5 bg-bg-surface border border-border/80 rounded-[28px] transition-all duration-300 focus-within:border-accent-primary/50 focus-within:shadow-[0_0_20px_rgba(124,58,237,0.12)] shadow-md"
    >
      {/* Left side - Attachment Button */}
      <button
        type="button"
        onClick={() => document.getElementById("file-input")?.click()}
        disabled={disabled || isLoading}
        className="relative w-9 h-9 rounded-full border-none flex items-center justify-center shrink-0 transition-all duration-200 bg-transparent text-text-muted hover:text-text-primary hover:bg-bg-elevated/70 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
        title={hasDocuments ? "Global Knowledge Base active. Click to add more documents" : "Attach document to knowledge base"}
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
        </svg>
        {hasDocuments && (
          <span className="absolute top-[5px] right-[5px] w-2.5 h-2.5 bg-emerald-500 rounded-full border border-bg-surface animate-pulse" />
        )}
      </button>

      {/* Middle - Textarea */}
      <textarea
        ref={textareaRef}
        id="chat-input"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKey}
        placeholder={placeholder}
        disabled={disabled || isLoading}
        rows={1}
        className="flex-1 bg-transparent border-none outline-none text-text-primary text-[15px] leading-relaxed resize-none font-sans max-h-[180px] overflow-y-auto py-2 px-1 placeholder:text-text-muted/60"
      />

      {/* Right side - Action Send Button */}
      <button
        id="send-button"
        onClick={onSend}
        disabled={!canSend}
        aria-label="Send message"
        className={`w-9 h-9 rounded-full border-none flex items-center justify-center shrink-0 transition-all duration-300 ${
          canSend
            ? "bg-accent-primary text-white cursor-pointer hover:bg-accent-secondary hover:scale-[1.05] active:scale-[0.98] shadow-md shadow-accent-primary/20"
            : "bg-bg-elevated/70 text-text-muted/40 cursor-not-allowed shadow-none"
        }`}
      >
        {isLoading ? (
          <div className="spinner" style={{ width: "14px", height: "14px", borderWidth: "1.5px" }} />
        ) : (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="12" y1="19" x2="12" y2="5" />
            <polyline points="5 12 12 5 19 12" />
          </svg>
        )}
      </button>
    </div>
  );
}
