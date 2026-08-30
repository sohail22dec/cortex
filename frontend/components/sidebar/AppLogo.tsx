"use client";

import React from "react";
import { CoretextLogo } from "@/components/ui/CoretextLogo";

interface AppLogoProps {
  isCollapsed?: boolean;
}

export function AppLogo({ isCollapsed = false }: AppLogoProps) {
  return (
    <div className="flex items-center px-4 py-3.5 border-b border-white/8 shrink-0">
      <div className="flex items-center gap-3">
        <CoretextLogo size="md" />
        {!isCollapsed && (
          <div className="flex flex-col">
            <span className="text-[15px] font-bold tracking-tight text-white">
              Coretext
            </span>
            <span className="text-[10px] font-medium text-zinc-400">
              Corrective RAG
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
