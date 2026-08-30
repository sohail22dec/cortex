"use client";

import React from "react";
import { ConversationItem, ConversationData } from "./ConversationItem";
import { ScrollArea } from "@/components/ui/scroll-area";

interface ConversationListProps {
  conversations: ConversationData[];
  activeChatId: string | null;
  onSelectChat: (id: string) => void;
  onDeleteChat: (id: string) => void;
  onRenameChat?: (id: string, newTitle: string) => void;
  isCollapsed?: boolean;
}

export function ConversationList({
  conversations,
  activeChatId,
  onSelectChat,
  onDeleteChat,
  onRenameChat,
  isCollapsed = false,
}: ConversationListProps) {
  return (
    <div className="flex-1 flex flex-col min-h-0 w-full min-w-0 overflow-hidden">
      {!isCollapsed && (
        <div className="px-4 pt-3 pb-1.5 flex items-center justify-between shrink-0">
          <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider">
            Conversations
          </span>
          <span className="text-[10px] text-zinc-500 font-mono">
            {conversations.length}
          </span>
        </div>
      )}

      <ScrollArea className="flex-1 px-3 py-1 w-full min-w-0">
        <div className="flex flex-col gap-1 w-full min-w-0">
          {conversations.length === 0 ? (
            <div className="py-8 text-center text-xs text-zinc-500 italic px-2">
              No chats yet. Start a new chat!
            </div>
          ) : (
            conversations.map((chat) => (
              <ConversationItem
                key={chat.id}
                chat={chat}
                isActive={chat.id === activeChatId}
                onSelect={onSelectChat}
                onDelete={onDeleteChat}
                onRename={onRenameChat}
                isCollapsed={isCollapsed}
              />
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
