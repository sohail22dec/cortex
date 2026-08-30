"use client";

import React from "react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

interface UserMessageProps {
  content: string;
  timestamp?: string;
}

export function UserMessage({ content, timestamp }: UserMessageProps) {
  return (
    <div className="flex items-end justify-end gap-3 mb-6 animate-fade-in">
      {/* Message Bubble + Timestamp */}
      <div className="flex items-end gap-2.5 max-w-[80%] sm:max-w-[70%]">
        {timestamp && (
          <span className="text-[11px] text-zinc-500 font-mono select-none shrink-0 mb-1">
            {timestamp}
          </span>
        )}
        <div className="rounded-2xl rounded-tr-xs bg-[#161f30] border border-white/8 px-4 py-3 text-sm text-zinc-100 leading-relaxed shadow-sm break-words">
          {content}
        </div>
      </div>

      {/* User Avatar */}
      <Avatar className="w-8 h-8 rounded-full ring-1 ring-white/10 shrink-0 mb-0.5">
        <AvatarFallback className="bg-gradient-to-br from-[#6d5dfc]/30 to-[#161f30] text-[#9d93ff] text-xs font-semibold">
          U
        </AvatarFallback>
      </Avatar>
    </div>
  );
}
