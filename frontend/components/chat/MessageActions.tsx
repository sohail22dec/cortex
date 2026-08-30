"use client";

import React, { useState } from "react";
import {
  Copy,
  Check,
  ThumbsUp,
  ThumbsDown,
  Globe,
  ChevronDown,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { RetrievalDetailsDialog } from "./RetrievalDetailsDialog";
import { toast } from "sonner";

interface MessageActionsProps {
  content: string;
  timestamp?: string;
  source?: "rag" | "llm" | "web_search";
  chunksCount?: number;
  question?: string;
  suggestWebSearch?: boolean;
  onWebSearchFallback?: (question: string) => void;
}

export function MessageActions({
  content,
  timestamp,
  source = "rag",
  chunksCount = 5,
  question,
  suggestWebSearch,
  onWebSearchFallback,
}: MessageActionsProps) {
  const [copied, setCopied] = useState(false);
  const [liked, setLiked] = useState<boolean | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);

  const handleCopy = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(content);
      setCopied(true);
      toast.success("Copied answer to clipboard");
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleLike = () => {
    setLiked(liked === true ? null : true);
    toast.success("Thank you for your feedback!");
  };

  const handleDislike = () => {
    setLiked(liked === false ? null : false);
    toast.info("Feedback recorded. We will improve.");
  };

  return (
    <>
      <div className="mt-3 flex flex-wrap items-center justify-between gap-3 text-xs">
        {/* Left: Quick Actions */}
        <div className="flex items-center gap-1 text-zinc-400">
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={handleCopy}
            className="h-7 w-7 rounded-md text-zinc-400 hover:text-white hover:bg-white/5"
            title="Copy answer"
          >
            {copied ? (
              <Check className="w-3.5 h-3.5 text-emerald-400" />
            ) : (
              <Copy className="w-3.5 h-3.5" />
            )}
          </Button>

          <Button
            variant="ghost"
            size="icon-sm"
            onClick={handleLike}
            className={`h-7 w-7 rounded-md hover:bg-white/5 ${
              liked === true ? "text-[#9d93ff]" : "text-zinc-400 hover:text-white"
            }`}
            title="Helpful"
          >
            <ThumbsUp className={`w-3.5 h-3.5 ${liked === true ? "fill-[#9d93ff]" : ""}`} />
          </Button>

          <Button
            variant="ghost"
            size="icon-sm"
            onClick={handleDislike}
            className={`h-7 w-7 rounded-md hover:bg-white/5 ${
              liked === false ? "text-red-400" : "text-zinc-400 hover:text-white"
            }`}
            title="Not helpful"
          >
            <ThumbsDown className={`w-3.5 h-3.5 ${liked === false ? "fill-red-400" : ""}`} />
          </Button>

          {suggestWebSearch && question && onWebSearchFallback && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => onWebSearchFallback(question)}
              className="ml-2 h-7 px-2.5 rounded-lg border-amber-500/30 bg-amber-500/10 text-amber-300 hover:bg-amber-500/20 text-xs font-medium flex items-center gap-1.5"
            >
              <Globe className="w-3 h-3" />
              Search web for &quot;{question}&quot;
            </Button>
          )}
        </div>

        {/* Right: Timestamp & RAG Transparency pill */}
        <div className="flex items-center gap-3">
          {timestamp && (
            <span className="text-[11px] text-zinc-500 font-mono select-none">
              {timestamp}
            </span>
          )}

          {source === "rag" && (
            <button
              onClick={() => setDetailsOpen(true)}
              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#121824] border border-emerald-500/25 hover:border-emerald-500/50 text-[11px] text-emerald-400 font-medium transition-colors cursor-pointer group"
              title="Click to view retrieval transparency details"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span>Retrieved {chunksCount} chunks</span>
              <ChevronDown className="w-3 h-3 text-emerald-400/70 group-hover:text-emerald-400 transition-transform" />
            </button>
          )}

          {source === "web_search" && (
            <button
              onClick={() => setDetailsOpen(true)}
              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#121824] border border-amber-500/25 hover:border-amber-500/50 text-[11px] text-amber-400 font-medium transition-colors cursor-pointer"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
              <span>Web Search</span>
            </button>
          )}
        </div>
      </div>

      <RetrievalDetailsDialog
        open={detailsOpen}
        onOpenChange={setDetailsOpen}
        question={question}
        source={source}
        chunksCount={chunksCount}
      />
    </>
  );
}
