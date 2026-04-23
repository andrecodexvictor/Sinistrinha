/**
 * api.ts — Centralized Axios client with JWT interceptor.
 *
 * All frontend API calls go through this instance.
 * - Attaches Authorization header automatically.
 * - Handles 401 by attempting token refresh, then retrying.
 */

import axios from 'axios';
import type { AxiosError, InternalAxiosRequestConfig } from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: `${API_BASE}/api`,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
});

// ---- Token helpers (localStorage) ----------------------------------------

export function getTokens() {
  const raw = localStorage.getItem('tokens');
  if (!raw) return null;
  try {
    return JSON.parse(raw) as { access: string; refresh: string };
  } catch {
    return null;
  }
}

export function setTokens(tokens: { access: string; refresh: string }) {
  localStorage.setItem('tokens', JSON.stringify(tokens));
}

export function clearTokens() {
  localStorage.removeItem('tokens');
}

// ---- Request interceptor: attach access token ----------------------------

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const tokens = getTokens();
  if (tokens?.access && config.headers) {
    config.headers.Authorization = `Bearer ${tokens.access}`;
  }
  return config;
});

// ---- Response interceptor: auto-refresh on 401 --------------------------

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (err: unknown) => void;
}> = [];

function processQueue(error: unknown, token: string | null) {
  failedQueue.forEach((prom) => {
    if (token) prom.resolve(token);
    else prom.reject(error);
  });
  failedQueue = [];
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status === 401 && !originalRequest._retry) {
      const tokens = getTokens();
      if (!tokens?.refresh) {
        clearTokens();
        window.location.href = '/login';
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({
            resolve: (token: string) => {
              if (originalRequest.headers) {
                originalRequest.headers.Authorization = `Bearer ${token}`;
              }
              resolve(api(originalRequest));
            },
            reject,
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const { data } = await axios.post(`${API_BASE}/api/auth/refresh/`, {
          refresh: tokens.refresh,
        });
        setTokens({ access: data.access, refresh: data.refresh ?? tokens.refresh });
        processQueue(null, data.access);
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${data.access}`;
        }
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        clearTokens();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  },
);

export default api;
