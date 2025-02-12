import React, { useState, useRef } from "react";
import axios from "axios";
import { QRCodeCanvas } from "qrcode.react";

function VotingPage() {
  const [selectedCandidate, setSelectedCandidate] = useState("");
  const [qrCode, setQrCode] = useState("");
  const qrRef = useRef();

  const handleVote = async () => {
    if (!selectedCandidate) {
      alert("Please select a candidate.");
      return;
    }

    try {
      const response = await axios.post("http://127.0.0.1:5000/store_vote", {
        voter_id: "123",
        candidate: selectedCandidate
      });

      setQrCode(response.data.qrCode);
    } catch (error) {
      console.error("Error storing vote:", error);
      alert("Failed to store vote.");
    }
  };

  // Function to Download QR Code
  const downloadQRCode = () => {
    const canvas = qrRef.current.querySelector("canvas");
    const qrUrl = canvas.toDataURL("image/png"); // Convert to Image URL

    const link = document.createElement("a");
    link.href = qrUrl;
    link.download = "vote_qr.png";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div>
      <h1>Secure Visual Cryptography Voting</h1>
      <label>Select Candidate:</label>
      <select onChange={(e) => setSelectedCandidate(e.target.value)}>
        <option value="">-- Choose --</option>
        <option value="Candidate A">Candidate A</option>
        <option value="Candidate B">Candidate B</option>
      </select>
      <button onClick={handleVote}>Vote</button>

      {qrCode && (
        <div>
          <h3>Your Vote Share (QR Code)</h3>
          <div ref={qrRef}>
            <QRCodeCanvas value={qrCode} size={200} />
          </div>
          <button onClick={downloadQRCode}>Download QR Code</button>
        </div>
      )}
    </div>
  );
}

export default VotingPage;
