import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { apiFetch } from "../api";

export default function Candidate() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const interviewId = searchParams.get("interview");
  const token = searchParams.get("token");

  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleLogin(e) {
    e.preventDefault();

    setError("");

    if (!interviewId || !token) {
      setError("Invalid interview invitation link.");
      return;
    }

    if (!email.trim()) {
      setError("Please enter your email.");
      return;
    }

    try {
      setLoading(true);

      const response = await apiFetch("/candidate/login", {
        method: "POST",
        body: JSON.stringify({
        interview_id: interviewId,
        invitation_token: token,
        email: email.trim(),
        }),
      });
      localStorage.setItem("candidate_access_token", response.access_token);
      localStorage.setItem("candidate_interview_id", response.interview_id);

      if (response.access_token) {
        localStorage.setItem(
          "candidate_access_token",
          response.access_token
        );
      }

      if (response.interview_id) {
        localStorage.setItem(
          "candidate_interview_id",
          response.interview_id
        );
      } else {
        localStorage.setItem(
          "candidate_interview_id",
          interviewId
        );
      }

      navigate("/ready");

    } catch (err) {
  console.error("FULL CANDIDATE LOGIN ERROR:", err);

  let message = "Candidate login failed.";

  try {
    if (typeof err === "string") {
      message = err;
    } else if (err && typeof err === "object") {
      if (err.detail !== undefined) {
        message =
          typeof err.detail === "string"
            ? err.detail
            : JSON.stringify(err.detail);
      } else if (err.message !== undefined) {
        message =
          typeof err.message === "string"
            ? err.message
            : JSON.stringify(err.message);
      } else {
        message = JSON.stringify(err);
      }
    } else {
      message = String(err);
    }
  } catch (formatError) {
    message = String(err);
  }

  setError(message);
} finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "#f5f7fb",
        padding: "20px",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "420px",
          background: "white",
          padding: "32px",
          borderRadius: "16px",
          boxShadow: "0 10px 30px rgba(0,0,0,0.08)",
        }}
      >
        <h1 style={{ marginBottom: "8px" }}>
          InterviewGuard
        </h1>

        <p style={{ color: "#666", marginBottom: "24px" }}>
          Candidate Interview Login
        </p>

        <form onSubmit={handleLogin}>
          <label
            style={{
              display: "block",
              marginBottom: "8px",
              fontWeight: 600,
            }}
          >
            Email
          </label>

          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your invited email"
            required
            style={{
              width: "100%",
              boxSizing: "border-box",
              padding: "12px",
              border: "1px solid #ccc",
              borderRadius: "8px",
              marginBottom: "16px",
            }}
          />

          {error && (
  <div
    style={{
      background: "#fee2e2",
      color: "#b91c1c",
      padding: "10px",
      borderRadius: "8px",
      marginBottom: "16px",
      whiteSpace: "pre-wrap",
    }}
  >
    {String(error)}
  </div>
)}

          <button
            type="submit"
            disabled={loading}
            style={{
              width: "100%",
              padding: "12px",
              border: "none",
              borderRadius: "8px",
              background: "#111827",
              color: "white",
              cursor: loading ? "not-allowed" : "pointer",
              opacity: loading ? 0.7 : 1,
            }}
          >
            {loading ? "Checking..." : "Continue"}
          </button>
        </form>
      </div>
    </div>
  );
}