"use client";

import React from "react";
import { Sparkles, PanelLeftClose } from "lucide-react";
import { Button } from "@/components/ui/button";

interface AppLogoProps {
  onToggleSidebar?: () => void;
  isCollapsed?: boolean;
}

export function AppLogo({ onToggleSidebar, isCollapsed = false }: AppLogoProps) {
  return (
    <div className="flex items-center justify-between px-4 py-3.5 border-b border-white/8 shrink-0">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-[#6d5dfc] to-[#9d93ff] flex items-center justify-center text-white shadow-md shadow-[#6d5dfc]/25 shrink-0">
          <Sparkles className="w-4 h-4 fill-white" />
        </div>
        {!isCollapsed && (
          <div className="flex flex-col">
            <span className="text-[15px] font-bold tracking-tight text-white flex items-center gap-1.5">
              Coretext
            </span>
            <span className="text-[10px] font-medium text-zinc-400">
              Corrective RAG
            </span>
          </div>
        )}
      </div>

      {onToggleSidebar && !isCollapsed && (
        <Button
          variant="ghost"
          size="icon-sm"
          onClick={onToggleSidebar}
          className="text-zinc-400 hover:text-zinc-200"
          title="Toggle sidebar"
        >
          <PanelLeftClose className="w-4 h-4" />
        </Button>
      )}
    </div>
  );
}
