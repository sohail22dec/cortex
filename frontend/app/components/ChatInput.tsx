"use client";
import React, { useRef, useEffect } from "react";

interface ChatInputProps {
  value: string;
  onChange: (v: string) => void;
  onSend: () => void;
  isLoading: boolean;
  disabled?: boolean;
  placeholder?: string;
}

export default function ChatInput({
  value,
  onChange,
  onSend,
  isLoading,
  disabled = false,
  placeholder = "Ask anything about your documents…",
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
      style={{
        display: "flex",
        alignItems: "flex-end",
        gap: "10px",
        padding: "12px 16px",
        background: "var(--bg-surface)",
        border: "1px solid var(--border)",
        borderRadius: "var(--radius-lg)",
        transition: "border-color 0.2s",
      }}
      onFocus={(e) => {
        (e.currentTarget as HTMLElement).style.borderColor = "var(--border-accent)";
      }}
      onBlur={(e) => {
        (e.currentTarget as HTMLElement).style.borderColor = "var(--border)";
      }}
    >
      <textarea
        ref={textareaRef}
        id="chat-input"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKey}
        placeholder={placeholder}
        disabled={disabled || isLoading}
        rows={1}
        style={{
          flex: 1,
          background: "transparent",
          border: "none",
          outline: "none",
          color: "var(--text-primary)",
          fontSize: "14px",
          lineHeight: 1.6,
          resize: "none",
          fontFamily: "inherit",
          maxHeight: "160px",
          overflowY: "auto",
          padding: 0,
        }}
      />

      <button
        id="send-button"
        onClick={onSend}
        disabled={!canSend}
        aria-label="Send message"
        style={{
          width: "36px",
          height: "36px",
          borderRadius: "var(--radius-sm)",
          border: "none",
          background: canSend
            ? "linear-gradient(135deg, var(--accent-primary), #6366f1)"
            : "var(--bg-overlay)",
          color: canSend ? "#fff" : "var(--text-muted)",
          cursor: canSend ? "pointer" : "not-allowed",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
          transition: "all 0.2s",
          boxShadow: canSend ? "0 4px 12px var(--accent-glow)" : "none",
        }}
      >
        {isLoading ? (
          <div className="spinner" style={{ width: "14px", height: "14px" }} />
        ) : (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        )}
      </button>
    </div>
  );
}
