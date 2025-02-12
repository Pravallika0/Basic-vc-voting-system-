import React from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import VotingPage from "./VotingPage";
import VerifyVote from "./VerifyVote";

function App() {
  return (
    <Router>
      <nav>
        <Link to="/">Vote</Link>
        <Link to="/verify">Verify Vote</Link>
      </nav>
      <Routes>
        <Route path="/" element={<VotingPage />} />
        <Route path="/verify" element={<VerifyVote />} />
      </Routes>
    </Router>
  );
}

export default App;
