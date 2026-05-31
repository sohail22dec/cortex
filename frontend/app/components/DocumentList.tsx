"use client";
import React, { useState } from "react";

interface DocumentListProps {
  documents: string[];
  sessionId: string;
  onDeleted: (filename: string) => void;
}

export default function DocumentList({ documents, sessionId, onDeleted }: DocumentListProps) {
  const [deleting, setDeleting] = useState<string | null>(null);

  const handleDelete = async (filename: string) => {
    setDeleting(filename);
    try {
      const res = await fetch(
        `http://localhost:8000/api/documents/${encodeURIComponent(filename)}?session_id=${sessionId}`,
        { method: "DELETE" }
      );
      if (res.ok) onDeleted(filename);
    } catch {
      // ignore
    } finally {
      setDeleting(null);
    }
  };

  if (documents.length === 0) {
    return (
      <div className="text-center px-3 py-5 text-text-muted text-[13px]">
        <p className="text-[24px] mb-1.5">🗂️</p>
        <p>No documents uploaded yet</p>
        <p className="text-[11px] mt-1 text-text-muted">
          Upload a file above to get started
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-1.5">
      {documents.map((doc) => (
        <div
          key={doc}
          className="fade-in group flex items-center gap-2.5 px-3 py-2 bg-bg-base border border-border rounded-sm transition-colors duration-200 hover:border-border-hover"
        >
          <span className="text-[14px]">
            {doc.endsWith(".pdf") ? "📑" : doc.endsWith(".docx") || doc.endsWith(".doc") ? "📝" : "📄"}
          </span>
          <span
            className="flex-1 text-[13px] text-text-secondary overflow-hidden text-ellipsis whitespace-nowrap"
            title={doc}
          >
            {doc}
          </span>
          <button
            onClick={() => handleDelete(doc)}
            disabled={deleting === doc}
            aria-label={`Delete ${doc}`}
            className="bg-transparent border-none cursor-pointer text-text-muted px-1 py-0.5 rounded flex items-center transition-colors duration-200 shrink-0 hover:text-red-400 disabled:cursor-not-allowed"
          >
            {deleting === doc ? (
              <div className="spinner w-3 h-3" />
            ) : (
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <polyline points="3 6 5 6 21 6" />
                <path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6" />
                <path d="M10 11v6M14 11v6" />
                <path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2" />
              </svg>
            )}
          </button>
        </div>
      ))}
    </div>
  );
}
