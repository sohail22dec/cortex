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
import { FileText, RotateCcw, Trash2 } from "lucide-react";
import { toast } from "sonner";

export interface DeletedDocInfo {
  filename: string;
  deletedAt: string;
  sizeMb: string;
}

interface ManageDeletedDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  deletedDocs: DeletedDocInfo[];
  onRestore: (filename: string) => void;
  onPurge: (filename: string) => void;
}

export function ManageDeletedDialog({
  open,
  onOpenChange,
  deletedDocs,
  onRestore,
  onPurge,
}: ManageDeletedDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md bg-[#0d111a] border-white/10 text-zinc-100">
        <DialogHeader>
          <DialogTitle className="text-base font-semibold">Deleted Documents</DialogTitle>
          <DialogDescription className="text-xs text-zinc-400">
            Restore previously removed documents to your knowledge base or delete them permanently.
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-2 py-2 max-h-[300px] overflow-y-auto">
          {deletedDocs.length === 0 ? (
            <div className="py-8 text-center text-xs text-zinc-500 italic">
              Trash is empty. No deleted documents.
            </div>
          ) : (
            deletedDocs.map((doc) => (
              <div
                key={doc.filename}
                className="flex items-center justify-between p-2.5 rounded-lg bg-[#121824] border border-white/6"
              >
                <div className="flex items-center gap-2.5 min-w-0 flex-1 pr-2">
                  <FileText className="w-4 h-4 text-zinc-500 shrink-0" />
                  <div className="flex flex-col min-w-0">
                    <span className="text-xs font-medium text-zinc-300 truncate">
                      {doc.filename}
                    </span>
                    <span className="text-[10px] text-zinc-500 font-mono">
                      Deleted: {doc.deletedAt} • {doc.sizeMb}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-1 shrink-0">
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => {
                      onRestore(doc.filename);
                      toast.success(`Restored ${doc.filename}`);
                    }}
                    className="h-7 px-2 text-[11px] flex items-center gap-1"
                    title="Restore document"
                  >
                    <RotateCcw className="w-3 h-3" />
                    Restore
                  </Button>
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => {
                      onPurge(doc.filename);
                      toast.success(`Permanently deleted ${doc.filename}`);
                    }}
                    className="h-7 w-7 p-0"
                    title="Permanently delete"
                  >
                    <Trash2 className="w-3 h-3" />
                  </Button>
                </div>
              </div>
            ))
          )}
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            className="text-xs h-8"
          >
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
