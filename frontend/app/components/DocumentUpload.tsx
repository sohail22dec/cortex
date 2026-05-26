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
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: "8px",
          padding: "24px 16px",
          border: `2px dashed ${isDragOver ? "var(--accent-primary)" : "var(--border)"}`,
          borderRadius: "var(--radius-md)",
          background: isDragOver ? "var(--accent-soft)" : "var(--bg-base)",
          cursor: isUploading ? "not-allowed" : "pointer",
          transition: "all 0.2s",
          textAlign: "center",
          userSelect: "none",
        }}
      >
        <input
          id="file-input"
          type="file"
          accept=".pdf,.docx,.doc,.txt,.md,.rst"
          onChange={(e) => handleFiles(e.target.files)}
          disabled={isUploading}
          style={{ display: "none" }}
        />

        {isUploading ? (
          <>
            <div className="spinner" />
            <span style={{ fontSize: "13px", color: "var(--text-muted)" }}>Indexing…</span>
          </>
        ) : (
          <>
            <div
              style={{
                width: "40px",
                height: "40px",
                borderRadius: "var(--radius-sm)",
                background: "var(--accent-soft)",
                border: "1px solid var(--border-accent)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "18px",
                transition: "transform 0.2s",
              }}
            >
              📁
            </div>
            <div>
              <p style={{ fontSize: "13px", fontWeight: 500, color: "var(--text-secondary)" }}>
                Drop file or <span style={{ color: "var(--accent-primary)" }}>click to browse</span>
              </p>
              <p style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "2px" }}>
                PDF, DOCX, TXT, MD — up to 20 MB
              </p>
            </div>
          </>
        )}
      </label>

      {error && (
        <div
          style={{
            marginTop: "8px",
            padding: "8px 12px",
            background: "rgba(239, 68, 68, 0.1)",
            border: "1px solid rgba(239, 68, 68, 0.3)",
            borderRadius: "var(--radius-sm)",
            fontSize: "12px",
            color: "#f87171",
          }}
        >
          ⚠️ {error}
        </div>
      )}
    </div>
  );
}
