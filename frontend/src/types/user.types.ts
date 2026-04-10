export interface User {
  id: string;
  username: string;
  email: string;
  avatarUrl?: string;
  level: number;
  xp: number;
  balance: number;
  createdAt: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
}
