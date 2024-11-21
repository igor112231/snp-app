"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

const PairPage = () => {
  const [mutantSequence, setMutantSequence] = useState("");
  const [wildSequence, setWildSequence] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
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
      router.push(`/pair/${responseData.analysis_id}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "An unknown error occurred");
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

      {error && <p style={{ color: "red", textAlign: "center" }}>{error}</p>}
    </div>
  );
};

export default PairPage;
