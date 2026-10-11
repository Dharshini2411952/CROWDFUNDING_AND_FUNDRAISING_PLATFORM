import axios from "axios";

const rawApiUrl = import.meta.env.VITE_API_URL;
const defaultUrl = import.meta.env.PROD
  ? "https://crowdfunding-and-fundraising-platform.onrender.com"
  : "http://127.0.0.1:8000";
const baseURL = (rawApiUrl ? rawApiUrl.replace(/\/+$/, "") : defaultUrl).replace(/\/+$/, "");

const api = axios.create({
  baseURL,
  timeout: 45000,
  headers: {
    "Content-Type": "application/json",
  },
});


api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("role");
      localStorage.removeItem("name");
      localStorage.removeItem("email");
      localStorage.removeItem("user_id");
    }

    return Promise.reject(error);
  }
);

export default api;
