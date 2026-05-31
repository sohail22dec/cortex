import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Cortex — Multi-Agent RAG Assistant",
  description:
    "Upload your documents and ask questions. Cortex intelligently routes your queries across RAG, direct LLM knowledge, and real-time web search.",
  keywords: ["RAG", "AI", "document assistant", "multi-agent", "Groq", "Supabase"],
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>{children}</body>
    </html>
  );
}
