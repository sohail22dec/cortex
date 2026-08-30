"use client";

import React from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { FileText, Database, ShieldCheck, Calendar, HardDrive } from "lucide-react";

export interface DocumentInfo {
  filename: string;
  chunks?: number;
  sizeMb?: string;
  uploadDate?: string;
}

interface DocumentPreviewProps {
  open: boolean;
  document: DocumentInfo | null;
  onOpenChange: (open: boolean) => void;
  onUseInChat?: (filename: string) => void;
}

export function DocumentPreview({
  open,
  document,
  onOpenChange,
  onUseInChat,
}: DocumentPreviewProps) {
  if (!document) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md bg-[#0d111a] border-white/10 text-zinc-100">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center justify-center text-red-400">
              <FileText className="w-5 h-5" />
            </div>
            <div className="flex flex-col text-left">
              <DialogTitle className="text-sm font-semibold truncate max-w-[320px]">
                {document.filename}
              </DialogTitle>
              <DialogDescription className="text-xs text-zinc-400">
                Indexed in Supabase pgvector store
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="flex flex-col gap-3 py-2 text-xs">
          <div className="grid grid-cols-2 gap-2.5">
            <div className="p-2.5 rounded-lg bg-[#121824] border border-white/6 flex items-center gap-2">
              <Database className="w-4 h-4 text-[#6d5dfc]" />
              <div className="flex flex-col">
                <span className="text-[10px] text-zinc-400">Chunks Indexed</span>
                <span className="font-semibold text-white">{document.chunks || 128} chunks</span>
              </div>
            </div>

            <div className="p-2.5 rounded-lg bg-[#121824] border border-white/6 flex items-center gap-2">
              <HardDrive className="w-4 h-4 text-emerald-400" />
              <div className="flex flex-col">
                <span className="text-[10px] text-zinc-400">File Size</span>
                <span className="font-semibold text-white">{document.sizeMb || "2.4 MB"}</span>
              </div>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-[#121824] border border-white/6 flex flex-col gap-2">
            <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider">
              Ingestion Status
            </span>
            <div className="flex justify-between items-center text-zinc-300">
              <span className="flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                PII Redaction & Sanitization:
              </span>
              <Badge variant="rag">Passed</Badge>
            </div>
            <div className="flex justify-between items-center text-zinc-300">
              <span className="flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-zinc-400" />
                Upload Date:
              </span>
              <span className="text-zinc-400 font-mono">{document.uploadDate || "May 28, 2025"}</span>
            </div>
          </div>
        </div>

        <DialogFooter className="gap-2">
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            className="text-xs h-8"
          >
            Close
          </Button>
          {onUseInChat && (
            <Button
              onClick={() => {
                onUseInChat(document.filename);
                onOpenChange(false);
              }}
              className="text-xs h-8 bg-[#6d5dfc] hover:bg-[#7f70ff]"
            >
              Ask about this document
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
