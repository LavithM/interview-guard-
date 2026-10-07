export const API_BASE =
  import.meta.env.VITE_API_BASE_URL ||
  `${window.location.protocol}//${window.location.hostname}:8000`;

export function getAdminToken() {
  return localStorage.getItem("interviewguard_admin_token");
}

export function getCandidateToken() {
  return (
    sessionStorage.getItem("interviewguard_candidate_token") ||
    localStorage.getItem("candidate_access_token")
  );
}

export async function apiFetch(path, options = {}, explicitToken = null) {
  const token =
    explicitToken ||
    options.token ||
    localStorage.getItem("interviewguard_admin_token") ||
    localStorage.getItem("candidate_access_token");

  const headers = {
    ...(options.headers || {}),
  };

  // Do NOT manually set Content-Type for FormData.
  // The browser must create the multipart boundary itself.
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const controller = new AbortController();

  // Prevent the UI from loading forever.
  const timeout = setTimeout(() => {
    controller.abort();
  }, 10000);

  try {
    console.log("InterviewGuard API request:", `${API_BASE}${path}`);

    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
      signal: controller.signal,
    });

    let data = null;

    try {
      data = await response.json();
    } catch {
      data = null;
    }

    console.log(
      "InterviewGuard API response:",
      response.status,
      data
    );

    if (!response.ok) {
      let message = `Request failed with status ${response.status}`;

      if (data?.detail !== undefined) {
        message =
          typeof data.detail === "string"
            ? data.detail
            : JSON.stringify(data.detail);
      } else if (data?.message !== undefined) {
        message =
          typeof data.message === "string"
            ? data.message
            : JSON.stringify(data.message);
      }

      const error = new Error(message);
      error.status = response.status;
      error.data = data;

      throw error;
    }

    return data;
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error(
        `Backend request timed out. Cannot reach ${API_BASE}`
      );
    }

    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

export function wsUrl(path, token) {
  const base = API_BASE.replace(/^http/, "ws");

  const separator = path.includes("?") ? "&" : "?";

  return `${base}${path}${separator}token=${encodeURIComponent(token)}`;
}