"use client";

import { useState, useEffect } from "react";

const DEFAULT_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [apiUrl, setApiUrl] = useState(DEFAULT_URL);
  const [isOnline, setIsOnline] = useState<boolean | null>(null);

  // Upload state
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedInfo, setUploadedInfo] = useState<{ filename: string; chunks: number } | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Ask question state
  const [question, setQuestion] = useState("");
  const [isAsking, setIsAsking] = useState(false);
  const [answer, setAnswer] = useState<string | null>(null);
  const [sources, setSources] = useState<string[]>([]);
  const [askError, setAskError] = useState<string | null>(null);
  const [showSources, setShowSources] = useState(false);

  // Check health and current status on mount
  useEffect(() => {
    const saved = localStorage.getItem("RAG_API_URL") || DEFAULT_URL;
    setApiUrl(saved);
    checkHealth(saved);
  }, []);

  const checkHealth = async (url: string) => {
    try {
      const res = await fetch(`${url.replace(/\/$/, "")}/health`);
      if (res.ok) {
        const data = await res.json();
        setIsOnline(true);
        if (data.uploaded_file) {
          setUploadedInfo({ filename: data.uploaded_file, chunks: 0 });
        }
      } else {
        setIsOnline(false);
      }
    } catch {
      setIsOnline(false);
    }
  };

  const handleApiUrlChange = (newUrl: string) => {
    setApiUrl(newUrl);
    localStorage.setItem("RAG_API_URL", newUrl);
    checkHealth(newUrl);
  };

  // Upload handler
  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setIsUploading(true);
    setUploadError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${apiUrl.replace(/\/$/, "")}/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed");

      setUploadedInfo({ filename: data.filename, chunks: data.chunks });
      setFile(null);
      setAnswer(null);
      setQuestion("");
      setSources([]);
    } catch (err: any) {
      setUploadError(err.message || "Failed to upload file");
    } finally {
      setIsUploading(false);
    }
  };

  // Reset / Change document handler
  const handleReset = async () => {
    try {
      await fetch(`${apiUrl.replace(/\/$/, "")}/reset`, { method: "POST" });
    } catch {}
    setUploadedInfo(null);
    setFile(null);
    setAnswer(null);
    setQuestion("");
    setSources([]);
  };

  // Ask handler
  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setIsAsking(true);
    setAskError(null);
    setAnswer(null);

    try {
      const res = await fetch(`${apiUrl.replace(/\/$/, "")}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question.trim() }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Query failed");

      setAnswer(data.answer);
      setSources(data.sources || []);
    } catch (err: any) {
      setAskError(err.message || "Failed to get answer");
    } finally {
      setIsAsking(false);
    }
  };

  return (
    <main className="container">
      {/* Step 1: Upload Document */}
      <section className="card">
        <h2 className="card-title">Upload Document</h2>
        <p className="card-subtitle">
          {uploadedInfo
            ? "Your document is active. Click 'Change File' to replace it with a new one."
            : "Upload your PDF or TXT file to ask questions from."}
        </p>

        {uploadedInfo ? (
          <div className="active-document-box">
            <div className="active-doc-info">
              <span className="active-doc-icon">📄</span>
              <div>
                <span className="active-doc-name">{uploadedInfo.filename}</span>
                <span className="active-doc-chunks">
                  {uploadedInfo.chunks > 0 ? `${uploadedInfo.chunks} searchable chunks indexed` : "Active in memory"}
                </span>
              </div>
            </div>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleReset}
            >
              Change File
            </button>
          </div>
        ) : (
          <form onSubmit={handleUpload} className="upload-area">
            <div className="file-input-wrapper">
              <input
                type="file"
                accept=".pdf,.txt"
                className="file-input"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
            </div>
            <button type="submit" className="btn" disabled={!file || isUploading}>
              {isUploading ? "Uploading..." : "Upload File"}
            </button>
          </form>
        )}

        {uploadError && <div className="upload-error">✗ {uploadError}</div>}
      </section>

      {/* Step 2: Ask Questions */}
      <section className="card">
        <h2 className="card-title">Ask Questions</h2>
        <p className="card-subtitle">
          {uploadedInfo
            ? `Ask any question based on ${uploadedInfo.filename}:`
            : "Please upload a document above first."}
        </p>

        <form onSubmit={handleAsk} className="ask-form">
          <textarea
            className="ask-textarea"
            placeholder="e.g. What are the key findings discussed in this document?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={!uploadedInfo}
          />
          <button
            type="submit"
            className="btn"
            disabled={!uploadedInfo || !question.trim() || isAsking}
          >
            {isAsking ? "Thinking..." : "Ask Question"}
          </button>
        </form>

        {askError && <div className="upload-error" style={{ marginTop: 16 }}>✗ {askError}</div>}

        {answer && (
          <div className="answer-box">
            <div className="answer-header">Answer:</div>
            <div className="answer-text">{answer}</div>

            {sources.length > 0 && (
              <div className="sources-accordion">
                <span
                  className="sources-title"
                  onClick={() => setShowSources(!showSources)}
                >
                  {showSources ? "▼ Hide Sources" : `▶ View Referenced Snippets (${sources.length})`}
                </span>
                {showSources && (
                  <div>
                    {sources.map((s, idx) => (
                      <div key={idx} className="source-item">
                        {s}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </section>
    </main>
  );
}
