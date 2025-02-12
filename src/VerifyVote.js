import React, { useState } from "react";
import axios from "axios";
import { useDropzone } from "react-dropzone";

function VerifyVote() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState("");

  const { getRootProps, getInputProps } = useDropzone({
    accept: "image/png",
    onDrop: (acceptedFiles) => {
      setFile(acceptedFiles[0]);
    }
  });

  const handleVerify = async () => {
    if (!file) {
      alert("Please upload your vote share.");
      return;
    }

    const formData = new FormData();
    formData.append("vote_share", file);
    formData.append("voter_id", "123");

    try {
      const response = await axios.post("http://localhost:5000/verify_vote", formData);
      setResult(response.data.message);
    } catch (error) {
      console.error("Error verifying vote:", error);
      setResult("Verification failed.");
    }
  };

  return (
    <div>
      <h1>Verify Your Vote</h1>
      <div {...getRootProps()} className="dropzone">
        <input {...getInputProps()} />
        <p>Drag & drop your vote share here, or click to select a file</p>
      </div>

      {file && <p>Uploaded: {file.name}</p>}

      <button onClick={handleVerify}>Verify Vote</button>

      {result && <h3>Result: {result}</h3>}
    </div>
  );
}

export default VerifyVote;
