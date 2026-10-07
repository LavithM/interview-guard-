import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch, getCandidateToken, wsUrl } from "../api";

function encodeWav(samples, sampleRate = 16000) {
  const buffer = new ArrayBuffer(44 + samples.length * 2);
  const view = new DataView(buffer);

  const writeString = (offset, text) => {
    for (let i = 0; i < text.length; i++) {
      view.setUint8(offset + i, text.charCodeAt(i));
    }
  };

  writeString(0, "RIFF");
  view.setUint32(4, 36 + samples.length * 2, true);
  writeString(8, "WAVE");
  writeString(12, "fmt ");

  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);

  writeString(36, "data");
  view.setUint32(40, samples.length * 2, true);

  let offset = 44;

  for (let i = 0; i < samples.length; i++) {
    const sample = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(
      offset,
      sample < 0 ? sample * 0x8000 : sample * 0x7fff,
      true
    );
    offset += 2;
  }

  return new Blob([buffer], { type: "audio/wav" });
}

export default function Interview() {
  const navigate = useNavigate();

  const candidateVideoRef = useRef(null);
  const adminVideoRef = useRef(null);

  const cameraStreamRef = useRef(null);
  const screenStreamRef = useRef(null);

  const mediaRecorderRef = useRef(null);

  const audioContextRef = useRef(null);
  const audioProcessorRef = useRef(null);
  const audioSourceRef = useRef(null);
  const audioSamplesRef = useRef([]);

  const frameTimerRef = useRef(null);
  const audioTimerRef = useRef(null);
  const windowTimerRef = useRef(null);

  const endingRef = useRef(false);
  const startedRef = useRef(false);

  // ---------------------------------------------------------
  // WEBRTC
  // ---------------------------------------------------------

  const webrtcSocketRef = useRef(null);
  const peerConnectionRef = useRef(null);
  const pendingIceCandidatesRef = useRef([]);
  const remoteDescriptionSetRef = useRef(false);

  const [webrtcStatus, setWebrtcStatus] = useState("Connecting to admin...");
  const [adminConnected, setAdminConnected] = useState(false);

  const [recording, setRecording] = useState(false);
  const [error, setError] = useState("");
  const [ending, setEnding] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [aiStatus, setAiStatus] = useState("AI monitoring active");
  const [elapsed, setElapsed] = useState(0);

  const interviewId =
  localStorage.getItem("candidate_interview_id") ||
  sessionStorage.getItem("interviewguard_interview_id");

  const candidateToken = getCandidateToken();

  // ---------------------------------------------------------
  // WEBRTC HELPERS
  // ---------------------------------------------------------

  async function createWebRTCConnection() {
    if (peerConnectionRef.current) {
      return peerConnectionRef.current;
    }

    const pc = new RTCPeerConnection({
      iceServers: [
        {
          urls: "stun:stun.l.google.com:19302",
        },
      ],
    });

    peerConnectionRef.current = pc;

    const candidateStream = cameraStreamRef.current;

    if (candidateStream) {
      candidateStream.getTracks().forEach((track) => {
        pc.addTrack(track, candidateStream);
      });
    }

    pc.ontrack = (event) => {
      const [remoteStream] = event.streams;

      if (!remoteStream) {
        return;
      }

      if (adminVideoRef.current) {
        adminVideoRef.current.srcObject = remoteStream;
        adminVideoRef.current
          .play()
          .catch(() => {});
      }

      setAdminConnected(true);
      setWebrtcStatus("Admin connected");
    };

    pc.onicecandidate = (event) => {
      if (!event.candidate) {
        return;
      }

      const socket = webrtcSocketRef.current;

      if (!socket || socket.readyState !== WebSocket.OPEN) {
        return;
      }

      socket.send(
        JSON.stringify({
          type: "ice-candidate",
          candidate: event.candidate,
        })
      );
    };

    pc.onconnectionstatechange = () => {
      const state = pc.connectionState;

      if (state === "connected") {
        setAdminConnected(true);
        setWebrtcStatus("Live with admin");
      } else if (state === "connecting") {
        setWebrtcStatus("Connecting to admin...");
      } else if (state === "disconnected") {
        setAdminConnected(false);
        setWebrtcStatus("Admin connection interrupted");
      } else if (state === "failed") {
        setAdminConnected(false);
        setWebrtcStatus("Video connection failed");
      } else if (state === "closed") {
        setAdminConnected(false);
        setWebrtcStatus("Video connection closed");
      }
    };

    return pc;
  }

  async function createCandidateOffer() {
    const pc = await createWebRTCConnection();

    const offer = await pc.createOffer();

    await pc.setLocalDescription(offer);

    const socket = webrtcSocketRef.current;

    if (!socket || socket.readyState !== WebSocket.OPEN) {
      return;
    }

    socket.send(
      JSON.stringify({
        type: "offer",
        sdp: offer,
      })
    );

    setWebrtcStatus("Calling admin...");
  }

  async function handleWebRTCMessage(message) {
    const type = message.type;

    // -------------------------------------------------------
    // SERVER READY
    // -------------------------------------------------------

    if (type === "signaling-ready") {
      setWebrtcStatus("Waiting for admin...");
      return;
    }

    // -------------------------------------------------------
    // ADMIN IS CONNECTED
    // -------------------------------------------------------

    if (type === "peer-ready") {
      await createCandidateOffer();
      return;
    }

    // -------------------------------------------------------
    // ADMIN ANSWER
    // -------------------------------------------------------

    if (type === "answer") {
  const pc = await createWebRTCConnection();

  await pc.setRemoteDescription(
    new RTCSessionDescription(message.sdp)
  );

  remoteDescriptionSetRef.current = true;

  const pending =
    pendingIceCandidatesRef.current;

  pendingIceCandidatesRef.current = [];

  for (const candidate of pending) {
    try {
      await pc.addIceCandidate(candidate);
    } catch (err) {
      console.error(
        "Failed to add queued ICE candidate:",
        err
      );
    }
  }

  setWebrtcStatus("Connecting video...");
  return;
}

    // -------------------------------------------------------
    // ADMIN ICE CANDIDATE
    // -------------------------------------------------------

    if (type === "ice-candidate") {
  const pc = await createWebRTCConnection();

  if (!message.candidate) {
    return;
  }

  const candidate =
    new RTCIceCandidate(message.candidate);

  if (!remoteDescriptionSetRef.current) {
    pendingIceCandidatesRef.current.push(candidate);
    return;
  }

  try {
    await pc.addIceCandidate(candidate);
  } catch (err) {
    console.error(
      "Failed to add ICE candidate:",
      err
    );
  }

  return;
}

    // -------------------------------------------------------
    // ADMIN LEFT
    // -------------------------------------------------------

    if (type === "peer-left") {
      setAdminConnected(false);
      setWebrtcStatus("Admin disconnected");

      if (adminVideoRef.current) {
        adminVideoRef.current.srcObject = null;
      }

      return;
    }
  }

  function connectWebRTC() {
    if (!interviewId || !candidateToken) {
      setWebrtcStatus("Missing interview authentication");
      return;
    }

    const socket = new WebSocket(
      wsUrl(
        `/ws/webrtc/${encodeURIComponent(interviewId)}?role=candidate`,
        candidateToken
      )
    );

    webrtcSocketRef.current = socket;

    socket.onopen = () => {
      setWebrtcStatus("Waiting for admin...");
    };

    socket.onmessage = async (event) => {
      try {
        const message = JSON.parse(event.data);

        await handleWebRTCMessage(message);
      } catch (err) {
        console.error("WebRTC signaling error:", err);
      }
    };

    socket.onerror = () => {
      setWebrtcStatus("Video signaling error");
    };

    socket.onclose = () => {
      setAdminConnected(false);

      if (!endingRef.current) {
        setWebrtcStatus("Admin video connection closed");
      }
    };
  }

  function closeWebRTC() {
    const socket = webrtcSocketRef.current;

    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(
        JSON.stringify({
          type: "leave",
        })
      );

      socket.close();
    }

    webrtcSocketRef.current = null;

    const pc = peerConnectionRef.current;

    if (pc) {
      pc.close();
    }

    peerConnectionRef.current = null;
    pendingIceCandidatesRef.current = [];
    remoteDescriptionSetRef.current = false;

    if (adminVideoRef.current) {
      adminVideoRef.current.srcObject = null;
    }
  }

  // ---------------------------------------------------------
  // AI FRAME ANALYSIS
  // ---------------------------------------------------------

  async function sendFrame() {
    if (!candidateVideoRef.current || !interviewId) {
      return;
    }

    const video = candidateVideoRef.current;

    if (
      !video.videoWidth ||
      !video.videoHeight
    ) {
      return;
    }

    const canvas = document.createElement("canvas");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const context = canvas.getContext("2d");

    context.drawImage(
      video,
      0,
      0,
      canvas.width,
      canvas.height
    );

    const blob = await new Promise((resolve) => {
      canvas.toBlob(
        resolve,
        "image/jpeg",
        0.7
      );
    });

    if (!blob) {
      return;
    }

    const formData = new FormData();

    formData.append(
      "file",
      blob,
      "frame.jpg"
    );

    try {
      await apiFetch(
        `/interview/${interviewId}/frame`,
        {
          method: "POST",
          body: formData,
        },
        candidateToken
      );
    } catch (err) {
      console.error("Frame analysis error:", err);
    }
  }

  // ---------------------------------------------------------
  // AI AUDIO ANALYSIS
  // ---------------------------------------------------------

  async function sendAudio() {
    if (!interviewId) {
      return;
    }

    const samples = audioSamplesRef.current;

    if (!samples.length) {
      return;
    }

    const copiedSamples = samples.slice();

    audioSamplesRef.current = [];

    const wavBlob = encodeWav(
      copiedSamples,
      16000
    );

    const formData = new FormData();

    formData.append(
      "file",
      wavBlob,
      "audio.wav"
    );

    try {
      await apiFetch(
        `/interview/${interviewId}/audio`,
        {
          method: "POST",
          body: formData,
        },
        candidateToken
      );
    } catch (err) {
      console.error("Audio analysis error:", err);
    }
  }

  // ---------------------------------------------------------
  // FEATURE WINDOW
  // ---------------------------------------------------------

  async function createFeatureWindow() {
    if (!interviewId) {
      return;
    }

    try {
      await apiFetch(
        `/interview/${interviewId}/window`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({}),
        },
        candidateToken
      );
    } catch (err) {
      console.error(
        "Feature window error:",
        err
      );
    }
  }

  // ---------------------------------------------------------
  // AUDIO PIPELINE
  // ---------------------------------------------------------

  async function startAudioPipeline(stream) {
    const AudioContext =
      window.AudioContext ||
      window.webkitAudioContext;

    if (!AudioContext) {
      return;
    }

    const audioContext = new AudioContext({
      sampleRate: 16000,
    });

    audioContextRef.current = audioContext;

    const source =
      audioContext.createMediaStreamSource(stream);

    audioSourceRef.current = source;

    const processor =
      audioContext.createScriptProcessor(
        4096,
        1,
        1
      );

    audioProcessorRef.current = processor;

    processor.onaudioprocess = (event) => {
      const input =
        event.inputBuffer.getChannelData(0);

      for (let i = 0; i < input.length; i++) {
        audioSamplesRef.current.push(input[i]);
      }
    };

    source.connect(processor);
    processor.connect(audioContext.destination);
  }

  // ---------------------------------------------------------
  // CLEANUP
  // ---------------------------------------------------------

  function cleanupStreams() {
    if (frameTimerRef.current) {
      clearInterval(frameTimerRef.current);
      frameTimerRef.current = null;
    }

    if (audioTimerRef.current) {
      clearInterval(audioTimerRef.current);
      audioTimerRef.current = null;
    }

    if (windowTimerRef.current) {
      clearInterval(windowTimerRef.current);
      windowTimerRef.current = null;
    }

    if (audioProcessorRef.current) {
      try {
        audioProcessorRef.current.disconnect();
      } catch {}
    }

    if (audioSourceRef.current) {
      try {
        audioSourceRef.current.disconnect();
      } catch {}
    }

    if (audioContextRef.current) {
      try {
        audioContextRef.current.close();
      } catch {}
    }

    audioProcessorRef.current = null;
    audioSourceRef.current = null;
    audioContextRef.current = null;

    if (cameraStreamRef.current) {
      cameraStreamRef.current
        .getTracks()
        .forEach((track) => track.stop());

      cameraStreamRef.current = null;
    }

    if (screenStreamRef.current) {
      screenStreamRef.current
        .getTracks()
        .forEach((track) => track.stop());

      screenStreamRef.current = null;
    }

    if (candidateVideoRef.current) {
      candidateVideoRef.current.srcObject = null;
    }

    closeWebRTC();
  }

  // ---------------------------------------------------------
  // FINISH INTERVIEW
  // ---------------------------------------------------------

  async function finishInterview() {
    if (endingRef.current) {
      return;
    }

    endingRef.current = true;
    setEnding(true);

    try {
      await sendAudio();

      if (interviewId) {
        await apiFetch(
          `/interview/${interviewId}/end`,
          {
            method: "POST",
          },
          candidateToken
        );
      }

      closeWebRTC();
      cleanupStreams();

      if (document.fullscreenElement) {
        try {
          await document.exitFullscreen();
        } catch {}
      }

      setSubmitted(true);
      setAiStatus("Interview submitted");
    } catch (err) {
      console.error(err);

      setError(
        err.message ||
          "Unable to submit the interview."
      );

      endingRef.current = false;
      setEnding(false);
    }
  }

  function endInterview() {
    if (endingRef.current) {
      return;
    }

    finishInterview();
  }

  // ---------------------------------------------------------
  // START INTERVIEW
  // ---------------------------------------------------------

  async function startInterview() {
    if (startedRef.current) {
      return;
    }

    startedRef.current = true;

    try {
      const cameraStream =
        window.interviewCameraStream;

      const screenStream =
        window.interviewScreenStream;

      if (!cameraStream) {
        throw new Error(
          "Candidate camera stream not found."
        );
      }

      cameraStreamRef.current =
        cameraStream;

      screenStreamRef.current =
        screenStream || null;

      if (candidateVideoRef.current) {
        candidateVideoRef.current.srcObject =
          cameraStream;

        await candidateVideoRef.current.play();
      }

      // -----------------------------------------------------
      // Start candidate audio processing for AI
      // -----------------------------------------------------

      await startAudioPipeline(
        cameraStream
      );

      // -----------------------------------------------------
      // Start WebRTC
      // -----------------------------------------------------

      connectWebRTC();

      // -----------------------------------------------------
      // Existing recording behavior
      // -----------------------------------------------------

      try {
        const recorder =
          new MediaRecorder(
            cameraStream,
            {
              mimeType:
                "video/webm;codecs=vp8,opus",
            }
          );

        mediaRecorderRef.current =
          recorder;

        recorder.ondataavailable = () => {};

        recorder.onstop = () => {};

        recorder.start();

        setRecording(true);
      } catch (err) {
        console.warn(
          "MediaRecorder unavailable:",
          err
        );
      }

      // -----------------------------------------------------
      // AI frame analysis every second
      // -----------------------------------------------------

      frameTimerRef.current =
        setInterval(() => {
          sendFrame();
        }, 1000);

      // -----------------------------------------------------
      // AI audio analysis every 3 seconds
      // -----------------------------------------------------

      audioTimerRef.current =
        setInterval(() => {
          sendAudio();
        }, 3000);

      // -----------------------------------------------------
      // Feature window every 5 seconds
      // -----------------------------------------------------

      windowTimerRef.current =
        setInterval(() => {
          createFeatureWindow();
        }, 5000);

      // -----------------------------------------------------
      // Screen share ended
      // -----------------------------------------------------

      if (screenStream) {
        const screenTrack =
          screenStream.getVideoTracks()[0];

        if (screenTrack) {
          screenTrack.onended = () => {
            setError(
              "Screen sharing ended. Please contact the administrator."
            );
          };
        }
      }
    } catch (err) {
      console.error(err);

      setError(
        err.message ||
          "Unable to start the interview."
      );
    }
  }

  // ---------------------------------------------------------
  // MOUNT
  // ---------------------------------------------------------

  useEffect(() => {
    startInterview();

    const timer = setInterval(() => {
      setElapsed((value) => value + 1);
    }, 1000);

    return () => {
      clearInterval(timer);

      if (!endingRef.current) {
        cleanupStreams();
      }
    };
  }, []);

  // ---------------------------------------------------------
  // FORMAT TIME
  // ---------------------------------------------------------

  function formatElapsed(seconds) {
    const minutes =
      Math.floor(seconds / 60);

    const remaining =
      seconds % 60;

    return `${String(minutes).padStart(
      2,
      "0"
    )}:${String(remaining).padStart(
      2,
      "0"
    )}`;
  }

  // ---------------------------------------------------------
  // SUBMITTED SCREEN
  // ---------------------------------------------------------

  if (submitted) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "#f5f7fb",
          padding: "30px",
        }}
      >
        <div
          style={{
            background: "white",
            padding: "40px",
            borderRadius: "16px",
            maxWidth: "600px",
            width: "100%",
            textAlign: "center",
            boxShadow:
              "0 10px 40px rgba(0,0,0,0.08)",
          }}
        >
          <h1>
            Interview Submitted
          </h1>

          <p>
            Your interview has been submitted
            successfully.
          </p>

          <p>
            The interview session has ended.
          </p>
        </div>
      </div>
    );
  }

  // ---------------------------------------------------------
  // MAIN UI
  // ---------------------------------------------------------

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#f5f7fb",
        padding: "20px",
      }}
    >
      <div
        style={{
          maxWidth: "1400px",
          margin: "0 auto",
        }}
      >
        {/* HEADER */}

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "20px",
            background: "white",
            padding: "16px 20px",
            borderRadius: "14px",
          }}
        >
          <div>
            <h2
              style={{
                margin: 0,
              }}
            >
              Live Interview
            </h2>

            <div
              style={{
                marginTop: "5px",
                color: "#666",
              }}
            >
              Interview ID: {interviewId}
            </div>
          </div>

          <div
            style={{
              display: "flex",
              gap: "15px",
              alignItems: "center",
            }}
          >
            <span>
              {formatElapsed(elapsed)}
            </span>

            <span
              style={{
                padding: "8px 12px",
                borderRadius: "20px",
                background: adminConnected
                  ? "#dcfce7"
                  : "#fef3c7",
                color: adminConnected
                  ? "#166534"
                  : "#92400e",
                fontSize: "14px",
              }}
            >
              {webrtcStatus}
            </span>
          </div>
        </div>

        {/* VIDEO AREA */}

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(2, minmax(0, 1fr))",
            gap: "20px",
          }}
        >
          {/* ADMIN VIDEO */}

          <div
            style={{
              background: "black",
              borderRadius: "16px",
              overflow: "hidden",
              minHeight: "420px",
              position: "relative",
            }}
          >
            <video
              ref={adminVideoRef}
              autoPlay
              playsInline
              style={{
                width: "100%",
                height: "100%",
                minHeight: "420px",
                objectFit: "cover",
                background: "#111",
              }}
            />

            <div
              style={{
                position: "absolute",
                left: "15px",
                top: "15px",
                background:
                  "rgba(0,0,0,0.65)",
                color: "white",
                padding: "8px 12px",
                borderRadius: "8px",
                fontSize: "14px",
              }}
            >
              Admin
            </div>
          </div>

          {/* CANDIDATE VIDEO */}

          <div
            style={{
              background: "black",
              borderRadius: "16px",
              overflow: "hidden",
              minHeight: "420px",
              position: "relative",
            }}
          >
            <video
              ref={candidateVideoRef}
              autoPlay
              muted
              playsInline
              style={{
                width: "100%",
                height: "100%",
                minHeight: "420px",
                objectFit: "cover",
                background: "#111",
              }}
            />

            <div
              style={{
                position: "absolute",
                left: "15px",
                top: "15px",
                background:
                  "rgba(0,0,0,0.65)",
                color: "white",
                padding: "8px 12px",
                borderRadius: "8px",
                fontSize: "14px",
              }}
            >
              You
            </div>
          </div>
        </div>

        {/* STATUS */}

        <div
          style={{
            marginTop: "20px",
            background: "white",
            padding: "18px",
            borderRadius: "14px",
          }}
        >
          <strong>
            {aiStatus}
          </strong>

          <p
            style={{
              marginBottom: 0,
              color: "#666",
            }}
          >
            Your interview is being processed
            in real time. Analysis results are
            not displayed to the candidate.
          </p>
        </div>

        {/* ERROR */}

        {error && (
          <div
            style={{
              marginTop: "15px",
              background: "#fee2e2",
              color: "#991b1b",
              padding: "15px",
              borderRadius: "10px",
            }}
          >
            {error}
          </div>
        )}

        {/* END BUTTON */}

        <div
          style={{
            marginTop: "20px",
            textAlign: "center",
          }}
        >
          <button
            onClick={endInterview}
            disabled={ending}
            style={{
              padding:
                "12px 24px",
              border: "none",
              borderRadius: "10px",
              background: "#dc2626",
              color: "white",
              fontSize: "16px",
              cursor: ending
                ? "not-allowed"
                : "pointer",
              opacity: ending ? 0.6 : 1,
            }}
          >
            {ending
              ? "Submitting..."
              : "End Interview"}
          </button>
        </div>
      </div>
    </div>
  );
}