"use client";

import React, { useState } from "react";
import { FileText, Globe, ExternalLink } from "lucide-react";

interface SourcesProps {
  citations?: string[];
  sourceType?: "rag" | "llm" | "web_search" | "hybrid" | "guardrail";
}

export function Sources({
  citations = [],
  sourceType = "rag",
}: SourcesProps) {
  const [showAll, setShowAll] = useState(false);

  if (!citations || citations.length === 0) {
    if (sourceType === "llm") return null;
    return null;
  }

  const visibleCitations = showAll ? citations : citations.slice(0, 3);
  const remainingCount = citations.length - 3;

  return (
    <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
      <span className="text-[11px] font-medium text-zinc-500 select-none mr-0.5">
        Sources:
      </span>

      {visibleCitations.map((cite, idx) => {
        const isWeb = cite.startsWith("http");
        let label = cite;

        if (isWeb) {
          try {
            const url = new URL(cite);
            label = url.hostname.replace(/^www\./, "");
          } catch {
            label = "Web Source";
          }
        }

        if (isWeb) {
          return (
            <a
              key={idx}
              href={cite}
              target="_blank"
              rel="noopener noreferrer"
              title={cite}
              className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-[#121824]/60 hover:bg-[#161f30] border border-white/6 hover:border-amber-500/30 text-[11px] text-zinc-300 hover:text-white transition-all select-none group cursor-pointer max-w-[240px]"
            >
              <Globe className="w-3 h-3 text-amber-400 shrink-0" />
              <span className="truncate">{label}</span>
              <ExternalLink className="w-2.5 h-2.5 text-zinc-500 group-hover:text-zinc-300 shrink-0" />
            </a>
          );
        }

        return (
          <div
            key={idx}
            title={cite}
            className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-[#121824]/60 border border-white/6 text-[11px] text-zinc-300 select-none cursor-default max-w-[240px]"
          >
            <FileText className="w-3 h-3 text-red-400/90 shrink-0" />
            <span className="truncate">{label}</span>
          </div>
        );
      })}

      {remainingCount > 0 && !showAll && (
        <button
          type="button"
          onClick={() => setShowAll(true)}
          className="px-1.5 py-0.5 rounded-md text-[11px] text-zinc-400 hover:text-zinc-200 hover:bg-white/5 transition-colors cursor-pointer"
        >
          +{remainingCount} more
        </button>
      )}
    </div>
  );
}
