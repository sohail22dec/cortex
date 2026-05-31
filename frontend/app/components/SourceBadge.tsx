"use client";

type Source = "rag" | "llm" | "web_search";

interface SourceBadgeProps {
  source: Source;
  small?: boolean;
}

const config: Record<Source, { icon: string; label: string; colorClass: string; bgClass: string; borderClass: string }> = {
  rag: {
    icon: "📄",
    label: "From Documents",
    colorClass: "text-source-rag",
    bgClass: "bg-source-rag-soft",
    borderClass: "border-source-rag/20",
  },
  llm: {
    icon: "🧠",
    label: "LLM Knowledge",
    colorClass: "text-source-llm",
    bgClass: "bg-source-llm-soft",
    borderClass: "border-source-llm/20",
  },
  web_search: {
    icon: "🌐",
    label: "Web Search",
    colorClass: "text-source-web",
    bgClass: "bg-source-web-soft",
    borderClass: "border-source-web/20",
  },
};

export default function SourceBadge({ source, small = false }: SourceBadgeProps) {
  const cfg = config[source] ?? config.llm;
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-medium tracking-[0.01em] select-none shrink-0 border ${cfg.colorClass} ${cfg.bgClass} ${cfg.borderClass} ${small ? "px-2 py-0.5 text-[11px]" : "px-2.5 py-1 text-[12px]"
        }`}
    >
      <span className={small ? "text-[10px]" : "text-[12px]"}>{cfg.icon}</span>
      {cfg.label}
    </span>
  );
}
