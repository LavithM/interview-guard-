import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";

function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [examCode, setExamCode] = useState("");
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    const newErrors = {};

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
    const examCodeRegex = /^[A-Za-z0-9-]+$/;

    if (!email.trim()) {
      newErrors.email = "Email is required";
    } else if (!emailRegex.test(email.trim())) {
      newErrors.email = "Enter a valid email address";
    }

    if (!examCode.trim()) {
      newErrors.examCode = "Exam code is required";
    } else if (!examCodeRegex.test(examCode.trim())) {
      newErrors.examCode =
        "Exam code can contain only letters, numbers and -";
    }

    setErrors(newErrors);

    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (validateForm()) {
      navigate("/verification");
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">

        <h1>InterviewGuard</h1>

        <p className="login-subtitle">
          Candidate Login
        </p>

        <p className="login-description">
          Enter the email ID and exam code provided by your company.
        </p>

        <form onSubmit={handleSubmit}>

          <label>Company Email ID</label>

          <input
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          {errors.email && (
            <small className="error">
              {errors.email}
            </small>
          )}

          <label>Exam Code</label>

          <input
            type="text"
            placeholder="e.g. IG-2026-AX72"
            value={examCode}
            onChange={(e) => setExamCode(e.target.value)}
          />

          {errors.examCode && (
            <small className="error">
              {errors.examCode}
            </small>
          )}

          <button type="submit">
            LOGIN
          </button>

        </form>

      </div>
    </div>
  );
}

export default Login;