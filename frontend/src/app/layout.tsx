import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RAG Workspace | Multi-source research",
  description: "Search your documents, sales records, and the web with traceable evidence in one workspace.",
  robots: { index: false, follow: false },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
