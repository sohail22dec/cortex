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
      <div
        style={{
          textAlign: "center",
          padding: "20px 12px",
          color: "var(--text-muted)",
          fontSize: "13px",
        }}
      >
        <p style={{ fontSize: "24px", marginBottom: "6px" }}>🗂️</p>
        <p>No documents uploaded yet</p>
        <p style={{ fontSize: "11px", marginTop: "4px", color: "var(--text-muted)" }}>
          Upload a file above to get started
        </p>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
      {documents.map((doc) => (
        <div
          key={doc}
          className="fade-in"
          style={{
            display: "flex",
            alignItems: "center",
            gap: "10px",
            padding: "9px 12px",
            background: "var(--bg-base)",
            border: "1px solid var(--border)",
            borderRadius: "var(--radius-sm)",
            transition: "border-color 0.2s",
          }}
          onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.borderColor = "var(--border-hover)"; }}
          onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.borderColor = "var(--border)"; }}
        >
          <span style={{ fontSize: "14px" }}>
            {doc.endsWith(".pdf") ? "📑" : doc.endsWith(".docx") || doc.endsWith(".doc") ? "📝" : "📄"}
          </span>
          <span
            style={{
              flex: 1,
              fontSize: "13px",
              color: "var(--text-secondary)",
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
            title={doc}
          >
            {doc}
          </span>
          <button
            onClick={() => handleDelete(doc)}
            disabled={deleting === doc}
            aria-label={`Delete ${doc}`}
            style={{
              background: "none",
              border: "none",
              cursor: "pointer",
              color: "var(--text-muted)",
              padding: "2px 4px",
              borderRadius: "4px",
              display: "flex",
              alignItems: "center",
              transition: "color 0.2s",
              flexShrink: 0,
            }}
            onMouseEnter={(e) => { (e.target as HTMLElement).style.color = "#f87171"; }}
            onMouseLeave={(e) => { (e.target as HTMLElement).style.color = "var(--text-muted)"; }}
          >
            {deleting === doc ? (
              <div className="spinner" style={{ width: "12px", height: "12px" }} />
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
