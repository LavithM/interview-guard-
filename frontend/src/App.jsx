import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Candidate from "./pages/candidate";
import Ready from "./pages/Ready";
import Interview from "./pages/Interview";

import AdminLogin from "./pages/admin/AdminLogin";
import AdminDashboard from "./pages/AdminDashboard";
import AdminReport from "./pages/AdminReport";

function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Candidate */}
        <Route path="/" element={<Candidate />} />
        <Route path="/candidate" element={<Candidate />} />

        {/* Candidate invitation link */}
        <Route path="/candidate/login" element={<Candidate />} />

        <Route path="/ready" element={<Ready />} />
        <Route path="/interview/:invitationToken" element={<Candidate />} />
        <Route path="/interview/session" element={<Interview />} />

        <Route
          path="/interview"
          element={<Navigate to="/candidate" replace />}
        />

        {/* Admin */}
        <Route path="/admin" element={<AdminLogin />} />
        <Route path="/admin/login" element={<AdminLogin />} />
        <Route path="/admin/dashboard" element={<AdminDashboard />} />
        <Route path="/admin/report/:id" element={<AdminReport />} />
        <Route path="/admin/report" element={<AdminReport />} />

      </Routes>
    </BrowserRouter>
  );
}

export default App;