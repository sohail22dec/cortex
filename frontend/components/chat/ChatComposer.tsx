"use client";

import React, { useRef, useEffect } from "react";
import {
  Paperclip,
  Send,
} from "lucide-react";
import { Button } from "@/components/ui/button";

interface ChatComposerProps {
  value: string;
  onChange: (v: string) => void;
  onSend: (text?: string) => void;
  isLoading: boolean;
  onOpenDocuments?: () => void;
  hasDocuments?: boolean;
}

export function ChatComposer({
  value,
  onChange,
  onSend,
  isLoading,
  onOpenDocuments,
}: ChatComposerProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea up to max height
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = `${Math.min(ta.scrollHeight, 180)}px`;
  }, [value]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Enter sends message.
    // Shift + Enter inserts new line.
    if (e.key === "Enter" && !e.shiftKey && !e.ctrlKey) {
      e.preventDefault();
      if (!isLoading && value.trim()) {
        onSend(value.trim());
      }
    }
  };

  const handleSendClick = () => {
    if (!isLoading && value.trim()) {
      onSend(value.trim());
    }
  };

  const canSend = value.trim().length > 0 && !isLoading;

  return (
    <div className="w-full max-w-[800px] mx-auto px-4 pb-4 pt-2">
      <div className="rounded-2xl bg-[#0d111a] border border-white/10 shadow-2xl focus-within:border-[#6d5dfc]/50 focus-within:shadow-[0_0_24px_rgba(109,93,252,0.15)] transition-all duration-300 p-3.5 flex flex-col gap-3">
        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything about your documents..."
          disabled={isLoading}
          rows={1}
          className="w-full bg-transparent border-0 outline-none text-zinc-100 text-sm placeholder:text-zinc-500 resize-none max-h-[180px] overflow-y-auto leading-relaxed py-1 px-1 font-sans"
        />

        {/* Toolbar & Send Button */}
        <div className="flex items-center justify-between pt-1 border-t border-white/6">
          {/* Left Toolbar: Attach / Open Documents */}
          <div className="flex items-center gap-1 text-zinc-400">
            <button
              type="button"
              onClick={onOpenDocuments}
              className="p-2 rounded-lg hover:bg-[#161f30] hover:text-white transition-colors cursor-pointer"
              title="Knowledge Base Documents"
            >
              <Paperclip className="w-4 h-4" />
            </button>
          </div>

          {/* Right: Send Button */}
          <Button
            onClick={handleSendClick}
            disabled={!canSend}
            className={`h-9 px-4 rounded-xl font-medium text-xs flex items-center gap-2 transition-all duration-200 ${
              canSend
                ? "bg-[#6d5dfc] hover:bg-[#7f70ff] text-white shadow-md shadow-[#6d5dfc]/25 cursor-pointer active:scale-[0.98]"
                : "bg-[#161f30] text-zinc-500 border border-white/6 cursor-not-allowed opacity-60"
            }`}
          >
            {isLoading ? (
              <div className="spinner w-3.5 h-3.5 border-t-white" />
            ) : (
              <>
                <span>Send</span>
                <Send className="w-3.5 h-3.5" />
              </>
            )}
          </Button>
        </div>
      </div>

      <p className="mt-2 text-[11px] text-zinc-400 text-center font-normal tracking-wide select-none">
        Cortex can make mistakes. Check important info.
      </p>
    </div>
  );
}
