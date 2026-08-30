"use client";

import React from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

interface UserProfileProps {
  userId: string;
  isCollapsed?: boolean;
}

export function UserProfile({ userId, isCollapsed = false }: UserProfileProps) {
  if (isCollapsed) {
    return (
      <div className="p-2.5 flex justify-center border-t border-white/8">
        <Avatar className="w-8 h-8 ring-1 ring-white/15">
          <AvatarImage src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80" />
          <AvatarFallback className="bg-[#161f30] text-[#6d5dfc] text-xs font-semibold">
            SI
          </AvatarFallback>
        </Avatar>
      </div>
    );
  }

  return (
    <div className="px-3.5 py-3 border-t border-white/8 flex items-center justify-between shrink-0 bg-[#0a0d14]/60">
      <div className="flex items-center gap-2.5 min-w-0">
        <Avatar className="w-8 h-8 rounded-full ring-1 ring-white/15 shrink-0">
          <AvatarImage src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80" />
          <AvatarFallback className="bg-[#161f30] text-[#6d5dfc] text-xs font-semibold">
            SI
          </AvatarFallback>
        </Avatar>
        <div className="flex flex-col min-w-0">
          <span className="text-xs font-semibold text-white truncate">
            Sohel Islam
          </span>
          <span className="text-[11px] text-zinc-400 truncate">
            sohel@example.com
          </span>
        </div>
      </div>
      <span className="text-[9px] text-zinc-400 font-mono">
        {userId.slice(0, 6)}
      </span>
    </div>
  );
}
