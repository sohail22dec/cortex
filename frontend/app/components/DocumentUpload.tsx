"use client";
import React, { useCallback, useState } from "react";

interface DocumentUploadProps {
  sessionId: string;
  onUploaded: (filename: string, chunks: number) => void;
  isUploading: boolean;
  setIsUploading: (v: boolean) => void;
}

export default function DocumentUpload({
  sessionId,
  onUploaded,
  isUploading,
  setIsUploading,
}: DocumentUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const upload = useCallback(
    async (file: File) => {
      setError(null);
      setIsUploading(true);
      const form = new FormData();
      form.append("file", file);
      form.append("session_id", sessionId);

      try {
        const res = await fetch("http://localhost:8000/api/documents/upload", {
          method: "POST",
          body: form,
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Upload failed");
        onUploaded(data.filename, data.chunks);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Upload failed");
      } finally {
        setIsUploading(false);
      }
    },
    [sessionId, onUploaded, setIsUploading]
  );

  const handleFiles = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    upload(files[0]);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    handleFiles(e.dataTransfer.files);
  };

  return (
    <div>
      <label
        id="document-upload-zone"
        htmlFor="file-input"
        onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        className={`group flex flex-col items-center justify-center gap-2 px-4 py-6 rounded-md transition-all duration-200 text-center select-none border-2 border-dashed ${
          isDragOver ? "border-accent-primary bg-accent-soft" : "border-border bg-bg-base hover:border-border-hover"
        } ${isUploading ? "cursor-not-allowed" : "cursor-pointer"}`}
      >
        <input
          id="file-input"
          type="file"
          accept=".pdf,.docx,.doc,.txt,.md,.rst"
          onChange={(e) => handleFiles(e.target.files)}
          disabled={isUploading}
          className="hidden"
        />

        {isUploading ? (
          <>
            <div className="spinner" />
            <span className="text-[13px] text-text-muted">Indexing…</span>
          </>
        ) : (
          <>
            <div className="w-10 h-10 rounded-sm bg-accent-soft border border-border-accent flex items-center justify-center text-[18px] transition-transform duration-200 group-hover:scale-105">
              📁
            </div>
            <div>
              <p className="text-[13px] font-medium text-text-secondary">
                Drop file or <span className="text-accent-primary">click to browse</span>
              </p>
              <p className="text-[11px] text-text-muted mt-0.5">
                PDF, DOCX, TXT, MD — up to 20 MB
              </p>
            </div>
          </>
        )}
      </label>

      {error && (
        <div className="mt-2 px-3 py-2 bg-red-500/10 border border-red-500/30 rounded-sm text-[12px] text-red-400">
          ⚠️ {error}
        </div>
      )}
    </div>
  );
}
