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
      className="flex flex-col gap-2.5 px-4 py-3 bg-bg-surface border border-border rounded-xl transition-all duration-200 focus-within:border-border-hover shadow-md"
    >
      {/* Top area - Textarea only */}
      <textarea
        ref={textareaRef}
        id="chat-input"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKey}
        placeholder={placeholder}
        disabled={disabled || isLoading}
        rows={1}
        className="w-full bg-transparent border-none outline-none text-text-primary text-[14px] leading-relaxed resize-none font-sans max-h-[160px] overflow-y-auto p-0 placeholder:text-text-muted"
      />

      {/* Bottom area - Toolbar with send button on right */}
      <div className="flex justify-between items-center mt-1.5">
        {/* Attachment Button */}
        <button
          type="button"
          onClick={() => document.getElementById("file-input")?.click()}
          disabled={disabled || isLoading}
          className="w-8 h-8 rounded-full border-none flex items-center justify-center shrink-0 transition-all duration-200 bg-transparent text-text-muted hover:text-text-primary hover:bg-bg-elevated cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          title="Attach document to knowledge base"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
          </svg>
        </button>

        {/* Action Send Button */}
        <button
          id="send-button"
          onClick={onSend}
          disabled={!canSend}
          aria-label="Send message"
          className={`w-8 h-8 rounded-full border-none flex items-center justify-center shrink-0 transition-all duration-200 ${canSend
            ? "bg-text-primary text-bg-base cursor-pointer hover:bg-gray-200 hover:scale-105 active:scale-95 shadow-sm"
            : "bg-bg-elevated/60 text-text-muted cursor-not-allowed shadow-none"
            }`}
        >
          {isLoading ? (
            <div className="spinner w-[12px] h-[12px]" />
          ) : (
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          )}
        </button>
      </div>
    </div>
  );
}
