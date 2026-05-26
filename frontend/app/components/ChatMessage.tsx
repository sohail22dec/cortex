"use client";
import React from "react";
import SourceBadge from "./SourceBadge";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  source?: "rag" | "llm" | "web_search";
  citations?: string[];
  isLoading?: boolean;
}

interface ChatMessageProps {
  message: Message;
}

function formatContent(text: string): React.ReactNode {
  // Basic markdown-ish rendering: bold, code blocks, inline code
  const lines = text.split("\n");
  const elements: React.ReactNode[] = [];

  let inCodeBlock = false;
  let codeLines: string[] = [];
  let codeLanguage = "";

  const flushCode = (key: string) => {
    elements.push(
      <pre
        key={key}
        style={{
          background: "var(--bg-base)",
          border: "1px solid var(--border)",
          borderRadius: "var(--radius-sm)",
          padding: "12px 16px",
          overflowX: "auto",
          fontSize: "13px",
          lineHeight: 1.6,
          margin: "8px 0",
          color: "#a5b4fc",
          fontFamily: "'Fira Code', 'Cascadia Code', monospace",
        }}
      >
        <code>{codeLines.join("\n")}</code>
      </pre>
    );
    codeLines = [];
    codeLanguage = "";
  };

  lines.forEach((line, i) => {
    if (line.startsWith("```")) {
      if (inCodeBlock) {
        flushCode(`code-${i}`);
        inCodeBlock = false;
      } else {
        inCodeBlock = true;
        codeLanguage = line.slice(3).trim();
      }
      return;
    }
    if (inCodeBlock) {
      codeLines.push(line);
      return;
    }

    // Headings
    if (line.startsWith("### ")) {
      elements.push(<h3 key={i} style={{ fontSize: "15px", fontWeight: 600, margin: "12px 0 4px", color: "var(--text-primary)" }}>{line.slice(4)}</h3>);
    } else if (line.startsWith("## ")) {
      elements.push(<h2 key={i} style={{ fontSize: "16px", fontWeight: 700, margin: "14px 0 6px", color: "var(--text-primary)" }}>{line.slice(3)}</h2>);
    } else if (line.startsWith("# ")) {
      elements.push(<h1 key={i} style={{ fontSize: "18px", fontWeight: 700, margin: "16px 0 8px", color: "var(--text-primary)" }}>{line.slice(2)}</h1>);
    } else if (line.startsWith("- ") || line.startsWith("* ")) {
      elements.push(
        <li key={i} style={{ marginLeft: "16px", marginBottom: "2px", lineHeight: 1.6, color: "var(--text-primary)" }}>
          {renderInline(line.slice(2))}
        </li>
      );
    } else if (line.trim() === "") {
      elements.push(<div key={i} style={{ height: "6px" }} />);
    } else {
      elements.push(
        <p key={i} style={{ lineHeight: 1.7, color: "var(--text-primary)", marginBottom: "2px" }}>
          {renderInline(line)}
        </p>
      );
    }
  });

  if (inCodeBlock && codeLines.length > 0) flushCode("code-final");

  return <>{elements}</>;
}

function renderInline(text: string): React.ReactNode {
  // Handle **bold** and `code`
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i} style={{ fontWeight: 600, color: "var(--text-primary)" }}>{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return (
        <code key={i} style={{ background: "var(--bg-overlay)", padding: "1px 5px", borderRadius: "4px", fontSize: "13px", color: "#a5b4fc", fontFamily: "monospace" }}>
          {part.slice(1, -1)}
        </code>
      );
    }
    return part;
  });
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div
        className="fade-in"
        style={{
          display: "flex",
          justifyContent: "flex-end",
          marginBottom: "16px",
        }}
      >
        <div
          style={{
            maxWidth: "70%",
            background: "linear-gradient(135deg, var(--accent-primary), #6366f1)",
            color: "#fff",
            padding: "12px 16px",
            borderRadius: "var(--radius-lg) var(--radius-lg) 4px var(--radius-lg)",
            fontSize: "14px",
            lineHeight: 1.6,
            boxShadow: "0 4px 16px var(--accent-glow)",
            wordBreak: "break-word",
          }}
        >
          {message.content}
        </div>
      </div>
    );
  }

  // Assistant message
  return (
    <div
      className="fade-in"
      style={{
        display: "flex",
        gap: "12px",
        marginBottom: "20px",
        alignItems: "flex-start",
      }}
    >
      {/* Avatar */}
      <div
        style={{
          width: "32px",
          height: "32px",
          borderRadius: "var(--radius-full)",
          background: "linear-gradient(135deg, var(--accent-primary), #6366f1)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: "14px",
          flexShrink: 0,
          boxShadow: "0 0 12px var(--accent-glow)",
        }}
      >
        ✦
      </div>

      <div style={{ flex: 1, minWidth: 0 }}>
        {/* Header row */}
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
          <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-secondary)" }}>Cortex</span>
          {message.source && !message.isLoading && (
            <SourceBadge source={message.source} small />
          )}
        </div>

        {/* Content */}
        <div
          style={{
            background: "var(--bg-surface)",
            border: "1px solid var(--border)",
            borderRadius: "4px var(--radius-lg) var(--radius-lg) var(--radius-lg)",
            padding: "14px 16px",
            fontSize: "14px",
            lineHeight: 1.7,
            boxShadow: "var(--shadow-sm)",
          }}
        >
          {message.isLoading ? (
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <div className="spinner" />
              <span style={{ color: "var(--text-muted)", fontSize: "13px" }}>Thinking…</span>
            </div>
          ) : (
            formatContent(message.content)
          )}
        </div>

        {/* Citations */}
        {!message.isLoading && message.citations && message.citations.length > 0 && (
          <div style={{ marginTop: "8px", display: "flex", flexWrap: "wrap", gap: "6px" }}>
            {message.citations.map((cite, i) => (
              <a
                key={i}
                href={cite.startsWith("http") ? cite : undefined}
                target="_blank"
                rel="noopener noreferrer"
                title={cite}
                style={{
                  fontSize: "11px",
                  padding: "2px 8px",
                  borderRadius: "var(--radius-full)",
                  background: "var(--bg-overlay)",
                  border: "1px solid var(--border)",
                  color: "var(--text-muted)",
                  textDecoration: "none",
                  cursor: cite.startsWith("http") ? "pointer" : "default",
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  maxWidth: "220px",
                  display: "inline-block",
                  transition: "color 0.2s",
                }}
                onMouseEnter={e => { if (cite.startsWith("http")) (e.target as HTMLElement).style.color = "var(--text-primary)"; }}
                onMouseLeave={e => { (e.target as HTMLElement).style.color = "var(--text-muted)"; }}
              >
                {cite.startsWith("http") ? `🔗 ${new URL(cite).hostname}` : `📄 ${cite}`}
              </a>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
