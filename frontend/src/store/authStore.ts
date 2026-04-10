import { create } from 'zustand';
import type { User, AuthTokens } from '../types/user.types';

interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  setUser: (user: User) => void;
  setTokens: (tokens: AuthTokens) => void;
  login: (user: User, tokens: AuthTokens) => void;
  logout: () => void;
  setLoading: (loading: boolean) => void;
  updateBalance: (balance: number) => void;
  updateLevel: (level: number, xp: number) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  tokens: null,
  isAuthenticated: false,
  isLoading: false,

  setUser: (user) => set({ user }),
  setTokens: (tokens) => set({ tokens }),
  login: (user, tokens) => set({ user, tokens, isAuthenticated: true }),
  logout: () => {
    localStorage.removeItem('tokens');
    set({ user: null, tokens: null, isAuthenticated: false });
  },
  setLoading: (isLoading) => set({ isLoading }),
  updateBalance: (balance) =>
    set((state) => ({
      user: state.user ? { ...state.user, balance } : null,
    })),
  updateLevel: (level, xp) =>
    set((state) => ({
      user: state.user ? { ...state.user, level, xp } : null,
    })),
}));
