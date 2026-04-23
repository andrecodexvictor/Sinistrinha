/** Generic wrapper — DRF doesn't wrap in {data,success}, but useful for custom endpoints */
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

/** DRF PageNumberPagination shape */
export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next: string | null;
  previous: string | null;
}

/** Win feed item (used in casino sidebar) */
export interface WinFeedItem {
  id: string;
  username: string;
  amount: number;
  symbolName: string;
  symbolIcon: string;
  timestamp: string;
}

/** Leaderboard entry mapped from UserProfileSerializer */
export interface LeaderboardEntry {
  rank: number;
  username: string;
  level: number;
  totalWon: number;
  balance: number;
}

/** Backend Transaction model shape */
export interface Transaction {
  id: number;
  user: number;
  amount: string;
  transaction_type: 'deposit' | 'withdraw' | 'bet' | 'win' | 'bonus';
  status: 'pending' | 'completed' | 'failed' | 'cancelled';
  external_id: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

/** Backend SpinHistory model shape (from SpinHistorySerializer fields='__all__') */
export interface SpinHistoryEntry {
  id: number;
  spin_id: string;
  user: number;
  bet_amount: string;
  result_reels: string[];
  payout: string;
  combination_type: string;
  xp_earned: number;
  rtp_at_spin: number;
  near_miss: boolean;
  is_free_spin: boolean;
  jackpot_contribution: string;
  wild_used: boolean;
  timestamp: string;
}
