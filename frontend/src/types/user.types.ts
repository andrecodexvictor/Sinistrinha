// ========== User types matching Django backend ==========

/** Matches the nested shape from UserProfileSerializer */
export interface UserProfile {
  id: number;
  user: {
    id: number;
    username: string;
    email: string;
  };
  balance: string;          // Decimal comes as string from DRF
  level: number;
  xp: number;
  total_spins: number;
  total_wagered: string;
  total_won: string;
  free_spins: number;
  current_multiplier: number;
  created_at: string;
  avatar_url: string;
  is_vip: boolean;
}

/** Convenience flat user object used in UI state */
export interface User {
  id: number;
  username: string;
  email: string;
  avatarUrl?: string;
  level: number;
  xp: number;
  balance: number;
  freeSpins: number;
  createdAt: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginPayload {
  username: string;   // SimpleJWT expects "username"
  password: string;
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
}

/** Convert the nested backend profile into a flat UI User */
export function profileToUser(profile: UserProfile): User {
  return {
    id: profile.user.id,
    username: profile.user.username,
    email: profile.user.email,
    avatarUrl: profile.avatar_url || undefined,
    level: profile.level,
    xp: profile.xp,
    balance: parseFloat(profile.balance),
    freeSpins: profile.free_spins,
    createdAt: profile.created_at,
  };
}
