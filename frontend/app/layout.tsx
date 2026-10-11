import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RAG - upload and ask",
  description: "Document Q&A powered by FastAPI and Google Gemini",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
