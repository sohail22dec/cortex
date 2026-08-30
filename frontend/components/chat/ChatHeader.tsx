"use client";

import React from "react";
import {
  FileText,
  Share2,
  PanelLeft,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

interface ChatHeaderProps {
  title: string;
  docCount: number;
  onOpenDocuments: () => void;
  onToggleSidebar?: () => void;
  sidebarOpen?: boolean;
}

export function ChatHeader({
  title,
  docCount,
  onOpenDocuments,
  onToggleSidebar,
  sidebarOpen = true,
}: ChatHeaderProps) {
  const handleShare = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(window.location.href);
      toast.success("Chat link copied to clipboard");
    }
  };

  return (
    <header className="h-14 border-b border-white/8 bg-[#080b11]/80 backdrop-blur-md px-4 flex items-center justify-between shrink-0 sticky top-0 z-20">
      {/* Left: Sidebar toggle & Clean Chat Title */}
      <div className="flex items-center gap-3 min-w-0">
        {onToggleSidebar && (
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={onToggleSidebar}
            className={`text-zinc-400 hover:text-white transition-colors ${
              !sidebarOpen ? "text-[#9d93ff] bg-white/5" : ""
            }`}
            title={sidebarOpen ? "Collapse sidebar" : "Open sidebar"}
          >
            <PanelLeft className="w-4 h-4" />
          </Button>
        )}

        <h1 className="text-sm font-semibold text-white truncate max-w-[260px] sm:max-w-[480px]">
          {title || "New Chat"}
        </h1>
      </div>

      {/* Right Actions: Share & Documents */}
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon-sm"
          onClick={handleShare}
          className="text-zinc-400 hover:text-white"
          title="Share conversation"
        >
          <Share2 className="w-4 h-4" />
        </Button>

        <div className="h-4 w-[1px] bg-white/10 mx-0.5" />

        {/* Documents Drawer Trigger Button */}
        <Button
          onClick={onOpenDocuments}
          className="h-8 px-3 rounded-lg bg-[#161f30] hover:bg-[#1f2b42] text-zinc-200 border border-[#6d5dfc]/40 hover:border-[#6d5dfc] transition-all flex items-center gap-1.5 text-xs font-medium group"
          title="Documents"
        >
          <FileText className="w-3.5 h-3.5 text-[#9d93ff] group-hover:scale-105 transition-transform" />
          <span className="hidden sm:inline">Documents</span>
          {docCount > 0 && (
            <span className="ml-0.5 px-1.5 py-0.2 rounded-full bg-[#6d5dfc]/25 text-[#9d93ff] text-[10px] font-mono">
              {docCount}
            </span>
          )}
        </Button>
      </div>
    </header>
  );
}
