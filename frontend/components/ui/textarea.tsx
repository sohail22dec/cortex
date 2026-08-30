import * as React from "react";
import { cn } from "@/lib/utils";

const Textarea = React.forwardRef<
  HTMLTextAreaElement,
  React.TextareaHTMLAttributes<HTMLTextAreaElement>
>(({ className, ...props }, ref) => {
  return (
    <textarea
      className={cn(
        "flex min-h-[60px] w-full rounded-lg border border-white/8 bg-[#121824] px-3 py-2 text-sm text-zinc-200 placeholder:text-zinc-500 transition-colors focus-visible:outline-none focus-visible:border-[#6d5dfc] focus-visible:ring-1 focus-visible:ring-[#6d5dfc] disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      ref={ref}
      {...props}
    />
  );
});
Textarea.displayName = "Textarea";

export { Textarea };
