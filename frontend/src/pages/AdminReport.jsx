import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "./AdminReport.css";
import { apiFetch, getAdminToken } from "../api";

function AdminReport() {
  const { id } = useParams();
  const navigate = useNavigate();
  const token = getAdminToken();
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) {
      navigate("/admin");
      return;
    }

    apiFetch(`/admin/interviews/${id}/report`, {}, token)
      .then((data) => setReport(data))
      .catch((err) => setError(err.message));
  }, [id, token, navigate]);

  if (error) {
    return (
      <div className="admin-report-page">
        <div className="report-card">
          <h1>Report unavailable</h1>
          <p>{error}</p>
          <button onClick={() => navigate("/admin/dashboard")}>BACK TO DASHBOARD</button>
        </div>
      </div>
    );
  }

  if (!report) {
    return <div className="admin-report-page"><div className="report-card"><h1>Loading report...</h1></div></div>;
  }

  const data = report.report || {};
  const indicators = data.indicator_counts || {};
  const temporal = data.temporal_analysis || {};
  const objectAnalysis = data.object_analysis || {};
  const speech = data.speech_analysis || {};

  return (
    <div className="admin-report-page">
      <header className="report-header">
        <div>
          <h1>Interview Report</h1>
          <p>InterviewGuard Admin Portal</p>
        </div>
        <button className="back-button" onClick={() => navigate("/admin/dashboard")}>← BACK TO DASHBOARD</button>
      </header>

      <main className="report-content">
        <section className="report-card">
          <h2>Candidate Information</h2>
          <div className="candidate-details">
            <div><span>Name</span><strong>{report.candidate_name}</strong></div>
            <div><span>Email</span><strong>{report.candidate_email}</strong></div>
            <div><span>Role</span><strong>{report.role}</strong></div>
            <div><span>Status</span><strong>{report.status}</strong></div>
          </div>
        </section>

        <section className="report-card">
          <h2>Interview Summary</h2>
          <div className="analysis-grid">
            <div className="analysis-item"><span>Feature Windows</span><strong>{data.total_feature_windows ?? 0}</strong></div>
            <div className="analysis-item"><span>Face Presence</span><strong>{data.face_presence_percentage != null ? `${Number(data.face_presence_percentage).toFixed(1)}%` : "-"}</strong></div>
            <div className="analysis-item"><span>Speech Percentage</span><strong>{data.speech_percentage != null ? `${Number(data.speech_percentage).toFixed(1)}%` : "-"}</strong></div>
            <div className="analysis-item"><span>Average Gaze</span><strong>{data.average_gaze != null ? Number(data.average_gaze).toFixed(2) : "-"}</strong></div>
          </div>
        </section>

        <section className="report-card">
          <h2>AI Behaviour Evidence</h2>
          {Object.keys(indicators).length === 0 ? <p>No indicators recorded.</p> : Object.entries(indicators).map(([key, value]) => (
            <div className="event-item" key={key}>
              <span className="event-warning">{value}</span>
              <div><strong>{key.replaceAll("_", " ")}</strong><p>Observed in {value} feature window(s).</p></div>
            </div>
          ))}
          <p style={{ color: "#6b7280", fontSize: 13 }}>
            Evidence indicators are shown for administrator review. They should not be treated as proof of cheating by themselves.
          </p>
        </section>

        <section className="report-card">
          <h2>Object Analysis</h2>
          <div className="analysis-grid">
            <div className="analysis-item"><span>Multiple People Windows</span><strong>{objectAnalysis.multiple_people_windows ?? 0}</strong></div>
            <div className="analysis-item"><span>Mobile Phone Windows</span><strong>{objectAnalysis.mobile_phone_windows ?? 0}</strong></div>
          </div>
        </section>

        <section className="report-card">
          <h2>Speech Analysis</h2>
          <div className="analysis-grid">
            <div className="analysis-item"><span>Words</span><strong>{speech.total_words ?? 0}</strong></div>
            <div className="analysis-item"><span>Filler Words</span><strong>{speech.filler_word_count ?? 0}</strong></div>
          </div>
          {speech.transcript && <p style={{ whiteSpace: "pre-wrap", marginTop: 20 }}>{speech.transcript}</p>}
        </section>

        <section className="report-card">
          <h2>Temporal Analysis</h2>
          <div className="analysis-grid">
            {Object.entries(temporal).map(([key, value]) => (
              <div className="analysis-item" key={key}><span>{key.replaceAll("_", " ")}</span><strong>{String(value)}</strong></div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}

export default AdminReport;
