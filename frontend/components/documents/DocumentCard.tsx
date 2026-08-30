"use client";

import React from "react";
import {
  FileText,
  MoreVertical,
  Eye,
  MessageSquarePlus,
  Download,
  Trash2,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { DocumentInfo } from "./DocumentPreview";
import { toast } from "sonner";

interface DocumentCardProps {
  doc: DocumentInfo;
  onPreview: (doc: DocumentInfo) => void;
  onDelete: (filename: string) => void;
  onUseInChat?: (filename: string) => void;
}

export function DocumentCard({
  doc,
  onPreview,
  onDelete,
  onUseInChat,
}: DocumentCardProps) {
  const isPdf = doc.filename.toLowerCase().endsWith(".pdf");
  const isDocx = doc.filename.toLowerCase().endsWith(".docx") || doc.filename.toLowerCase().endsWith(".doc");

  const handleDownload = () => {
    toast.info(`Downloading ${doc.filename}...`);
  };

  return (
    <div className="group flex items-center justify-between p-3 rounded-xl bg-[#121824] border border-white/6 hover:border-white/15 hover:bg-[#161f30] transition-all duration-200">
      <div
        className="flex items-center gap-3 min-w-0 flex-1 cursor-pointer pr-2"
        onClick={() => onPreview(doc)}
      >
        {/* File Icon Badge */}
        <div
          className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 border ${
            isPdf
              ? "bg-red-500/10 border-red-500/20 text-red-400"
              : isDocx
              ? "bg-blue-500/10 border-blue-500/20 text-blue-400"
              : "bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
          }`}
        >
          <FileText className="w-4.5 h-4.5" />
        </div>

        {/* File Info */}
        <div className="flex flex-col min-w-0 flex-1">
          <span
            className="text-xs font-semibold text-zinc-100 truncate group-hover:text-white transition-colors"
            title={doc.filename}
          >
            {doc.filename}
          </span>
          <div className="flex items-center gap-1.5 text-[11px] text-zinc-400 font-normal mt-0.5">
            <span>{doc.chunks || 128} chunks</span>
            <span>•</span>
            <span>{doc.sizeMb || "2.4 MB"}</span>
          </div>
          <span className="text-[10px] text-zinc-500 mt-0.5">
            {doc.uploadDate || "May 28, 2025"}
          </span>
        </div>
      </div>

      {/* Action Menu */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-white/10 transition-colors focus:outline-none cursor-pointer">
            <MoreVertical className="w-4 h-4" />
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-44">
          <DropdownMenuItem onClick={() => onPreview(doc)}>
            <Eye className="w-3.5 h-3.5 mr-2 text-zinc-400" />
            Preview details
          </DropdownMenuItem>
          {onUseInChat && (
            <DropdownMenuItem onClick={() => onUseInChat(doc.filename)}>
              <MessageSquarePlus className="w-3.5 h-3.5 mr-2 text-zinc-400" />
              Use in chat
            </DropdownMenuItem>
          )}
          <DropdownMenuItem onClick={handleDownload}>
            <Download className="w-3.5 h-3.5 mr-2 text-zinc-400" />
            Download
          </DropdownMenuItem>
          <DropdownMenuItem
            onClick={() => onDelete(doc.filename)}
            className="text-red-400 focus:text-red-400 focus:bg-red-500/10"
          >
            <Trash2 className="w-3.5 h-3.5 mr-2" />
            Delete document
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
