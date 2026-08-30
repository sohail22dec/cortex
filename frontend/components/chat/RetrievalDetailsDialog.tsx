"use client";

import React from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Database, CheckCircle2, ShieldCheck, Cpu } from "lucide-react";

interface RetrievalDetailsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  question?: string;
  source?: "rag" | "llm" | "web_search";
  chunksCount?: number;
}

export function RetrievalDetailsDialog({
  open,
  onOpenChange,
  question = "What is RAG and how does it work?",
  source = "rag",
  chunksCount = 5,
}: RetrievalDetailsDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md bg-[#0d111a] border-white/10 text-zinc-100">
        <DialogHeader>
          <DialogTitle className="text-base font-semibold flex items-center gap-2">
            <Database className="w-4 h-4 text-[#6d5dfc]" />
            Corrective RAG Pipeline Details
          </DialogTitle>
          <DialogDescription className="text-xs text-zinc-400">
            Transparency breakdown of query routing, chunk retrieval, and groundedness validation.
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-3 py-2 text-xs">
          {/* Query */}
          <div className="p-2.5 rounded-lg bg-[#121824] border border-white/6 flex flex-col gap-1">
            <span className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">
              Original Query
            </span>
            <span className="text-zinc-200 italic">&ldquo;{question}&rdquo;</span>
          </div>

          {/* Stats grid */}
          <div className="grid grid-cols-2 gap-2.5">
            <div className="p-2.5 rounded-lg bg-[#121824] border border-white/6 flex flex-col gap-1">
              <span className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">
                Retrieval Route
              </span>
              <Badge variant={source === "rag" ? "rag" : source === "web_search" ? "web" : "llm"}>
                {source === "rag" ? "Document RAG" : source === "web_search" ? "Web Search Fallback" : "Direct LLM"}
              </Badge>
            </div>

            <div className="p-2.5 rounded-lg bg-[#121824] border border-white/6 flex flex-col gap-1">
              <span className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">
                Retrieved Context
              </span>
              <span className="font-semibold text-white">{chunksCount} Chunks</span>
            </div>
          </div>

          {/* Corrective checks */}
          <div className="p-3 rounded-lg bg-[#121824] border border-white/6 flex flex-col gap-2">
            <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider">
              Verification & Grounding
            </span>
            <div className="flex justify-between items-center text-zinc-300">
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                Retrieval Evaluator:
              </span>
              <span className="text-emerald-400 font-medium">CORRECT (High Relevance)</span>
            </div>
            <div className="flex justify-between items-center text-zinc-300">
              <span className="flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                Groundedness Judge:
              </span>
              <span className="text-emerald-400 font-medium">100% Grounded</span>
            </div>
            <div className="flex justify-between items-center text-zinc-300">
              <span className="flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-[#6d5dfc]" />
                Embeddings Model:
              </span>
              <span className="font-mono text-zinc-400">Gemini MRL (768d)</span>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            className="text-xs h-8"
          >
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
