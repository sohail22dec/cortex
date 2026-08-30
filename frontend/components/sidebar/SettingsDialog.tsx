"use client";

import React, { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

interface SettingsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  userId: string;
}

export function SettingsDialog({
  open,
  onOpenChange,
  userId,
}: SettingsDialogProps) {
  const [userName, setUserName] = useState("Sohel Islam");
  const [userEmail, setUserEmail] = useState("sohel@example.com");

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md bg-[#0d111a] border-white/10 text-zinc-100">
        <DialogHeader>
          <DialogTitle className="text-base font-semibold">Settings & Preferences</DialogTitle>
          <DialogDescription className="text-xs text-zinc-400">
            Configure your local profile and system settings.
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-4 py-2 text-xs">
          {/* User Info */}
          <div className="flex flex-col gap-2">
            <label className="text-zinc-300 font-medium">Display Name</label>
            <Input
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              className="h-8.5 bg-[#121824] text-xs"
            />
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-zinc-300 font-medium">Email Address</label>
            <Input
              value={userEmail}
              onChange={(e) => setUserEmail(e.target.value)}
              className="h-8.5 bg-[#121824] text-xs"
            />
          </div>

          {/* System Specs */}
          <div className="rounded-lg bg-[#121824] p-3 border border-white/6 flex flex-col gap-2">
            <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider">
              System Architecture
            </span>
            <div className="flex justify-between items-center text-zinc-300">
              <span>Pipeline:</span>
              <Badge variant="accent">Corrective RAG (CRAG)</Badge>
            </div>
            <div className="flex justify-between items-center text-zinc-300">
              <span>Vector Store:</span>
              <span className="font-mono text-zinc-400">Supabase pgvector (768d)</span>
            </div>
            <div className="flex justify-between items-center text-zinc-300">
              <span>Session ID:</span>
              <span className="font-mono text-zinc-400">{userId.slice(0, 12)}...</span>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            className="text-xs h-8"
          >
            Close
          </Button>
          <Button
            onClick={() => onOpenChange(false)}
            className="text-xs h-8 bg-[#6d5dfc] hover:bg-[#7f70ff]"
          >
            Save Changes
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
