"use client";

import { Toaster as Sonner } from "sonner";

type ToasterProps = React.ComponentProps<typeof Sonner>;

const Toaster = ({ ...props }: ToasterProps) => {
  return (
    <Sonner
      theme="dark"
      className="toaster group"
      toastOptions={{
        classNames: {
          toast:
            "group toast group-[.toaster]:bg-[#0d111a] group-[.toaster]:text-zinc-100 group-[.toaster]:border-white/10 group-[.toaster]:shadow-2xl group-[.toaster]:rounded-xl font-sans text-xs",
          description: "group-[.toast]:text-zinc-400",
          actionButton:
            "group-[.toast]:bg-[#6d5dfc] group-[.toast]:text-white",
          cancelButton:
            "group-[.toast]:bg-[#161f30] group-[.toast]:text-zinc-400",
        },
      }}
      {...props}
    />
  );
};

export { Toaster };
