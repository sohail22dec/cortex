"use client";

import React, { useState } from "react";
import {
  Sheet,
  SheetContent,
  SheetTitle,
} from "@/components/ui/sheet";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Search,
  SlidersHorizontal,
  Trash2,
  FileText,
  Upload,
} from "lucide-react";
import { DocumentCard } from "./DocumentCard";
import { DocumentUpload } from "./DocumentUpload";
import { DocumentPreview, DocumentInfo } from "./DocumentPreview";
import { DeleteConfirmDialog } from "./DeleteConfirmDialog";
import { ManageDeletedDialog, DeletedDocInfo } from "./ManageDeletedDialog";
import { toast } from "sonner";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface DocumentsDrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  documents: DocumentInfo[];
  sessionId: string;
  onDocumentUploaded: (filename: string, chunks: number, sizeMb: string) => void;
  onDocumentDeleted: (filename: string) => void;
  onUseInChat?: (filename: string) => void;
}

export function DocumentsDrawer({
  open,
  onOpenChange,
  documents,
  sessionId,
  onDocumentUploaded,
  onDocumentDeleted,
  onUseInChat,
}: DocumentsDrawerProps) {
  const [activeTab, setActiveTab] = useState("my-documents");
  const [searchQuery, setSearchQuery] = useState("");
  const [isUploading, setIsUploading] = useState(false);

  // Modal states
  const [previewDoc, setPreviewDoc] = useState<DocumentInfo | null>(null);
  const [docToDelete, setDocToDelete] = useState<string | null>(null);
  const [manageDeletedOpen, setManageDeletedOpen] = useState(false);
  const [deletedDocs, setDeletedDocs] = useState<DeletedDocInfo[]>([]);


  const filteredDocs = documents.filter((d) =>
    d.filename.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleDeleteConfirm = async () => {
    if (!docToDelete) return;
    const targetFile = docToDelete;
    try {
      const res = await fetch(
        `${API_URL}/api/documents/${encodeURIComponent(targetFile)}?session_id=${sessionId}`,
        { method: "DELETE" }
      );
      if (res.ok) {
        onDocumentDeleted(targetFile);
        const deletedItem = documents.find((d) => d.filename === targetFile);
        setDeletedDocs((prev) => [
          {
            filename: targetFile,
            deletedAt: "Just now",
            sizeMb: deletedItem?.sizeMb || "2.1 MB",
          },
          ...prev,
        ]);
        toast.success(`Removed ${targetFile} from knowledge base`);
      } else {
        toast.error("Failed to delete document");
      }
    } catch {
      toast.error("Network error deleting document");
    } finally {
      setDocToDelete(null);
    }
  };

  const handleRestore = (filename: string) => {
    setDeletedDocs((prev) => prev.filter((d) => d.filename !== filename));
    onDocumentUploaded(filename, 120, "2.0 MB");
  };

  const handlePurge = (filename: string) => {
    setDeletedDocs((prev) => prev.filter((d) => d.filename !== filename));
  };

  // Calculate total storage
  const totalMb = documents
    .reduce((acc, d) => {
      const num = parseFloat(d.sizeMb || "2.4");
      return acc + (isNaN(num) ? 2.4 : num);
    }, 0)
    .toFixed(1);

  return (
    <>
      <Sheet open={open} onOpenChange={onOpenChange}>
        <SheetContent side="right" className="flex flex-col p-0 bg-[#0a0d14] border-white/8 w-full sm:max-w-[420px]">
          {/* Header */}
          <div className="p-5 pb-3 border-b border-white/8 flex items-center justify-between shrink-0">
            <SheetTitle className="text-base font-semibold text-white flex items-center gap-2">
              <FileText className="w-4 h-4 text-[#9d93ff]" />
              Documents
            </SheetTitle>
          </div>

          {/* Body Tabs */}
          <div className="flex-1 flex flex-col min-h-0 p-5 pt-2">
            <Tabs
              value={activeTab}
              onValueChange={setActiveTab}
              className="flex-1 flex flex-col min-h-0"
            >
              <TabsList className="grid grid-cols-2 mb-3">
                <TabsTrigger value="my-documents">My Documents</TabsTrigger>
                <TabsTrigger value="upload-new">Upload New</TabsTrigger>
              </TabsList>

              <TabsContent value="my-documents" className="flex-1 flex flex-col min-h-0 mt-0">
                {/* Search & Filter Bar */}
                <div className="flex items-center gap-2 mb-3 shrink-0">
                  <div className="relative flex-1">
                    <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 pointer-events-none" />
                    <Input
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="Search documents..."
                      className="pl-8.5 h-9 bg-[#121824] border-white/6 text-xs text-zinc-200 placeholder:text-zinc-500 rounded-xl"
                    />
                  </div>
                  <Button
                    variant="outline"
                    size="icon"
                    className="h-9 w-9 rounded-xl border-white/6 bg-[#121824] text-zinc-400 hover:text-white shrink-0"
                    title="Filters"
                  >
                    <SlidersHorizontal className="w-3.5 h-3.5" />
                  </Button>
                </div>

                {/* Documents List */}
                <ScrollArea className="flex-1 -mr-2 pr-2">
                  <div className="flex flex-col gap-2">
                    {filteredDocs.length === 0 ? (
                      <div className="py-12 flex flex-col items-center justify-center text-center gap-2 text-zinc-500 px-4">
                        <FileText className="w-8 h-8 opacity-40 text-[#6d5dfc]" />
                        <span className="text-xs font-medium text-zinc-300">
                          {searchQuery ? "No documents found" : "No documents uploaded yet"}
                        </span>
                        <p className="text-[11px] text-zinc-500 max-w-[200px]">
                          {searchQuery
                            ? "Try refining your search terms"
                            : "Upload PDFs, DOCX, or text files to ground your chats"}
                        </p>
                        {!searchQuery && (
                          <Button
                            size="sm"
                            onClick={() => setActiveTab("upload-new")}
                            className="mt-2 bg-[#6d5dfc] hover:bg-[#7f70ff] text-xs h-7 rounded-lg"
                          >
                            <Upload className="w-3 h-3 mr-1.5" />
                            Upload Now
                          </Button>
                        )}
                      </div>
                    ) : (
                      filteredDocs.map((doc) => (
                        <DocumentCard
                          key={doc.filename}
                          doc={doc}
                          sessionId={sessionId}
                          onPreview={(d) => setPreviewDoc(d)}
                          onDelete={(f) => setDocToDelete(f)}
                          onUseInChat={onUseInChat}
                        />
                      ))
                    )}
                  </div>
                </ScrollArea>
              </TabsContent>

              <TabsContent value="upload-new" className="flex-1 flex flex-col mt-0 pt-2">
                <DocumentUpload
                  sessionId={sessionId}
                  onUploaded={(filename, chunks, sizeMb) => {
                    onDocumentUploaded(filename, chunks, sizeMb);
                    setActiveTab("my-documents");
                  }}
                  isUploading={isUploading}
                  setIsUploading={setIsUploading}
                />
              </TabsContent>
            </Tabs>
          </div>

          {/* Footer Stats & Manage Deleted */}
          <div className="p-4 border-t border-white/8 bg-[#0d111a] flex flex-col gap-2.5 shrink-0">
            <div className="flex items-center justify-between text-[11px] text-zinc-400 font-mono">
              <span>Total {documents.length} documents</span>
              <span>{totalMb} MB used</span>
            </div>

            <Button
              variant="outline"
              onClick={() => setManageDeletedOpen(true)}
              className="w-full h-9 rounded-xl border-white/8 bg-[#121824] hover:bg-[#161f30] text-zinc-300 text-xs font-medium flex items-center justify-center gap-2 transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5 text-zinc-500" />
              Manage deleted documents
            </Button>
          </div>
        </SheetContent>
      </Sheet>

      {/* Preview Dialog */}
      <DocumentPreview
        open={!!previewDoc}
        document={previewDoc}
        sessionId={sessionId}
        onOpenChange={(op) => !op && setPreviewDoc(null)}
        onUseInChat={onUseInChat}
      />

      {/* Delete Confirmation Alert Dialog */}
      <DeleteConfirmDialog
        open={!!docToDelete}
        filename={docToDelete || ""}
        onOpenChange={(op) => !op && setDocToDelete(null)}
        onConfirm={handleDeleteConfirm}
      />

      {/* Manage Deleted Recycle Bin Modal */}
      <ManageDeletedDialog
        open={manageDeletedOpen}
        onOpenChange={setManageDeletedOpen}
        deletedDocs={deletedDocs}
        onRestore={handleRestore}
        onPurge={handlePurge}
      />
    </>
  );
}
