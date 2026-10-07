import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./AdminLogin.css";

function AdminLogin() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = (e) => {
    e.preventDefault();

    setError("");

    if (!email.trim() || !password.trim()) {
      setError("Please enter email and password.");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

    if (!emailRegex.test(email.trim())) {
      setError("Please enter a valid email address.");
      return;
    }

    // Temporary admin login.
    // We will replace this with backend authentication later.
    if (
      email.trim() === "admin@interviewguard.com" &&
      password === "admin123"
    ) {
      navigate("/admin/dashboard");
    } else {
      setError("Invalid admin email or password.");
    }
  };

  return (
    <div className="admin-login-page">
      <div className="admin-login-card">

        <div className="admin-logo">
          InterviewGuard
        </div>

        <p className="admin-label">
          ADMIN PORTAL
        </p>

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

          {error && (
            <p className="admin-error">
              {error}
            </p>
          )}

          <button type="submit">
            ADMIN LOGIN
          </button>

        </form>

      </div>
    </div>
  );
}

export default AdminLogin;