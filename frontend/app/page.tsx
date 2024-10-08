//Ustalić język komentarzy
"use client";

import { useState, useEffect } from "react";
import { io } from "socket.io-client";


const HomePage = () => {
    const [mutantSequence, setMutantSequence] = useState("");
    const [wildSequence, setWildSequence] = useState("");
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");
    const [wsError, setWsError] = useState("");

    useEffect(() => {
        
        const socket = io("http://localhost:8080", {
            transports: ['websocket'] // Wymuszenie WebSocket
        });

        socket.on("connect", () => {
            console.log("WebSocket is connected");
        });

        socket.on("message", (data) => {
            console.log("Message from server: ", data);
        });

        socket.on("error", (error) => {
            console.error("WebSocket error: ", error);
            setWsError("WebSocket connection error");
        });

        socket.on("disconnect", () => {
            console.log("WebSocket connection closed");
        });

        
        return () => {
            socket.disconnect();
        };
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        setMessage("");
        setError("");
        setWsError("");

        const data = {
            mutantSequence,
            wildSequence,
        };

        // Wysyłanie zapytania do backendu
        try {
            const response = await fetch("http://localhost:8080/api/analyze", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(data),
            });

            if (!response.ok) {
                throw new Error("Failed to start analysis");
            }

            const responseData = await response.json();
            setMessage(`${responseData.result}`);
        } catch (err: unknown) {
            if (err instanceof Error) {
                setError(err.message);
            } else {
                setError("An unknown error occurred");
            }
        }
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
