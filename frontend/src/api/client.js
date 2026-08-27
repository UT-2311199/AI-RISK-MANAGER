import axios from 'axios';

const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Auto-attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auto-logout on 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ── Auth ──────────────────────────────────────────────────────────────────
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
};

// ── Projects ──────────────────────────────────────────────────────────────
export const projectsAPI = {
  list: () => api.get('/projects'),
  get: (id) => api.get(`/projects/${id}`),
  create: (data) => api.post('/projects', data),
  delete: (id) => api.delete(`/projects/${id}`),
  analyze: (id, data = {}) => api.post(`/projects/${id}/analyze`, data),
};

// ── Risks ─────────────────────────────────────────────────────────────────
export const risksAPI = {
  list: (projectId) => api.get(`/projects/${projectId}/risks`),
  get: (id) => api.get(`/risks/${id}`),
  updateStatus: (id, status) => api.patch(`/risks/${id}/status`, { status }),
  delete: (id) => api.delete(`/risks/${id}`),
};

export default api;
