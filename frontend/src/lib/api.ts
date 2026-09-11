const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

async function fetchWithAuth(path: string, options: RequestInit = {}) {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const headers = new Headers(options.headers);

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401 && typeof window !== "undefined") {
    localStorage.removeItem("token");
    if (!window.location.pathname.startsWith("/login") && !window.location.pathname.startsWith("/register")) {
      window.location.href = "/login";
    }
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "API request failed");
  }

  return response.json();
}

export const api = {
  auth: {
    login: (data: any) => fetchWithAuth("/api/auth/login", { method: "POST", body: JSON.stringify(data) }),
    register: (data: any) => fetchWithAuth("/api/auth/register", { method: "POST", body: JSON.stringify(data) }),
    me: () => fetchWithAuth("/api/auth/me"),
  },
  reflections: {
    create: (data: any) => fetchWithAuth("/api/reflections/", { method: "POST", body: JSON.stringify(data) }),
    list: (skip = 0, limit = 10) => fetchWithAuth(`/api/reflections/?skip=${skip}&limit=${limit}`),
    today: () => fetchWithAuth("/api/reflections/today"),
    get: (id: string) => fetchWithAuth(`/api/reflections/${id}`),
    delete: (id: string) => fetchWithAuth(`/api/reflections/${id}`, { method: "DELETE" }),
    deleteToday: () => fetchWithAuth("/api/reflections/today", { method: "DELETE" }),
    followup: (id: string, data: any) => fetchWithAuth(`/api/reflections/${id}/followup`, { method: "POST", body: JSON.stringify(data) }),
    weekly: () => fetchWithAuth("/api/reflections/weekly"),
    monthly: () => fetchWithAuth("/api/reflections/monthly"),
  },
  experiments: {
    list: () => fetchWithAuth("/api/experiments/"),
    pending: () => fetchWithAuth("/api/experiments/pending"),
    stats: () => fetchWithAuth("/api/experiments/stats"),
    respond: (id: string, data: any) => fetchWithAuth(`/api/experiments/${id}/respond`, { method: "POST", body: JSON.stringify(data) }),
    review: (id: string, data: any) => fetchWithAuth(`/api/experiments/${id}/review`, { method: "POST", body: JSON.stringify(data) }),
  },
  emotions: {
    trends: (range = "7d") => fetchWithAuth(`/api/emotions/trends?range=${range}`),
    heatmap: (range = "30d") => fetchWithAuth(`/api/emotions/heatmap?range=${range}`),
    triggers: () => fetchWithAuth("/api/emotions/triggers"),
  },
  goals: {
    list: () => fetchWithAuth("/api/goals/"),
    create: (data: any) => fetchWithAuth("/api/goals/", { method: "POST", body: JSON.stringify(data) }),
    update: (id: string, data: any) => fetchWithAuth(`/api/goals/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
    interests: () => fetchWithAuth("/api/goals/interests"),
    respondInterest: (id: string, data: any) => fetchWithAuth(`/api/goals/interests/${id}/respond`, { method: "POST", body: JSON.stringify(data) }),
  },
  stats: {
    get: () => fetchWithAuth("/api/stats/"),
    achievements: () => fetchWithAuth("/api/stats/achievements"),
  },
  user: {
    export: () => fetchWithAuth("/api/user/export"),
    deleteAccount: () => fetchWithAuth("/api/user/account", { method: "DELETE" }),
    feedback: (data: any) => fetchWithAuth("/api/user/feedback", { method: "POST", body: JSON.stringify(data) }),
  },
};
