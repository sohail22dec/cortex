"use client";

import React from "react";
import { Upload, ArrowRight, FileText, Brain, Globe } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CoretextLogo } from "@/components/ui/CoretextLogo";

interface EmptyStateProps {
  onSelectPrompt: (prompt: string) => void;
  onOpenDocuments: () => void;
}

const STARTER_PROMPTS = [
  "What is RAG and how does it work?",
  "Explain LangGraph with example",
  "Best practices for chunking documents",
  "Difference between RAG and Fine-tuning",
  "Search the web for latest AI news",
];

export function EmptyState({
  onSelectPrompt,
  onOpenDocuments,
}: EmptyStateProps) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center py-10 px-4 max-w-[760px] mx-auto text-center animate-fade-in select-none">
      {/* Brand Icon */}
      <CoretextLogo size="lg" className="mb-5" />

      {/* Hero Title */}
      <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white mb-2">
        Welcome to Coretext
      </h1>
      <p className="text-xs sm:text-sm text-zinc-400 max-w-[460px] mb-8 leading-relaxed">
        Ask questions about your knowledge base with transparent Corrective RAG, real-time web search, and AI reasoning.
      </p>

      {/* 3 Pillars */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full mb-8 text-left">
        <div className="p-4 rounded-xl bg-[#0d111a] border border-white/6 hover:border-white/12 transition-all">
          <div className="w-8 h-8 rounded-lg bg-red-500/10 border border-red-500/20 flex items-center justify-center text-red-400 mb-2.5">
            <FileText className="w-4 h-4" />
          </div>
          <span className="text-xs font-semibold text-white block mb-1">Document RAG</span>
          <p className="text-[11px] text-zinc-400 leading-relaxed">
            Index PDFs, DOCX, and TXT files into Supabase pgvector store.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-[#0d111a] border border-white/6 hover:border-white/12 transition-all">
          <div className="w-8 h-8 rounded-lg bg-[#6d5dfc]/10 border border-[#6d5dfc]/20 flex items-center justify-center text-[#9d93ff] mb-2.5">
            <Brain className="w-4 h-4" />
          </div>
          <span className="text-xs font-semibold text-white block mb-1">Corrective Evaluator</span>
          <p className="text-[11px] text-zinc-400 leading-relaxed">
            Evaluates retrieved chunk relevance and triggers strict grounding checks.
          </p>
        </div>

        <div className="p-4 rounded-xl bg-[#0d111a] border border-white/6 hover:border-white/12 transition-all">
          <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 mb-2.5">
            <Globe className="w-4 h-4" />
          </div>
          <span className="text-xs font-semibold text-white block mb-1">Real-time Web Search</span>
          <p className="text-[11px] text-zinc-400 leading-relaxed">
            Falls back to live Tavily web search when documents lack coverage.
          </p>
        </div>
      </div>

      {/* Upload button or starter prompts */}
      <div className="flex flex-col items-center gap-3 w-full">
        <Button
          onClick={onOpenDocuments}
          className="h-9 px-4 rounded-xl bg-[#6d5dfc] hover:bg-[#7f70ff] text-white text-xs font-medium flex items-center gap-2 shadow-lg shadow-[#6d5dfc]/20"
        >
          <Upload className="w-3.5 h-3.5" />
          Upload Documents to Knowledge Base
        </Button>

        <div className="mt-4 flex flex-col items-center gap-2 w-full">
          <span className="text-[10px] uppercase font-semibold text-zinc-400 tracking-wider">
            Suggested starter queries
          </span>
          <div className="flex flex-wrap justify-center gap-2 max-w-[620px]">
            {STARTER_PROMPTS.map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => onSelectPrompt(prompt)}
                className="px-3.5 py-1.5 rounded-full bg-[#121824] hover:bg-[#161f30] border border-white/6 hover:border-[#6d5dfc]/40 text-xs text-zinc-300 hover:text-white transition-all cursor-pointer flex items-center gap-1.5 group"
              >
                <span>{prompt}</span>
                <ArrowRight className="w-3 h-3 text-zinc-500 group-hover:text-[#9d93ff] transition-transform group-hover:translate-x-0.5" />
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
