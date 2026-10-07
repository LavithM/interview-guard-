import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./admin/AdminDashboard.css";
import { apiFetch, getAdminToken, wsUrl } from "../api";


/* ============================================================
   LIVE WEBRTC INTERVIEW CARD
   ============================================================ */

function LiveInterviewCard({
  item,
  state,
  token,
}) {
  const candidateVideoRef = useRef(null);
  const adminVideoRef = useRef(null);

  const adminStreamRef = useRef(null);
  const peerConnectionRef = useRef(null);
  const socketRef = useRef(null);

  const [videoStatus, setVideoStatus] = useState(
    "Starting camera..."
  );

  const [adminCameraReady, setAdminCameraReady] =
    useState(false);

  const [candidateConnected, setCandidateConnected] =
    useState(false);


  /* ----------------------------------------------------------
     CREATE WEBRTC CONNECTION
     ---------------------------------------------------------- */

  const createPeerConnection = () => {
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


    /* --------------------------------------------------------
       ADMIN CAMERA + MICROPHONE
       -------------------------------------------------------- */

    const adminStream =
      adminStreamRef.current;

    if (adminStream) {
      adminStream
        .getTracks()
        .forEach((track) => {
          pc.addTrack(
            track,
            adminStream
          );
        });
    }


    /* --------------------------------------------------------
       RECEIVE CANDIDATE VIDEO/AUDIO
       -------------------------------------------------------- */

    pc.ontrack = (event) => {
      const remoteStream =
        event.streams[0];

      if (!remoteStream) {
        return;
      }

      if (candidateVideoRef.current) {
        candidateVideoRef.current.srcObject =
          remoteStream;

        candidateVideoRef.current
          .play()
          .catch(() => {});
      }

      setCandidateConnected(true);
      setVideoStatus("Candidate connected");
    };


    /* --------------------------------------------------------
       SEND ICE CANDIDATES
       -------------------------------------------------------- */

    pc.onicecandidate = (event) => {
      if (!event.candidate) {
        return;
      }

      const socket =
        socketRef.current;

      if (
        !socket ||
        socket.readyState !== WebSocket.OPEN
      ) {
        return;
      }

      socket.send(
        JSON.stringify({
          type: "ice-candidate",
          candidate: event.candidate,
        })
      );
    };


    /* --------------------------------------------------------
       CONNECTION STATE
       -------------------------------------------------------- */

    pc.onconnectionstatechange = () => {
      const connectionState =
        pc.connectionState;

      if (
        connectionState === "connected"
      ) {
        setCandidateConnected(true);
        setVideoStatus(
          "Live video connected"
        );
      }

      if (
        connectionState === "connecting"
      ) {
        setVideoStatus(
          "Connecting video..."
        );
      }

      if (
        connectionState === "disconnected"
      ) {
        setCandidateConnected(false);
        setVideoStatus(
          "Candidate disconnected"
        );
      }

      if (
        connectionState === "failed"
      ) {
        setCandidateConnected(false);
        setVideoStatus(
          "Video connection failed"
        );
      }

      if (
        connectionState === "closed"
      ) {
        setCandidateConnected(false);
        setVideoStatus(
          "Video connection closed"
        );
      }
    };

    return pc;
  };


  /* ----------------------------------------------------------
     WEBRTC SIGNALING
     ---------------------------------------------------------- */

  useEffect(() => {
    let socket = null;
    let cancelled = false;


    const start = async () => {
      try {
        setVideoStatus(
          "Requesting admin camera..."
        );


        /* ----------------------------------------------------
           GET ADMIN CAMERA + MICROPHONE
           ---------------------------------------------------- */

        const stream =
          await navigator.mediaDevices.getUserMedia(
            {
              video: true,
              audio: true,
            }
          );

        if (cancelled) {
          stream
            .getTracks()
            .forEach((track) =>
              track.stop()
            );

          return;
        }

        adminStreamRef.current =
          stream;

        setAdminCameraReady(true);


        /* ----------------------------------------------------
           SHOW ADMIN SELF PREVIEW
           ---------------------------------------------------- */

        if (adminVideoRef.current) {
          adminVideoRef.current.srcObject =
            stream;

          await adminVideoRef.current
            .play()
            .catch(() => {});
        }


        /* ----------------------------------------------------
           CONNECT SIGNALING WEBSOCKET
           ---------------------------------------------------- */

        socket = new WebSocket(
          wsUrl(
            `/ws/webrtc/${encodeURIComponent(
              item.interview_id
            )}?role=admin`,
            token
          )
        );

        socketRef.current =
          socket;


        socket.onopen = () => {
          setVideoStatus(
            "Waiting for candidate..."
          );
        };


        socket.onmessage = async (
          event
        ) => {
          try {
            const message =
              JSON.parse(
                event.data
              );

            const type =
              message.type;


            /* ----------------------------------------------
               SIGNALING READY
               ---------------------------------------------- */

            if (
              type ===
              "signaling-ready"
            ) {
              setVideoStatus(
                "Waiting for candidate..."
              );

              return;
            }


            /* ----------------------------------------------
               CANDIDATE READY
               ---------------------------------------------- */

            if (
              type === "peer-ready"
            ) {
              setVideoStatus(
                "Candidate found..."
              );

              return;
            }


            /* ----------------------------------------------
               RECEIVE CANDIDATE OFFER
               ---------------------------------------------- */

            if (
              type === "offer"
            ) {
              const pc =
                createPeerConnection();

              await pc.setRemoteDescription(
                new RTCSessionDescription(
                  message.sdp
                )
              );


              const answer =
                await pc.createAnswer();

              await pc.setLocalDescription(
                answer
              );


              if (
                socket.readyState ===
                WebSocket.OPEN
              ) {
                socket.send(
                  JSON.stringify({
                    type: "answer",
                    sdp: answer,
                  })
                );
              }

              setVideoStatus(
                "Connecting to candidate..."
              );

              return;
            }


            /* ----------------------------------------------
               RECEIVE ICE CANDIDATE
               ---------------------------------------------- */

            if (
              type ===
              "ice-candidate"
            ) {
              const pc =
                createPeerConnection();

              if (
                message.candidate
              ) {
                try {
                  await pc.addIceCandidate(
                    new RTCIceCandidate(
                      message.candidate
                    )
                  );
                } catch (err) {
                  console.error(
                    "ICE candidate error:",
                    err
                  );
                }
              }

              return;
            }


            /* ----------------------------------------------
               CANDIDATE LEFT
               ---------------------------------------------- */

            if (
              type === "peer-left"
            ) {
              setCandidateConnected(
                false
              );

              setVideoStatus(
                "Candidate disconnected"
              );

              if (
                candidateVideoRef.current
              ) {
                candidateVideoRef.current.srcObject =
                  null;
              }

              return;
            }
          } catch (err) {
            console.error(
              "WebRTC message error:",
              err
            );
          }
        };


        socket.onerror = (err) => {
          console.error(
            "WebRTC signaling error:",
            err
          );

          setVideoStatus(
            "WebRTC signaling error"
          );
        };


        socket.onclose = () => {
          if (!cancelled) {
            setCandidateConnected(
              false
            );

            setVideoStatus(
              "Video signaling closed"
            );
          }
        };
      } catch (err) {
        console.error(
          "Unable to start admin camera:",
          err
        );

        setVideoStatus(
          "Camera/microphone permission required"
        );
      }
    };


    start();


    /* --------------------------------------------------------
       CLEANUP
       -------------------------------------------------------- */

    return () => {
      cancelled = true;


      if (socket) {
        try {
          if (
            socket.readyState ===
            WebSocket.OPEN
          ) {
            socket.send(
              JSON.stringify({
                type: "leave",
              })
            );
          }

          socket.close();
        } catch {}
      }


      socketRef.current = null;


      if (
        peerConnectionRef.current
      ) {
        try {
          peerConnectionRef.current.close();
        } catch {}

        peerConnectionRef.current =
          null;
      }


      if (
        adminStreamRef.current
      ) {
        adminStreamRef.current
          .getTracks()
          .forEach((track) =>
            track.stop()
          );

        adminStreamRef.current =
          null;
      }


      if (
        adminVideoRef.current
      ) {
        adminVideoRef.current.srcObject =
          null;
      }


      if (
        candidateVideoRef.current
      ) {
        candidateVideoRef.current.srcObject =
          null;
      }
    };
  }, [item.interview_id, token]);


  /* ==========================================================
     AI DATA
     ========================================================== */

  const analysis =
    state?.latest_analysis || {};

  const fusion =
    analysis.fusion || {};

  const objects =
    fusion.objects || {};

  const model =
    analysis.model_prediction || {};


  /* ==========================================================
     RENDER
     ========================================================== */

  return (
    <div
      style={{
        border:
          "1px solid #e5e7eb",
        borderRadius: 16,
        padding: 20,
        marginBottom: 20,
        background: "#ffffff",
      }}
    >
      {/* HEADER */}

      <div
        style={{
          display: "flex",
          justifyContent:
            "space-between",
          alignItems: "center",
          marginBottom: 16,
        }}
      >
        <div>
          <h3
            style={{
              margin: 0,
            }}
          >
            {item.candidate_name}
          </h3>

          <p
            style={{
              margin:
                "5px 0 0 0",
              color: "#6b7280",
            }}
          >
            {item.role} ·{" "}
            {item.candidate_email}
          </p>
        </div>

        <div
          style={{
            display: "flex",
            gap: 8,
            alignItems:
              "center",
          }}
        >
          <span
            style={{
              padding:
                "7px 11px",
              borderRadius: 20,
              background:
                adminCameraReady
                  ? "#dcfce7"
                  : "#fef3c7",
              color:
                adminCameraReady
                  ? "#166534"
                  : "#92400e",
              fontSize: 13,
            }}
          >
            {adminCameraReady
              ? "Admin camera ready"
              : "Camera starting"}
          </span>

          <span
            style={{
              padding:
                "7px 11px",
              borderRadius: 20,
              background:
                candidateConnected
                  ? "#dcfce7"
                  : "#f3f4f6",
              color:
                candidateConnected
                  ? "#166534"
                  : "#4b5563",
              fontSize: 13,
            }}
          >
            {videoStatus}
          </span>
        </div>
      </div>


      {/* ======================================================
          TWO-WAY VIDEO
          ====================================================== */}

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(2, minmax(0, 1fr))",
          gap: 16,
          marginBottom: 20,
        }}
      >
        {/* CANDIDATE */}

        <div
          style={{
            position: "relative",
            background: "#111827",
            borderRadius: 14,
            overflow: "hidden",
            minHeight: 360,
          }}
        >
          <video
            ref={candidateVideoRef}
            autoPlay
            playsInline
            style={{
              width: "100%",
              height: 360,
              objectFit: "cover",
              display: "block",
              background: "#111827",
            }}
          />

          <div
            style={{
              position: "absolute",
              left: 12,
              top: 12,
              background:
                "rgba(0,0,0,0.65)",
              color: "white",
              padding:
                "7px 11px",
              borderRadius: 8,
              fontSize: 13,
            }}
          >
            Candidate
          </div>

          {!candidateConnected && (
            <div
              style={{
                position:
                  "absolute",
                inset: 0,
                display: "flex",
                alignItems:
                  "center",
                justifyContent:
                  "center",
                color: "white",
                background:
                  "rgba(17,24,39,0.8)",
              }}
            >
              Waiting for candidate video...
            </div>
          )}
        </div>


        {/* ADMIN */}

        <div
          style={{
            position: "relative",
            background: "#111827",
            borderRadius: 14,
            overflow: "hidden",
            minHeight: 360,
          }}
        >
          <video
            ref={adminVideoRef}
            autoPlay
            muted
            playsInline
            style={{
              width: "100%",
              height: 360,
              objectFit: "cover",
              display: "block",
              background: "#111827",
            }}
          />

          <div
            style={{
              position: "absolute",
              left: 12,
              top: 12,
              background:
                "rgba(0,0,0,0.65)",
              color: "white",
              padding:
                "7px 11px",
              borderRadius: 8,
              fontSize: 13,
            }}
          >
            Admin
          </div>
        </div>
      </div>


      {/* ======================================================
          AI LIVE MONITOR
          ====================================================== */}

      <div
        style={{
          borderTop:
            "1px solid #e5e7eb",
          paddingTop: 18,
        }}
      >
        <h4
          style={{
            marginTop: 0,
            marginBottom: 12,
          }}
        >
          Live AI Monitor
        </h4>


        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(4, 1fr)",
            gap: 12,
          }}
        >
          <div className="stat-card">
            <span>
              Face
            </span>

            <strong>
              {fusion.face_status ||
                "waiting"}
            </strong>
          </div>


          <div className="stat-card">
            <span>
              People
            </span>

            <strong>
              {objects
                .maximum_person_count ??
                "-"}
            </strong>
          </div>


          <div className="stat-card">
            <span>
              Phone
            </span>

            <strong>
              {objects.mobile_phone_detected
                ? "Detected"
                : "Not detected"}
            </strong>
          </div>


          <div className="stat-card">
            <span>
              Speech
            </span>

            <strong>
              {analysis.speech_detected
                ? "Detected"
                : "Quiet"}
            </strong>
          </div>
        </div>


        <p
          style={{
            marginBottom: 0,
            marginTop: 14,
          }}
        >
          AI stream:{" "}
          {state
            ? "Connected"
            : "Connecting..."}{" "}
          · Model prediction
          available:{" "}
          {model.prediction_available
            ? "Yes"
            : "No"}
        </p>


        <p
          style={{
            fontSize: 13,
            color: "#6b7280",
            marginBottom: 0,
          }}
        >
          These are live
          indicators/evidence
          signals, not a final
          cheating verdict.
        </p>
      </div>
    </div>
  );
}


