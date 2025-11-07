import React, { useEffect, useState } from "react";

function App() {
  const [sensorData, setSensorData] = useState({ temperature: "-", humidity: "-" });

  useEffect(() => {
    // Connect to WebSocket
    const ws = new WebSocket("ws://10.159.26.165:8000/ws/sensor/");

    ws.onopen = () => {
      console.log("Connected to sensor WebSocket");
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setSensorData(data);
      } catch (err) {
        console.error("Error parsing sensor data:", err);
      }
    };

    ws.onclose = () => {
      console.log("WebSocket closed, reconnecting in 5s...");
      setTimeout(() => window.location.reload(), 5000); // simple reconnect
    };

    ws.onerror = (err) => {
      console.error("WebSocket error:", err);
      ws.close();
    };

    return () => ws.close();
  }, []);

  return (
    <div style={{ textAlign: "center", background: "#111", color: "white", minHeight: "100vh", padding: "20px" }}>
      <h1>IoT Dashboard</h1>

      <h2>Live Camera Feed</h2>
      <img
        src="http://10.175.107.165:8000/video-feed/"
        alt="Live Feed"
        width="640"
        height="480"
        style={{ border: "2px solid white", marginBottom: "20px" }}
      />

      <h2>Sensor Data</h2>
      <pre style={{ textAlign: "left", display: "inline-block", background: "#222", padding: "10px", borderRadius: "8px" }}>
        {JSON.stringify(sensorData, null, 2)}
      </pre>
    </div>
  );
}

export default App;
