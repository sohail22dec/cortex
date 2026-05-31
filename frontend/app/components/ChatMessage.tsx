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
        className="bg-bg-base border border-border rounded-sm px-4 py-3 overflow-x-auto text-[13px] leading-relaxed my-2 text-[#a5b4fc] font-mono"
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
      elements.push(<h3 key={i} className="text-[15px] font-semibold mt-3 mb-1 text-text-primary">{line.slice(4)}</h3>);
    } else if (line.startsWith("## ")) {
      elements.push(<h2 key={i} className="text-[16px] font-bold mt-3.5 mb-1.5 text-text-primary">{line.slice(3)}</h2>);
    } else if (line.startsWith("# ")) {
      elements.push(<h1 key={i} className="text-[18px] font-bold mt-4 mb-2 text-text-primary">{line.slice(2)}</h1>);
    } else if (line.startsWith("- ") || line.startsWith("* ")) {
      elements.push(
        <li key={i} className="ml-4 mb-0.5 leading-relaxed text-text-primary">
          {renderInline(line.slice(2))}
        </li>
      );
    } else if (line.trim() === "") {
      elements.push(<div key={i} className="h-1.5" />);
    } else {
      elements.push(
        <p key={i} className="leading-[1.7] text-text-primary mb-0.5">
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
      return <strong key={i} className="font-semibold text-text-primary">{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return (
        <code key={i} className="bg-bg-overlay px-[5px] py-[1px] rounded-[4px] text-[13px] text-[#a5b4fc] font-mono">
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
      <div className="fade-in flex justify-end mb-4">
        <div
          className="max-w-[70%] text-white px-4 py-3 rounded-[var(--radius-lg)_var(--radius-lg)_4px_var(--radius-lg)] text-[14px] leading-relaxed shadow-glow break-words"
          style={{ background: "linear-gradient(135deg, var(--color-accent-primary), #6366f1)" }}
        >
          {message.content}
        </div>
      </div>
    );
  }

  // Assistant message
  return (
    <div className="fade-in flex gap-3 mb-5 items-start">
      {/* Avatar */}
      <div
        className="w-8 h-8 rounded-full flex items-center justify-center text-[14px] shrink-0 shadow-[0_0_12px_var(--color-accent-glow)]"
        style={{ background: "linear-gradient(135deg, var(--color-accent-primary), #6366f1)" }}
      >
        ✦
      </div>

      <div className="flex-1 min-w-0">
        {/* Header row */}
        <div className="flex items-center gap-2 mb-2">
          <span className="text-[13px] font-semibold text-text-secondary">Cortex</span>
          {message.source && !message.isLoading && (
            <SourceBadge source={message.source} small />
          )}
        </div>

        {/* Content */}
        <div className="bg-bg-surface border border-border rounded-[4px_var(--radius-lg)_var(--radius-lg)_var(--radius-lg)] px-4 py-3.5 text-[14px] leading-[1.7] shadow-sm">
          {message.isLoading ? (
            <div className="flex items-center gap-2.5">
              <div className="spinner" />
              <span className="text-text-muted text-[13px]">Thinking…</span>
            </div>
          ) : (
            formatContent(message.content)
          )}
        </div>

        {/* Citations */}
        {!message.isLoading && message.citations && message.citations.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1.5">
            {message.citations.map((cite, i) => (
              <a
                key={i}
                href={cite.startsWith("http") ? cite : undefined}
                target="_blank"
                rel="noopener noreferrer"
                title={cite}
                className={`text-[11px] px-2 py-0.5 rounded-full bg-bg-overlay border border-border text-text-muted no-underline whitespace-nowrap overflow-hidden text-ellipsis max-w-[220px] inline-block transition-colors ${
                  cite.startsWith("http") ? "cursor-pointer hover:text-text-primary" : "cursor-default"
                }`}
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