/* ============================================================
   ADMIN DASHBOARD
   ============================================================ */

function AdminDashboard() {
  const navigate =
    useNavigate();

  const token =
    getAdminToken();


  const [
    candidateName,
    setCandidateName,
  ] = useState("");

  const [
    candidateEmail,
    setCandidateEmail,
  ] = useState("");

  const [
    role,
    setRole,
  ] = useState(
    "Software Developer"
  );


  const [
    interviews,
    setInterviews,
  ] = useState([]);

  const [
    createdLink,
    setCreatedLink,
  ] = useState("");

  const [
    live,
    setLive,
  ] = useState({});

  const [
    error,
    setError,
  ] = useState("");

  const [
    loading,
    setLoading,
  ] = useState(false);


  /* ==========================================================
     LOAD INTERVIEWS
     ========================================================== */

  const loadInterviews =
    async () => {
      if (!token) {
        navigate("/admin");
        return;
      }

      try {
        const data =
          await apiFetch(
            "/admin/interviews/recent?limit=100",
            {},
            token
          );

        setInterviews(
          data.interviews || []
        );

        setError("");
      } catch (err) {
        console.error(
          "Failed to load interviews:",
          err
        );

        setError(
          err.message ||
            "Failed to load interviews."
        );
      }
    };


  useEffect(() => {
    loadInterviews();

    const timer =
      window.setInterval(
        () => {
          loadInterviews();
        },
        5000
      );

    return () => {
      window.clearInterval(
        timer
      );
    };
  }, []);


  /* ==========================================================
     EXISTING AI WEBSOCKETS
     ========================================================== */

  useEffect(() => {
    const activeInterviews =
      interviews.filter(
        (item) =>
          item.status ===
          "active"
      );

    const sockets = [];

    activeInterviews.forEach(
      (item) => {
        try {
          const socket =
            new WebSocket(
              wsUrl(
                `/ws/admin/${item.interview_id}`,
                token
              )
            );

          sockets.push(socket);

          socket.onopen = () => {
            console.log(
              "AI live connection opened:",
              item.interview_id
            );
          };

          socket.onmessage = (
            event
          ) => {
            try {
              const data =
                JSON.parse(
                  event.data
                );

              setLive(
                (current) => ({
                  ...current,
                  [item.interview_id]:
                    data,
                })
              );
            } catch (err) {
              console.error(
                "Invalid live update:",
                err
              );
            }
          };

          socket.onerror = (
            err
          ) => {
            console.error(
              "AI WebSocket error:",
              item.interview_id,
              err
            );
          };

          socket.onclose = () => {
            console.log(
              "AI live connection closed:",
              item.interview_id
            );
          };
        } catch (err) {
          console.error(
            "Could not create AI WebSocket:",
            err
          );
        }
      }
    );

    return () => {
      sockets.forEach(
        (socket) => {
          try {
            socket.close();
          } catch {}
        }
      );
    };
  }, [interviews, token]);


  /* ==========================================================
     CREATE INTERVIEW
     ========================================================== */

  const createInterview =
    async (e) => {
      e.preventDefault();

      setError("");
      setCreatedLink("");

      if (
        !candidateName.trim() ||
        !candidateEmail.trim() ||
        !role.trim()
      ) {
        setError(
          "Candidate name, email and role are required."
        );

        return;
      }

      try {
        setLoading(true);

        const data =
          await apiFetch(
            "/admin/interviews",
            {
              method: "POST",

              headers: {
                "Content-Type":
                  "application/json",
              },

              body: JSON.stringify({
                candidate_name:
                  candidateName.trim(),

                candidate_email:
                  candidateEmail.trim(),

                role:
                  role.trim(),
              }),
            },
            token
          );

        const link =
          data?.invitation
            ?.candidate_link ||
          data?.candidate_link ||
          "";

        setCreatedLink(link);

        setCandidateName("");
        setCandidateEmail("");
        setRole(
          "Software Developer"
        );

        await loadInterviews();
      } catch (err) {
        console.error(
          "Failed to create interview:",
          err
        );

        setError(
          err.message ||
            "Failed to create interview."
        );
      } finally {
        setLoading(false);
      }
    };


  /* ==========================================================
     COPY LINK
     ========================================================== */

  const copyLink =
    async (link) => {
      if (!link) {
        return;
      }

      try {
  if (navigator.clipboard && window.isSecureContext) {
    await navigator.clipboard.writeText(link);

    alert("Interview link copied.");
    return;
  }

  // Safari / non-secure fallback
  const textArea = document.createElement("textarea");

  textArea.value = link;
  textArea.style.position = "fixed";
  textArea.style.left = "-9999px";
  textArea.style.top = "0";

  document.body.appendChild(textArea);

  textArea.focus();
  textArea.select();

  const copied = document.execCommand("copy");

  document.body.removeChild(textArea);

  if (copied) {
    alert("Interview link copied.");
  } else {
    throw new Error("Clipboard copy failed");
  }
  } catch (err) {
    console.error("Could not copy link:", err);

    alert(
      "Could not copy automatically. Please select and copy the link manually."
    );
  }
  };


  /* ==========================================================
     LOGOUT
     ========================================================== */


  /* ==========================================================
     LOGOUT
     ========================================================== */

  const logout = () => {
    localStorage.removeItem(
      "interviewguard_admin_token"
    );

    localStorage.removeItem(
      "interviewguard_admin_user"
    );

    navigate("/admin");
  };


  /* ==========================================================
     STATUS
     ========================================================== */

  const getStatusLabel =
    (status) => {
      if (
        status ===
        "pending"
      ) {
        return "Invited";
      }

      if (
        status ===
        "active"
      ) {
        return "Active";
      }

      if (
        status ===
        "completed"
      ) {
        return "Completed";
      }

      return (
        status || "Unknown"
      );
    };


  const getStatusClass =
    (status) => {
      if (
        status ===
        "pending"
      ) {
        return "status status-invited";
      }

      if (
        status ===
        "active"
      ) {
        return "status status-active";
      }

      if (
        status ===
        "completed"
      ) {
        return "status status-completed";
      }

      return "status";
    };


  /* ==========================================================
     STATS
     ========================================================== */

  const stats =
    useMemo(
      () => ({
        total:
          interviews.length,

        active:
          interviews.filter(
            (item) =>
              item.status ===
              "active"
          ).length,

        completed:
          interviews.filter(
            (item) =>
              item.status ===
              "completed"
          ).length,

        invited:
          interviews.filter(
            (item) =>
              item.status ===
              "pending"
          ).length,
      }),
      [interviews]
    );


  /* ==========================================================
     RENDER
     ========================================================== */

  return (
    <div className="admin-dashboard">

      {/* SIDEBAR */}

      <aside className="admin-sidebar">

        <div className="dashboard-logo">
          InterviewGuard
        </div>

        <p className="sidebar-title">
          ADMIN PANEL
        </p>

        <div className="sidebar-menu">

          <button className="active">
            Dashboard
          </button>

          <button
            onClick={() =>
              document
                .querySelector(
                  ".interviews-section"
                )
                ?.scrollIntoView({
                  behavior:
                    "smooth",
                })
            }
          >
            Interviews
          </button>

          <button
            onClick={() =>
              document
                .querySelector(
                  ".live-section"
                )
                ?.scrollIntoView({
                  behavior:
                    "smooth",
                })
            }
          >
            Live Monitor
          </button>

          <button
            onClick={() =>
              document
                .querySelector(
                  ".reports-section"
                )
                ?.scrollIntoView({
                  behavior:
                    "smooth",
                })
            }
          >
            Reports
          </button>

        </div>

        <button
          className="logout-button"
          onClick={logout}
        >
          Logout
        </button>

      </aside>


      {/* MAIN */}

      <main className="dashboard-main">

        {/* HEADER */}

        <header className="dashboard-header">

          <div>

            <h1>
              Admin Dashboard
            </h1>

            <p>
              Create interviews and
              monitor candidates in
              real time.
            </p>

          </div>

          <div className="admin-profile">
            Admin
          </div>

        </header>


        {/* STATS */}

        <section className="stats">

          <div className="stat-card">
            <span>
              Total Interviews
            </span>

            <strong>
              {stats.total}
            </strong>
          </div>

          <div className="stat-card">
            <span>
              Active Now
            </span>

            <strong>
              {stats.active}
            </strong>
          </div>

          <div className="stat-card">
            <span>
              Invited
            </span>

            <strong>
              {stats.invited}
            </strong>
          </div>

          <div className="stat-card">
            <span>
              Completed
            </span>

            <strong>
              {stats.completed}
            </strong>
          </div>

        </section>


        {/* CREATE INTERVIEW */}

        <section className="create-exam">

          <h2>
            Create Interview
          </h2>

          <form
            onSubmit={
              createInterview
            }
          >

            <div
              className="form-row"
              style={{
                gridTemplateColumns:
                  "1fr 1fr",
              }}
            >

              <div>

                <label>
                  Candidate Name
                </label>

                <input
                  value={
                    candidateName
                  }
                  onChange={(e) =>
                    setCandidateName(
                      e.target.value
                    )
                  }
                  placeholder="Candidate name"
                />

              </div>


              <div>

                <label>
                  Candidate Email
                </label>

                <input
                  type="email"
                  value={
                    candidateEmail
                  }
                  onChange={(e) =>
                    setCandidateEmail(
                      e.target.value
                    )
                  }
                  placeholder="candidate@example.com"
                />

              </div>

            </div>


            <div
              style={{
                marginTop: 18,
              }}
            >

              <label>
                Interview Role
              </label>

              <input
                value={role}
                onChange={(e) =>
                  setRole(
                    e.target.value
                  )
                }
                placeholder="Software Developer"
              />

            </div>


            {error && (
              <p
                style={{
                  color:
                    "#dc2626",
                }}
              >
                {error}
              </p>
            )}


            <button
              type="submit"
              disabled={loading}
            >
              {loading
                ? "CREATING..."
                : "CREATE INTERVIEW LINK"}
            </button>

          </form>


          {createdLink && (
            <div className="generated-code">

              <p>
                Interview created
                successfully.
              </p>

              <span>
                Candidate Interview Link
              </span>

              <strong
                style={{
                  fontSize: 15,
                  letterSpacing: 0,
                  overflowWrap:
                    "anywhere",
                }}
              >
                {createdLink}
              </strong>

              <button
                type="button"
                onClick={() =>
                  copyLink(
                    createdLink
                  )
                }
              >
                COPY LINK
              </button>

            </div>
          )}

        </section>


        {/* INTERVIEWS */}

        <section className="interviews-section exam-section">

          <div className="section-header">

            <h2>
              Interviews
            </h2>

            <span>
              {interviews.length}{" "}
              interview(s)
            </span>

          </div>


          {interviews.length ===
          0 ? (

            <div className="empty-state">

              <h3>
                No interviews created yet
              </h3>

              <p>
                Create an interview above
                to generate a candidate
                link.
              </p>

            </div>

          ) : (

            <div className="exam-table">

              <div className="table-header interview-table-grid">

                <span>
                  Candidate
                </span>

                <span>
                  Email
                </span>

                <span>
                  Role
                </span>

                <span>
                  Interview ID
                </span>

                <span>
                  Status
                </span>

                <span>
                  Interview Link
                </span>

                <span>
                  Report
                </span>

              </div>


              {interviews.map(
                (item) => (

                  <div
                    className="table-row interview-table-grid"
                    key={
                      item.interview_id
                    }
                  >

                    <span>
                      {
                        item.candidate_name
                      }
                    </span>

                    <span>
                      {
                        item.candidate_email
                      }
                    </span>

                    <span>
                      {item.role}
                    </span>

                    <span className="code">
                      {
                        item.interview_id
                      }
                    </span>

                    <span
                      className={getStatusClass(
                        item.status
                      )}
                    >
                      {getStatusLabel(
                        item.status
                      )}
                    </span>

                    <span className="link-cell">

                      {item.candidate_link ? (

                        <button
                          type="button"
                          className="link-button"
                          onClick={() =>
                            copyLink(
                              item.candidate_link
                            )
                          }
                        >
                          COPY LINK
                        </button>

                      ) : (

                        <span className="no-link">
                          Not available
                        </span>

                      )}

                    </span>


                    <span>

                      <button
                        type="button"
                        onClick={() =>
                          navigate(
                            `/admin/report/${item.interview_id}`
                          )
                        }
                      >
                        VIEW
                      </button>

                    </span>

                  </div>

                )
              )}

            </div>

          )}

        </section>


        {/* =====================================================
            LIVE MONITOR
            ===================================================== */}

        <section
          className="live-section candidates-section"
        >

          <div className="section-header">

            <h2>
              Live Interview Monitor
            </h2>

            <span>
              Two-way video + AI
              monitoring
            </span>

          </div>


          {stats.active ===
          0 ? (

            <div className="empty-state">

              <h3>
                No active interview
              </h3>

              <p>
                When a candidate starts
                an interview, the live
                video and AI information
                will appear here.
              </p>

            </div>

          ) : (

            interviews
              .filter(
                (item) =>
                  item.status ===
                  "active"
              )
              .map(
                (item) => (
                  <LiveInterviewCard
                    key={
                      item.interview_id
                    }
                    item={item}
                    state={
                      live[
                        item.interview_id
                      ]
                    }
                    token={token}
                  />
                )
              )

          )}

        </section>

      </main>

    </div>
  );
}


export default AdminDashboard;