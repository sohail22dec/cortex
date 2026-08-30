"use client";

import React, { useState } from "react";
import {
  ChevronsUpDown,
  Settings,
  LogOut,
} from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { SettingsDialog } from "./SettingsDialog";
import { toast } from "sonner";

interface UserProfileProps {
  userId: string;
  isCollapsed?: boolean;
}

export function UserProfile({ userId, isCollapsed = false }: UserProfileProps) {
  const [settingsOpen, setSettingsOpen] = useState(false);

  const handleSignOut = () => {
    toast.info("Signed out of local session");
  };

  if (isCollapsed) {
    return (
      <>
        <div className="p-2.5 flex justify-center border-t border-white/8">
          <Avatar
            className="w-8 h-8 cursor-pointer hover:ring-2 hover:ring-[#6d5dfc] transition-all"
            onClick={() => setSettingsOpen(true)}
          >
            <AvatarFallback className="bg-gradient-to-br from-[#6d5dfc]/30 to-[#161f30] text-[#9d93ff] border border-[#6d5dfc]/40 text-xs font-semibold">
              SI
            </AvatarFallback>
          </Avatar>
        </div>
        <SettingsDialog
          open={settingsOpen}
          onOpenChange={setSettingsOpen}
          userId={userId}
        />
      </>
    );
  }

  return (
    <>
      <div className="p-3 border-t border-white/8 bg-[#0a0d14] shrink-0">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="w-full flex items-center justify-between p-2.5 rounded-xl bg-[#121824]/60 border border-white/6 hover:bg-[#121824] hover:border-white/12 transition-all text-left group focus:outline-none cursor-pointer">
              <div className="flex items-center gap-3 min-w-0">
                <Avatar className="w-8 h-8 rounded-lg shrink-0">
                  <AvatarFallback className="bg-gradient-to-br from-[#6d5dfc]/30 to-[#161f30] text-[#9d93ff] border border-[#6d5dfc]/40 text-xs font-semibold">
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
              <ChevronsUpDown className="w-3.5 h-3.5 text-zinc-500 group-hover:text-zinc-300 transition-colors shrink-0" />
            </button>
          </DropdownMenuTrigger>

          <DropdownMenuContent
            align="start"
            side="top"
            sideOffset={8}
            className="w-[256px] rounded-xl bg-[#0d111a] border border-white/10 shadow-2xl p-1.5 mb-1"
          >
            {/* Header info */}
            <div className="flex items-center gap-2.5 px-2.5 py-2">
              <Avatar className="w-8 h-8 rounded-lg shrink-0">
                <AvatarFallback className="bg-gradient-to-br from-[#6d5dfc]/30 to-[#161f30] text-[#9d93ff] border border-[#6d5dfc]/40 text-xs font-semibold">
                  SI
                </AvatarFallback>
              </Avatar>
              <div className="flex flex-col min-w-0">
                <span className="text-xs font-semibold text-white truncate">
                  Sohel Islam
                </span>
                <span className="text-[10px] text-zinc-400 font-mono truncate">
                  sohel@example.com
                </span>
              </div>
            </div>

            <DropdownMenuSeparator className="bg-white/8 my-1" />

            {/* Menu Items */}
            <DropdownMenuItem
              onClick={() => setSettingsOpen(true)}
              className="text-xs cursor-pointer text-zinc-300 hover:text-white focus:text-white px-2.5 py-2 rounded-lg"
            >
              <Settings className="w-4 h-4 mr-2.5 text-zinc-400" />
              Settings
            </DropdownMenuItem>

            <DropdownMenuSeparator className="bg-white/8 my-1" />

            <DropdownMenuItem
              onClick={handleSignOut}
              className="text-xs cursor-pointer text-red-400 focus:text-red-400 focus:bg-red-500/10 hover:bg-red-500/10 px-2.5 py-2 rounded-lg"
            >
              <LogOut className="w-4 h-4 mr-2.5" />
              Sign out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <SettingsDialog
        open={settingsOpen}
        onOpenChange={setSettingsOpen}
        userId={userId}
      />
    </>
  );
}
