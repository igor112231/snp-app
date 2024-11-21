"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import io from "socket.io-client";

const AnalysisPage = () => {
  const { analysisId } = useParams();
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [svgUrlMut, setSvgUrlMut] = useState<string | null>(null);
  const [svgUrlWt, setSvgUrlWt] = useState<string | null>(null);
  const [svgTreeUrlMut, setTreeSvgUrlMut] = useState<string | null>(null);
  const [svgTreeUrlWt, setTreeSvgUrlWt] = useState<string | null>(null);
  const [combinedText, setCombinedText] = useState<string | null>(null);

  // Pobieranie wyników
  const fetchResults = useCallback(async () => {
    try {
      const response = await fetch(`http://localhost:8080/api/results/pair/${analysisId}`);
      if (!response.ok) throw new Error("Failed to fetch combined text");
      const data = await response.json();
      setCombinedText(data.content);
    } catch {
      setError("Failed to fetch analysis results");
    }
  }, [analysisId]);

  // Pobieranie ZIP-a
  const fetchDownloadUrl = useCallback(async () => {
    try {
      const response = await fetch(`http://localhost:8080/api/results/${analysisId}/zip-download`);
      if (!response.ok) throw new Error("Failed to fetch ZIP download");
      const blob = await response.blob();
      setDownloadUrl(URL.createObjectURL(blob));
    } catch {
      setError("Failed to fetch ZIP download");
    }
  }, [analysisId]);

  // Pobieranie SVG
  const fetchSvgUrls = useCallback(async () => {
    const endpoints = {
      svgMut: `/pair/${analysisId}/rna-plot-mut`,
      svgWt: `/pair/${analysisId}/rna-plot-wt`,
      treeMut: `/pair/${analysisId}/hit-tree_mut`,
      treeWt: `/pair/${analysisId}/hit-tree_wt`,
    };

    for (const [key, endpoint] of Object.entries(endpoints)) {
      try {
        const response = await fetch(`http://localhost:8080/api/results${endpoint}`);
        if (!response.ok) throw new Error(`Failed to fetch ${key}`);
        const url = response.url;
        if (key === "svgMut") setSvgUrlMut(url);
        if (key === "svgWt") setSvgUrlWt(url);
        if (key === "treeMut") setTreeSvgUrlMut(url);
        if (key === "treeWt") setTreeSvgUrlWt(url);
      } catch {
        setError(`Failed to fetch ${key}`);
      }
    }
  }, [analysisId]);

  // Ustawianie WebSocket i reagowanie na status
  useEffect(() => {
    const socket = io(`http://localhost:8080/${analysisId}`, {
      transports: ["websocket"],
      autoConnect: true,
    });

    socket.on(`connect`, () => {
        console.log("WebSocket connected");
    });

    socket.on("task_status", (data: { analysis_id: string; status: string }) => {
      if (data.analysis_id === analysisId) {
        setMessage(data.status);
      }
    });

    return () => {
      socket.disconnect();
    };
  }, [analysisId]);

  // Reagowanie na zakończenie analizy
  useEffect(() => {
    if (message === "Analysis completed") {
      fetchResults();
      fetchDownloadUrl();
      fetchSvgUrls();
    }
  }, [message, fetchResults, fetchDownloadUrl, fetchSvgUrls]);

return (
  <div
    style={{
      width: "100%",
      maxWidth: "600px",
      margin: "0 auto",
      padding: "20px",
      backgroundColor: "#f0f0f0",
      border: "1px solid #ccc",
      borderRadius: "5px",
      fontFamily: "Tahoma, sans-serif",
    }}
  >
    <h1 style={{ textAlign: "center", color: "#0033cc" }}>Analysis Results</h1>

    {message && <p style={{ color: "green", textAlign: "center" }}>Status: {message}</p>}
    {error && <p style={{ color: "red", textAlign: "center" }}>{error}</p>}

    {combinedText && (
      <div
        style={{
          marginTop: "20px",
          backgroundColor: "#f7f7f7",
          padding: "15px",
          border: "1px solid #ddd",
          borderRadius: "5px",
        }}
      >
        <h3 style={{ color: "#333" }}>Analysis Results:</h3>
        <pre
          style={{
            color: "#333",
            whiteSpace: "pre-wrap",
            wordWrap: "break-word",
          }}
        >
          {combinedText}
        </pre>
      </div>
    )}

    {downloadUrl && (
      <div style={{ textAlign: "center", marginTop: "20px" }}>
        <a
          href={downloadUrl}
          download={`${analysisId}.zip`}
          style={{
            padding: "10px 20px",
            backgroundColor: "#28a745",
            color: "white",
            borderRadius: "5px",
            textDecoration: "none",
          }}
        >
          Download Results
        </a>
      </div>
    )}

    {svgTreeUrlMut && (
      <div style={{ marginTop: "20px", textAlign: "center" }}>
        <h3 style={{ color: "#333" }}>TREE MUT SVG:</h3>
        <object data={svgTreeUrlMut} type="image/svg+xml" width="600" height="400" />
      </div>
    )}

    {svgTreeUrlWt && (
      <div style={{ marginTop: "20px", textAlign: "center" }}>
        <h3 style={{ color: "#333" }}>TREE WT SVG:</h3>
        <object data={svgTreeUrlWt} type="image/svg+xml" width="600" height="400" />
      </div>
    )}

    {svgUrlMut && (
      <div style={{ marginTop: "20px", textAlign: "center" }}>
        <h3 style={{ color: "#333" }}>MUT SVG:</h3>
        <object data={svgUrlMut} type="image/svg+xml" width="600" height="400" />
      </div>
    )}

    {svgUrlWt && (
      <div style={{ marginTop: "20px", textAlign: "center" }}>
        <h3 style={{ color: "#333" }}>WT SVG:</h3>
        <object data={svgUrlWt} type="image/svg+xml" width="600" height="400" />
      </div>
    )}
  </div>
);

};

export default AnalysisPage;
