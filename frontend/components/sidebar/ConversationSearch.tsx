"use client";

import React from "react";
import { Search } from "lucide-react";

interface ConversationSearchProps {
  value: string;
  onChange: (v: string) => void;
  isCollapsed?: boolean;
}

export function ConversationSearch({
  value,
  onChange,
  isCollapsed = false,
}: ConversationSearchProps) {
  if (isCollapsed) return null;

  return (
    <div className="px-3 py-2">
      <div className="relative flex items-center">
        <Search className="w-3.5 h-3.5 absolute left-3 text-zinc-500 pointer-events-none" />
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Search conversations..."
          className="w-full h-8.5 rounded-lg bg-[#121824] border border-white/6 pl-8 pr-8 text-xs text-zinc-200 placeholder:text-zinc-500 focus:outline-none focus:border-[#6d5dfc]/60 focus:ring-1 focus:ring-[#6d5dfc]/40 transition-colors"
        />
        <span className="absolute right-2.5 text-[10px] text-zinc-500 font-mono select-none">
          ⌘ F
        </span>
      </div>
    </div>
  );
}
