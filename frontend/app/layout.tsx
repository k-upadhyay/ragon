import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Simple RAG — Upload & Ask",
  description: "Simple document Q&A powered by FastAPI and Google Gemini",
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
