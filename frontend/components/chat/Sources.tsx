"use client";

import React, { useState } from "react";
import { Sparkles, FileText, Globe, ExternalLink } from "lucide-react";
import { cn } from "@/lib/utils";

interface SourcesProps {
  citations?: string[];
  sourceType?: "rag" | "llm" | "web_search";
}

export function Sources({ citations = [], sourceType = "rag" }: SourcesProps) {
  const [showAll, setShowAll] = useState(false);

  if (!citations || citations.length === 0) {
    if (sourceType === "llm") return null;
    return null;
  }

  const visibleCitations = showAll ? citations : citations.slice(0, 3);
  const remainingCount = citations.length - 3;

  return (
    <div className="mt-4 pt-3 border-t border-white/6 flex flex-col gap-2.5">
      {/* Sources Header */}
      <div className="flex items-center gap-1.5 text-xs font-semibold text-[#9d93ff]">
        <Sparkles className="w-3.5 h-3.5 fill-[#9d93ff]" />
        <span>Sources</span>
      </div>

      {/* Sources Chips */}
      <div className="flex flex-wrap items-center gap-2">
        {visibleCitations.map((cite, idx) => {
          const isWeb = cite.startsWith("http");
          let label = cite;
          let tag = "PDF";

          if (isWeb) {
            try {
              const url = new URL(cite);
              label = url.hostname.replace("www.", "");
              tag = "Web";
            } catch {
              label = "Web Source";
              tag = "Web";
            }
          } else {
            label = cite.replace(/\.[^/.]+$/, "");
            tag = cite.endsWith(".docx") ? "DOCX" : "PDF";
          }

          return (
            <a
              key={idx}
              href={isWeb ? cite : undefined}
              target={isWeb ? "_blank" : undefined}
              rel={isWeb ? "noopener noreferrer" : undefined}
              title={cite}
              className={cn(
                "inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#121824] border border-white/8 text-xs font-medium text-zinc-300 hover:text-white hover:border-[#6d5dfc]/40 hover:bg-[#161f30] transition-all max-w-[260px] truncate group select-none",
                isWeb ? "cursor-pointer" : "cursor-default"
              )}
            >
              {isWeb ? (
                <Globe className="w-3.5 h-3.5 text-amber-400 shrink-0" />
              ) : (
                <FileText className="w-3.5 h-3.5 text-red-400 shrink-0" />
              )}
              <span className="truncate">{label}</span>
              <span
                className={cn(
                  "text-[10px] px-1.5 py-0.5 rounded font-mono uppercase",
                  isWeb ? "bg-amber-500/15 text-amber-300" : "bg-red-500/15 text-red-300"
                )}
              >
                {tag}
              </span>
              {isWeb && <ExternalLink className="w-3 h-3 text-zinc-500 group-hover:text-zinc-300 ml-0.5 shrink-0" />}
            </a>
          );
        })}

        {remainingCount > 0 && !showAll && (
          <button
            onClick={() => setShowAll(true)}
            className="px-2.5 py-1.5 rounded-lg bg-[#121824] border border-white/8 text-xs font-medium text-zinc-400 hover:text-white hover:bg-[#161f30] transition-colors cursor-pointer"
          >
            + {remainingCount} more
          </button>
        )}
      </div>
    </div>
  );
}
