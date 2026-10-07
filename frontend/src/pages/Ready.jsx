import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Ready.css";
import { apiFetch, getCandidateToken } from "../api";

function Ready() {
  const navigate = useNavigate();
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState("");

  const startInterview = async () => {
    if (starting) return;

    let cameraStream = null;
    let screenStream = null;

    try {
      setStarting(true);
      setError("");

      const interviewId = localStorage.getItem(
      "candidate_interview_id"
      );

      const token = getCandidateToken();

      if (!interviewId || !token) {
        throw new Error(
          "Candidate session is missing. Please open the interview link again."
        );
      }

      // Ask for camera + microphone.
      // Ask for screen sharing first.
// This must happen directly from the START INTERVIEW button.
screenStream = await navigator.mediaDevices.getDisplayMedia({
  video: true,
  audio: false,
});

// Then ask for camera + microphone.
cameraStream = await navigator.mediaDevices.getUserMedia({
  video: {
    width: { ideal: 1280 },
    height: { ideal: 720 },
  },
  audio: true,
});

      // Save the valid streams for the interview page.
      window.interviewCameraStream = cameraStream;
      window.interviewScreenStream = screenStream;

      // Start the backend interview.
      await apiFetch(
        `/candidate/interviews/${interviewId}/start`,
        {
          method: "POST",
        },
        token
      );

      // Fullscreen AFTER camera/screen permission requests.
      if (document.documentElement.requestFullscreen) {
        try {
          await document.documentElement.requestFullscreen();
        } catch (fullscreenError) {
          console.warn(
            "Fullscreen could not be enabled:",
            fullscreenError
          );
        }
      }

      navigate("/interview/session");
    } catch (err) {
      console.error("Unable to start interview:", err);

      // Clean up streams if something failed.
      if (cameraStream) {
        cameraStream.getTracks().forEach((track) => track.stop());
      }

      if (screenStream) {
        screenStream.getTracks().forEach((track) => track.stop());
      }

      window.interviewCameraStream = null;
      window.interviewScreenStream = null;

      setError(
        err.message ||
          "Camera, microphone, and screen sharing are required."
      );

      setStarting(false);
    }
  };

  return (
    <div className="ready-page">
      <div className="ready-card">
        <h1>Ready for Interview?</h1>

        <p>Your interview is about to begin.</p>

        <div className="ready-info">
          <p>📷 Camera access is required</p>
          <p>🎤 Microphone access is required</p>
          <p>🖥️ Screen sharing is required</p>
          <p>⛶ Interview will run in full screen</p>
          <p>🔴 Interview will be monitored in real time</p>
          <p>🤖 AI analysis runs while the interview is active</p>
        </div>

        {error && (
          <p style={{ color: "#dc2626" }}>
            {error}
          </p>
        )}

        <button
          type="button"
          onClick={startInterview}
          disabled={starting}
        >
          {starting ? "STARTING..." : "START INTERVIEW"}
        </button>
      </div>
    </div>
  );
}

export default Ready;
