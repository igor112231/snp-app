"use client";

import { useState, useEffect } from "react";
import { io } from "socket.io-client";

const socket = io("http://localhost:8080", {
    transports: ['websocket'], // Ensure it's using WebSocket
    withCredentials: true, // Allow cookies for cross-origin requests
    extraHeaders: {
        "Access-Control-Allow-Origin": "http://localhost:3000", // Allow specific origin
    },
});

const HomePage = () => {
    const [mutantSequence, setMutantSequence] = useState("");
    const [wildSequence, setWildSequence] = useState("");
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");
    const [wsError, setWsError] = useState("");

    useEffect(() => {
        socket.on("connect", () => {
            console.log("WebSocket connected");
        });

        socket.on("analysis_started", () => {
            console.log("Analysis started");
            setMessage("Analysis started"); // Set message when analysis starts
        });

        socket.on("analysis_completed", (data) => {
            console.log("Analysis completed: ", data);
            setMessage(`RNApdist result: ${data.rnapdist_result}`);
        });

        socket.on("analysis_failed", (data) => {
            console.error("Analysis failed: ", data.error);
            setError(`Error: ${data.error}`);
        });

        socket.on("disconnect", () => {
            console.log("WebSocket connection closed");
        });

        // Clean up the socket connection when the component unmounts
        return () => {
            socket.disconnect();
        };
    }, []);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        setMessage("");
        setError("");
        setWsError("");

        const data = {
            mutantSequence,
            wildSequence,
        };

        // Use the existing socket connection to send data
        socket.emit("analyze", data);
    };

    return (
        <div style={{ width: "100%", maxWidth: "600px", margin: "0 auto", padding: "20px", backgroundColor: "#f0f0f0", border: "1px solid #ccc", borderRadius: "5px", fontFamily: "Tahoma, sans-serif" }}>
            <h1 style={{ textAlign: "center", color: "#0033cc" }}>RNA Sequence Analysis</h1>
            <form onSubmit={handleSubmit}>
                <div style={{ marginBottom: "15px" }}>
                    <label htmlFor="mutantSequence" style={{ display: "block", marginBottom: "5px" }}>Mutant Sequence:</label>
                    <p style={{ fontSize: "14px", color: "#555" }}>Enter the sequence of the mutant RNA.</p>
                    <input
                        type="text"
                        id="mutantSequence"
                        value={mutantSequence}
                        onChange={(e) => setMutantSequence(e.target.value)}
                        required
                        style={{ width: "100%", padding: "10px", border: "1px solid #000", borderRadius: "3px" }}
                    />
                </div>
                <div style={{ marginBottom: "15px" }}>
                    <label htmlFor="wildSequence" style={{ display: "block", marginBottom: "5px" }}>Wild-Type Sequence:</label>
                    <p style={{ fontSize: "14px", color: "#555" }}>Enter the sequence of the wild-type RNA.</p>
                    <input
                        type="text"
                        id="wildSequence"
                        value={wildSequence}
                        onChange={(e) => setWildSequence(e.target.value)}
                        required
                        style={{ width: "100%", padding: "10px", border: "1px solid #000", borderRadius: "3px" }}
                    />
                </div>
                <button type="submit" style={{ width: "100%", padding: "10px", backgroundColor: "#0078d4", color: "white", border: "none", borderRadius: "3px", cursor: "pointer", fontSize: "16px" }}>
                    Analyze
                </button>
            </form>
            {message && <p style={{ color: "green", textAlign: "center" }}>{message}</p>}
            {error && <p style={{ color: "red", textAlign: "center" }}>{error}</p>}
            {wsError && <p style={{ color: "red", textAlign: "center" }}>{wsError}</p>}
        </div>
    );
};

export default HomePage;
