"use client";

import React, { useEffect, useState } from 'react';
import io from 'socket.io-client';

interface TaskStatus {
  analysis_id: string;
  status: string;
}

const HomePage = () => {
  const [mutantSequence, setMutantSequence] = useState("");
  const [wildSequence, setWildSequence] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [svgUrlMut, setSvgUrlMut] = useState<string | null>(null);
  const [svgUrlWt, setSvgUrlWt] = useState<string | null>(null);
  const [combinedText, setCombinedText] = useState<string | null>(null);

  useEffect(() => {
    const socket = io("http://localhost:8080", {
      path: "/socket.io",
      transports: ["websocket"],
      autoConnect: true,
    });

    socket.on('connect', () => {
      console.log("WebSocket connected");
    });

    socket.on("connect_error", (err: unknown) => {
      console.error("WebSocket connection error:", err);
    });

    socket.on('task_status', (data: TaskStatus) => {
      setAnalysisId(data.analysis_id);
      setMessage(data.status);
    });

    return () => {
      socket.off("task_status");
      socket.disconnect();
      console.log("WebSocket disconnected");
    };
  }, [analysisId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage("");
    setError("");

    try {
      const response = await fetch("http://localhost:8080/api/analyze/pair", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ mutantSequence, wildSequence }),
      });

      if (!response.ok) throw new Error("Failed to start analysis");

      const responseData = await response.json();
      console.log(responseData)
      setAnalysisId(responseData.analysis_id);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "An unknown error occurred");
    }
  };

  useEffect(() => {
    if (message === "Analysis completed" && analysisId) {
      fetchResults(analysisId);
      fetchResultsZIP(analysisId);
      fetchSvgUrlMut(analysisId);
      fetchSvgUrlWt(analysisId);
    }
  }, [message, analysisId]);

  const fetchResults = async (analysisId: string) => {
    try {
      const response = await fetch(`http://localhost:8080/api/results/pair/${analysisId}`);
      if (!response.ok) throw new Error("Failed to fetch combined text");

      const data = await response.json();
      setCombinedText(data.content);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "An unknown error occurred while fetching combined text");
    }
  };

  const fetchResultsZIP = async (analysisId: string) => {
    try {
      const response = await fetch(`http://localhost:8080/api/results/${analysisId}/zip-download`);
      if (!response.ok) throw new Error("Failed to fetch results");

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      setDownloadUrl(url);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "An unknown error occurred while fetching results");
    }
  };
  ///api/results/pair/<analysis_id>/rna-plot-mut
  
  const fetchSvgUrlMut = async (analysisId: string) => {
    try {
      const response = await fetch(`http://localhost:8080/api/results/pair/${analysisId}/rna-plot-mut`);
      if (!response.ok) throw new Error("Failed to fetch SVG");

      const svgUrlMut = response.url; 
      setSvgUrlMut(svgUrlMut);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "An unknown error occurred while fetching SVG");
    }
  };

  const fetchSvgUrlWt = async (analysisId: string) => {
    try {
      const response = await fetch(`http://localhost:8080/api/results/pair/${analysisId}/rna-plot-wt`);
      if (!response.ok) throw new Error("Failed to fetch SVG");

      const svgUrlWt = response.url; 
      setSvgUrlWt(svgUrlWt);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "An unknown error occurred while fetching SVG");
    }
  };

  return (
    <div style={{ width: "100%", maxWidth: "600px", margin: "0 auto", padding: "20px", backgroundColor: "#f0f0f0", border: "1px solid #ccc", borderRadius: "5px", fontFamily: "Tahoma, sans-serif" }}>
      <h1 style={{ textAlign: "center", color: "#0033cc" }}>RNA Sequence Analysis</h1>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "15px" }}>
          <label htmlFor="mutantSequence" style={{ color: "#555", display: "block", marginBottom: "5px" }}>Mutant Sequence:</label>
          <input
            type="text"
            id="mutantSequence"
            value={mutantSequence}
            onChange={(e) => setMutantSequence(e.target.value)}
            required
            style={{ width: "100%", padding: "10px", border: "1px solid #000", borderRadius: "3px", color: "#333333" }}
          />
        </div>
        <div style={{ marginBottom: "15px" }}>
          <label htmlFor="wildSequence" style={{ color: "#555", display: "block", marginBottom: "5px" }}>Wild-Type Sequence:</label>
          <input
            type="text"
            id="wildSequence"
            value={wildSequence}
            onChange={(e) => setWildSequence(e.target.value)}
            required
            style={{ width: "100%", padding: "10px", border: "1px solid #000", borderRadius: "3px", color: "#333333" }}
          />
        </div>
        <button type="submit" style={{ width: "100%", padding: "10px", backgroundColor: "#0078d4", color: "white", border: "none", borderRadius: "3px", cursor: "pointer", fontSize: "16px" }}>
          Analyze
        </button>
      </form>

      {message && <p style={{ color: "green", textAlign: "center" }}>{message}</p>}
      {error && <p style={{ color: "red", textAlign: "center" }}>{error}</p>}

      {downloadUrl && (
        <div style={{ textAlign: "center", marginTop: "20px" }}>
          <a href={downloadUrl} download={`${analysisId}.zip`} style={{ padding: "10px 20px", backgroundColor: "#28a745", color: "white", borderRadius: "5px", textDecoration: "none" }}>
            Download Results
          </a>
        </div>
      )}

      {combinedText && (
        <div style={{ marginTop: "20px", backgroundColor: "#f7f7f7", padding: "15px", border: "1px solid #ddd", borderRadius: "5px" }}>
          <h3 style={{ color: "#333" }}>Analysis Results:</h3>
          <pre style={{ color: "#333", whiteSpace: "pre-wrap", wordWrap: "break-word" }}>{combinedText}</pre>
        </div>
      )}

      
      {svgUrlMut && (
        <div style={{ marginTop: "20px", textAlign: "center" }}>
          <h3 style={{ color: "#333" }}>MUT SVG:</h3>
          <object data={svgUrlMut} type="image/svg+xml" width="600" height="400">
            
          </object>
        </div>
      )}

      {svgUrlWt && (
        <div style={{ marginTop: "20px", textAlign: "center" }}>
          <h3 style={{ color: "#333" }}>WT SVG:</h3>
          <object data={svgUrlWt} type="image/svg+xml" width="600" height="400">
            
          </object>
        </div>
      )}
    </div>
  );
};

export default HomePage;
