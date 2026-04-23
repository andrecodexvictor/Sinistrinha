import { create } from 'zustand';
import type { User, AuthTokens, UserProfile } from '../types/user.types';
import { profileToUser } from '../types/user.types';
import api, { setTokens, clearTokens, getTokens } from '../lib/api';

interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  /** Attempt login via backend JWT endpoint */
  loginAsync: (username: string, password: string) => Promise<boolean>;
  /** Register a new account, then auto-login */
  registerAsync: (username: string, email: string, password: string) => Promise<boolean>;
  /** Fetch profile from backend and update local user state */
  fetchProfile: () => Promise<void>;
  /** Logout: blacklist refresh token + clear local state */
  logout: () => Promise<void>;
  /** Restore session from localStorage on app init */
  restoreSession: () => Promise<void>;
  /** Manual setters for WebSocket-driven updates */
  updateBalance: (balance: number) => void;
  updateLevel: (level: number, xp: number) => void;
  updateFreeSpins: (freeSpins: number) => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  tokens: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  loginAsync: async (username, password) => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await api.post<AuthTokens>('/auth/login/', { username, password });
      setTokens(data);
      set({ tokens: data, isAuthenticated: true });
      await get().fetchProfile();
      set({ isLoading: false });
      return true;
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
        || 'Login failed';
      set({ isLoading: false, error: msg });
      return false;
    }
  },

  registerAsync: async (username, email, password) => {
    set({ isLoading: true, error: null });
    try {
      await api.post('/auth/register/', { username, email, password });
      // Auto-login after successful registration
      return await get().loginAsync(username, password);
    } catch (err: unknown) {
      const data = (err as { response?: { data?: Record<string, string[]> } })?.response?.data;
      const msg = data
        ? Object.values(data).flat().join('; ')
        : 'Registration failed';
      set({ isLoading: false, error: msg });
      return false;
    }
  },

  fetchProfile: async () => {
    try {
      const { data } = await api.get<UserProfile>('/user/profile/');
      const user = profileToUser(data);
      set({ user });
    } catch {
      // Profile fetch failed — token may be invalid
      set({ user: null, isAuthenticated: false });
      clearTokens();
    }
  },

  logout: async () => {
    const tokens = getTokens();
    try {
      if (tokens?.refresh) {
        await api.post('/auth/logout/', { refresh_token: tokens.refresh });
      }
    } catch {
      // Ignore — server may already have invalidated
    }
    clearTokens();
    set({ user: null, tokens: null, isAuthenticated: false, error: null });
  },

  restoreSession: async () => {
    const tokens = getTokens();
    if (!tokens?.access) return;
    set({ tokens, isAuthenticated: true, isLoading: true });
    await get().fetchProfile();
    set({ isLoading: false });
  },

  updateBalance: (balance) =>
    set((s) => ({ user: s.user ? { ...s.user, balance } : null })),

  updateLevel: (level, xp) =>
    set((s) => ({ user: s.user ? { ...s.user, level, xp } : null })),

  updateFreeSpins: (freeSpins) =>
    set((s) => ({ user: s.user ? { ...s.user, freeSpins } : null })),

  setLoading: (isLoading) => set({ isLoading }),
}));
