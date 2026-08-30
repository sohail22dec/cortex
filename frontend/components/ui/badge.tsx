import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-[#6d5dfc] text-white",
        secondary:
          "border-white/10 bg-[#161f30] text-zinc-300",
        destructive:
          "border-red-500/20 bg-red-500/10 text-red-400",
        outline: "text-zinc-300 border-white/15",
        accent:
          "border-[#6d5dfc]/30 bg-[#6d5dfc]/15 text-[#9d93ff]",
        rag:
          "border-emerald-500/30 bg-emerald-500/10 text-emerald-400",
        llm:
          "border-blue-500/30 bg-blue-500/10 text-blue-400",
        web:
          "border-amber-500/30 bg-amber-500/10 text-amber-400",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
