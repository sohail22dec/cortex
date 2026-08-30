"use client";

import React from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";

interface NewChatButtonProps {
  onClick: () => void;
  isCollapsed?: boolean;
}

export function NewChatButton({ onClick, isCollapsed = false }: NewChatButtonProps) {
  if (isCollapsed) {
    return (
      <Button
        onClick={onClick}
        variant="accent"
        size="icon"
        className="w-9 h-9 rounded-xl mx-auto my-2 shrink-0"
        title="New Chat"
      >
        <Plus className="w-4 h-4" />
      </Button>
    );
  }

  return (
    <div className="px-3 pt-3 pb-2">
      <Button
        onClick={onClick}
        className="w-full h-10 rounded-xl bg-gradient-to-r from-[#6d5dfc] to-[#7f70ff] hover:from-[#7b6cff] hover:to-[#8c7fff] text-white font-medium text-[13px] shadow-md shadow-[#6d5dfc]/20 border border-[#6d5dfc]/40 flex items-center justify-center gap-2 px-3.5 transition-all duration-200"
      >
        <Plus className="w-4 h-4" />
        <span>New Chat</span>
      </Button>
    </div>
  );
}
