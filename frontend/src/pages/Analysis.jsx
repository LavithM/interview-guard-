import "./Analysis.css";

function Analysis() {
  return (
    <div className="analysis-page">

      <div className="analysis-container">

        {/* HEADER */}

        <div className="analysis-header">

          <div>
            <p className="report-label">
              INTERVIEWGUARD
            </p>

            <h1>
              Interview Analysis Report
            </h1>

            <p className="report-subtitle">
              Your interview has been completed successfully.
            </p>
          </div>

          <div className="completed-badge">
            ✓ Completed
          </div>

        </div>


        {/* OVERALL SCORE */}

        <div className="overall-card">

          <div className="score-circle">
            <strong>82</strong>
            <span>/100</span>
          </div>

          <div className="overall-info">

            <h2>
              Overall Interview Score
            </h2>

            <p>
              Your interview was analyzed using multiple
              behavioral and audio-visual signals.
            </p>

            <div className="score-status">
              Analysis Completed
            </div>

          </div>

        </div>


        {/* ANALYSIS CARDS */}

        <div className="analysis-grid">

          <div className="metric-card">

            <div className="metric-icon">
              👁
            </div>

            <div>
              <h3>
                Gaze Analysis
              </h3>

              <p>
                Eye movement and gaze direction
              </p>

              <strong>
                85%
              </strong>
            </div>

          </div>


          <div className="metric-card">

            <div className="metric-icon">
              🧠
            </div>

            <div>
              <h3>
                Head Movement
              </h3>

              <p>
                Head pose and movement analysis
              </p>

              <strong>
                78%
              </strong>
            </div>

          </div>


          <div className="metric-card">

            <div className="metric-icon">
              🎤
            </div>

            <div>
              <h3>
                Audio Analysis
              </h3>

              <p>
                Voice and speech consistency
              </p>

              <strong>
                90%
              </strong>
            </div>

          </div>


          <div className="metric-card">

            <div className="metric-icon">
              👄
            </div>

            <div>
              <h3>
                Lip Sync
              </h3>

              <p>
                Audio and lip movement consistency
              </p>

              <strong>
                81%
              </strong>
            </div>

          </div>

        </div>


        {/* INTERVIEW SUMMARY */}

        <div className="report-section">

          <h2>
            Interview Summary
          </h2>

          <div className="summary-grid">

            <div>
              <span>
                Interview Duration
              </span>

              <strong>
                18:42
              </strong>
            </div>

            <div>
              <span>
                Questions
              </span>

              <strong>
                10
              </strong>
            </div>

            <div>
              <span>
                Suspicious Events
              </span>

              <strong className="warning">
                2
              </strong>
            </div>

            <div>
              <span>
                Recording
              </span>

              <strong className="success">
                Verified
              </strong>
            </div>

          </div>

        </div>


        {/* BEHAVIORAL ANALYSIS */}

        <div className="report-section">

          <h2>
            Behavioral Analysis
          </h2>

          <div className="behavior-row">

            <div className="behavior-info">

              <span>
                Eye Contact
              </span>

              <strong>
                85%
              </strong>

            </div>

            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: "85%" }}
              ></div>
            </div>

          </div>


          <div className="behavior-row">

            <div className="behavior-info">

              <span>
                Head Stability
              </span>

              <strong>
                78%
              </strong>

            </div>

            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: "78%" }}
              ></div>
            </div>

          </div>


          <div className="behavior-row">

            <div className="behavior-info">

              <span>
                Audio-Visual Consistency
              </span>

              <strong>
                81%
              </strong>

            </div>

            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: "81%" }}
              ></div>
            </div>

          </div>

        </div>


        {/* SUSPICIOUS EVENTS */}

        <div className="report-section">

          <h2>
            Detected Events
          </h2>

          <div className="event-item">

            <span className="event-warning">
              !
            </span>

            <div>
              <strong>
                Unusual gaze movement
              </strong>

              <p>
                Detected around 06:32
              </p>
            </div>

          </div>


          <div className="event-item">

            <span className="event-warning">
              !
            </span>

            <div>
              <strong>
                Audio-visual inconsistency
              </strong>

              <p>
                Detected around 13:47
              </p>
            </div>

          </div>

        </div>


        {/* FINAL STATUS */}

        <div className="final-status">

          <div className="final-icon">
            ✓
          </div>

          <div>

            <h2>
              Analysis Completed
            </h2>

            <p>
              Your interview recording and behavioral signals
              have been successfully processed.
            </p>

          </div>

        </div>

      </div>

    </div>
  );
}

export default Analysis;