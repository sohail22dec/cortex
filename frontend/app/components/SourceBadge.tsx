"use client";
import React from "react";

type Source = "rag" | "llm" | "web_search";

interface SourceBadgeProps {
  source: Source;
  small?: boolean;
}

const config: Record<Source, { icon: string; label: string; color: string; bg: string }> = {
  rag: {
    icon: "📄",
    label: "From Documents",
    color: "var(--source-rag)",
    bg: "var(--source-rag-soft)",
  },
  llm: {
    icon: "🧠",
    label: "LLM Knowledge",
    color: "var(--source-llm)",
    bg: "var(--source-llm-soft)",
  },
  web_search: {
    icon: "🌐",
    label: "Web Search",
    color: "var(--source-web)",
    bg: "var(--source-web-soft)",
  },
};

export default function SourceBadge({ source, small = false }: SourceBadgeProps) {
  const cfg = config[source] ?? config.llm;
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "5px",
        padding: small ? "2px 8px" : "4px 10px",
        borderRadius: "var(--radius-full)",
        fontSize: small ? "11px" : "12px",
        fontWeight: 500,
        color: cfg.color,
        background: cfg.bg,
        border: `1px solid ${cfg.color}33`,
        letterSpacing: "0.01em",
        userSelect: "none",
        flexShrink: 0,
      }}
    >
      <span style={{ fontSize: small ? "10px" : "12px" }}>{cfg.icon}</span>
      {cfg.label}
    </span>
  );
}
