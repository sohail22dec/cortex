"use client";

import React from "react";
import { AppLogo } from "./AppLogo";
import { NewChatButton } from "./NewChatButton";
import { ConversationList } from "./ConversationList";
import { UserProfile } from "./UserProfile";
import { ConversationData } from "./ConversationItem";
import { cn } from "@/lib/utils";

interface SidebarProps {
  conversations: ConversationData[];
  activeChatId: string | null;
  userId: string;
  onSelectChat: (id: string) => void;
  onNewChat: () => void;
  onDeleteChat: (id: string) => void;
  onRenameChat?: (id: string, newTitle: string) => void;
  isOpen: boolean;
  onToggleOpen: () => void;
}

export function Sidebar({
  conversations,
  activeChatId,
  userId,
  onSelectChat,
  onNewChat,
  onDeleteChat,
  onRenameChat,
  isOpen,
  onToggleOpen,
}: SidebarProps) {
  return (
    <aside
      className={cn(
        "flex flex-col shrink-0 bg-[#0a0d14] border-r border-white/8 h-screen transition-all duration-300 ease-in-out select-none z-30",
        isOpen ? "w-[280px] min-w-[280px]" : "w-0 min-w-0 border-r-0 overflow-hidden"
      )}
    >
      <AppLogo
        onToggleSidebar={onToggleOpen}
        isCollapsed={!isOpen}
      />

      <NewChatButton
        onClick={onNewChat}
        isCollapsed={!isOpen}
      />

      <ConversationList
        conversations={conversations}
        activeChatId={activeChatId}
        onSelectChat={onSelectChat}
        onDeleteChat={onDeleteChat}
        onRenameChat={onRenameChat}
        isCollapsed={!isOpen}
      />

      <UserProfile userId={userId} isCollapsed={!isOpen} />
    </aside>
  );
}
