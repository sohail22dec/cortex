"use client";

import React, { useState, useCallback } from "react";
import { UploadCloud, AlertCircle } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface DocumentUploadProps {
  sessionId: string;
  onUploaded: (filename: string, chunks: number, sizeMb: string) => void;
  isUploading: boolean;
  setIsUploading: (v: boolean) => void;
}

export function DocumentUpload({
  sessionId,
  onUploaded,
  isUploading,
  setIsUploading,
}: DocumentUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [currentFileName, setCurrentFileName] = useState("");
  const [error, setError] = useState<string | null>(null);

  const uploadFile = useCallback(
    async (file: File) => {
      setError(null);
      setIsUploading(true);
      setCurrentFileName(file.name);
      setUploadProgress(15);

      const form = new FormData();
      form.append("file", file);
      form.append("session_id", sessionId);

      const progressTimer = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 85) return prev;
          return prev + 15;
        });
      }, 300);

      try {
        const res = await fetch(`${API_URL}/api/documents/upload`, {
          method: "POST",
          body: form,
        });

        clearInterval(progressTimer);
        const data = await res.json();

        if (!res.ok) {
          throw new Error(data.detail || "Document upload failed");
        }

        setUploadProgress(100);
        const sizeMb = `${(file.size / (1024 * 1024)).toFixed(1)} MB`;
        onUploaded(data.filename, data.chunks, sizeMb);
        toast.success(`Indexed ${data.filename} (${data.chunks} chunks)`);
      } catch (err: unknown) {
        clearInterval(progressTimer);
        const msg = err instanceof Error ? err.message : "Upload failed";
        setError(msg);
        toast.error(`Upload error: ${msg}`);
      } finally {
        setTimeout(() => {
          setIsUploading(false);
          setUploadProgress(0);
          setCurrentFileName("");
        }, 600);
      }
    },
    [sessionId, onUploaded, setIsUploading]
  );

  const handleFiles = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    uploadFile(files[0]);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    handleFiles(e.dataTransfer.files);
  };

  return (
    <div className="flex flex-col gap-3">
      <label
        htmlFor="doc-drawer-file-input"
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        className={`group relative flex flex-col items-center justify-center gap-3 p-6 rounded-2xl border-2 border-dashed transition-all duration-200 text-center select-none ${
          isDragOver
            ? "border-[#6d5dfc] bg-[#6d5dfc]/10"
            : "border-white/10 bg-[#121824]/50 hover:border-white/20 hover:bg-[#121824]"
        } ${isUploading ? "cursor-not-allowed opacity-80" : "cursor-pointer"}`}
      >
        <input
          id="doc-drawer-file-input"
          type="file"
          accept=".pdf,.docx,.doc,.txt,.md,.rst"
          onChange={(e) => handleFiles(e.target.files)}
          disabled={isUploading}
          className="hidden"
        />

        {isUploading ? (
          <div className="w-full flex flex-col items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-[#6d5dfc]/15 border border-[#6d5dfc]/30 flex items-center justify-center text-[#6d5dfc]">
              <div className="spinner w-5 h-5 border-t-[#6d5dfc]" />
            </div>
            <div className="flex flex-col items-center gap-1 w-full max-w-[240px]">
              <span className="text-xs font-semibold text-white truncate max-w-[200px]">
                {currentFileName}
              </span>
              <span className="text-[11px] text-zinc-400">
                {uploadProgress < 100 ? "Processing & Generating Embeddings..." : "Finished indexing!"}
              </span>
              <Progress value={uploadProgress} className="h-1.5 mt-1 bg-black/40" />
            </div>
          </div>
        ) : (
          <>
            <div className="w-12 h-12 rounded-2xl bg-[#6d5dfc]/10 border border-[#6d5dfc]/20 flex items-center justify-center text-[#9d93ff] group-hover:scale-105 transition-transform">
              <UploadCloud className="w-6 h-6" />
            </div>
            <div className="flex flex-col gap-1">
              <p className="text-xs font-semibold text-zinc-200">
                Upload documents
              </p>
              <p className="text-[11px] text-zinc-400">
                Drag & drop or <span className="text-[#9d93ff] underline underline-offset-2">browse files</span>
              </p>
            </div>
            <div className="flex items-center gap-2 text-[10px] text-zinc-500">
              <span>PDF</span> • <span>DOCX</span> • <span>TXT</span> • <span>MD</span> (Max 20MB)
            </div>
          </>
        )}
      </label>

      {error && (
        <div className="flex items-center gap-2 p-2.5 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-xs">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span className="truncate">{error}</span>
        </div>
      )}
    </div>
  );
}
