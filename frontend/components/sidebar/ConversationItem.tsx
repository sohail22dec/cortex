"use client";

import React, { useState } from "react";
import { MessageSquare, MoreVertical, Trash2, Edit2, Check, X } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";

export interface ConversationData {
  id: string;
  title: string;
  createdAt: number;
  timestampStr?: string;
}

interface ConversationItemProps {
  chat: ConversationData;
  isActive: boolean;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
  onRename?: (id: string, newTitle: string) => void;
  isCollapsed?: boolean;
}

function formatRelativeTime(timestamp: number): string {
  const now = Date.now();
  const diff = now - timestamp;
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (minutes < 1) return "Just now";
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
  }
  if (days === 1) return "Yesterday";
  if (days < 7) {
    const date = new Date(timestamp);
    return date.toLocaleDateString([], { weekday: "short" });
  }
  const date = new Date(timestamp);
  return date.toLocaleDateString([], { month: "short", day: "numeric" });
}

export function ConversationItem({
  chat,
  isActive,
  onSelect,
  onDelete,
  onRename,
  isCollapsed = false,
}: ConversationItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedTitle, setEditedTitle] = useState(chat.title);

  const handleSaveRename = (e?: React.MouseEvent | React.FormEvent) => {
    if (e) e.stopPropagation();
    if (editedTitle.trim() && onRename) {
      onRename(chat.id, editedTitle.trim());
    }
    setIsEditing(false);
  };

  const handleCancelRename = (e: React.MouseEvent) => {
    e.stopPropagation();
    setEditedTitle(chat.title);
    setIsEditing(false);
  };

  if (isCollapsed) {
    return (
      <button
        onClick={() => onSelect(chat.id)}
        className={cn(
          "w-9 h-9 mx-auto my-0.5 rounded-lg flex items-center justify-center transition-colors cursor-pointer",
          isActive
            ? "bg-[#6d5dfc]/15 text-[#9d93ff] border border-[#6d5dfc]/30"
            : "text-zinc-400 hover:text-zinc-200 hover:bg-white/5"
        )}
        title={chat.title}
      >
        <MessageSquare className="w-4 h-4" />
      </button>
    );
  }

  return (
    <div
      onClick={() => onSelect(chat.id)}
      className={cn(
        "group relative flex items-center justify-between px-3 py-2.5 rounded-xl cursor-pointer transition-all duration-200 text-left border",
        isActive
          ? "bg-[#161f30] border-[#6d5dfc]/40 text-white shadow-xs"
          : "bg-transparent border-transparent hover:bg-[#121824]/80 text-zinc-300 hover:text-white"
      )}
    >
      <div className="flex items-start gap-2.5 min-w-0 flex-1 pr-2">
        <MessageSquare
          className={cn(
            "w-4 h-4 mt-0.5 shrink-0 transition-colors",
            isActive ? "text-[#9d93ff]" : "text-zinc-500 group-hover:text-zinc-400"
          )}
        />

        {isEditing ? (
          <div
            className="flex items-center gap-1 flex-1 min-w-0"
            onClick={(e) => e.stopPropagation()}
          >
            <input
              type="text"
              value={editedTitle}
              onChange={(e) => setEditedTitle(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleSaveRename();
                if (e.key === "Escape") setIsEditing(false);
              }}
              autoFocus
              className="w-full bg-[#0d111a] border border-[#6d5dfc] rounded px-1.5 py-0.5 text-xs text-white focus:outline-none"
            />
            <button
              onClick={handleSaveRename}
              className="p-1 hover:text-emerald-400 text-zinc-400"
              title="Save"
            >
              <Check className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={handleCancelRename}
              className="p-1 hover:text-red-400 text-zinc-400"
              title="Cancel"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        ) : (
          <div className="flex flex-col min-w-0 flex-1">
            <span className="text-[13px] font-medium truncate leading-tight">
              {chat.title}
            </span>
            <span className="text-[11px] text-zinc-500 font-normal mt-0.5">
              {chat.timestampStr || formatRelativeTime(chat.createdAt)}
            </span>
          </div>
        )}
      </div>

      {!isEditing && (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button
              onClick={(e) => e.stopPropagation()}
              className={cn(
                "p-1 rounded-md text-zinc-500 hover:text-white hover:bg-white/10 transition-opacity focus:outline-none",
                isActive ? "opacity-100" : "opacity-0 group-hover:opacity-100"
              )}
            >
              <MoreVertical className="w-3.5 h-3.5" />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem
              onClick={(e) => {
                e.stopPropagation();
                setIsEditing(true);
              }}
            >
              <Edit2 className="w-3.5 h-3.5 mr-2" />
              Rename
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={(e) => {
                e.stopPropagation();
                onDelete(chat.id);
              }}
              className="text-red-400 focus:text-red-400 focus:bg-red-500/10"
            >
              <Trash2 className="w-3.5 h-3.5 mr-2" />
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      )}
    </div>
  );
}
