import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./AdminLogin.css";
import { apiFetch } from "../../api";

function AdminLogin() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    if (!email.trim() || !password) {
      setError("Please enter email and password.");
      return;
    }

    try {
      setLoading(true);
      const data = await apiFetch("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: email.trim(),
          password,
        }),
      });

      if (data.user?.role !== "admin") {
        throw new Error("This account is not an admin account.");
      }

      localStorage.setItem(
        "interviewguard_admin_token",
        data.access_token
      );
      localStorage.setItem(
        "interviewguard_admin_user",
        JSON.stringify(data.user)
      );

      navigate("/admin/dashboard");
    } catch (err) {
      setError(err.message || "Login failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-login-page">
      <div className="admin-login-card">
        <div className="admin-logo">InterviewGuard</div>
        <p className="admin-label">ADMIN PORTAL</p>
        <h1>Welcome Back</h1>
        <p className="admin-subtitle">
          Sign in to manage interviews and candidates.
        </p>

        <form onSubmit={handleLogin}>
          <label>Admin Email</label>
          <input
            type="email"
            placeholder="Enter admin email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <label>Password</label>
          <input
            type="password"
            placeholder="Enter password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {error && <p className="admin-error">{error}</p>}

          <button type="submit" disabled={loading}>
            {loading ? "LOGGING IN..." : "ADMIN LOGIN"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default AdminLogin;
