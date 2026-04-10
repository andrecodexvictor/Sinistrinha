export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next: string | null;
  previous: string | null;
}

export interface WinFeedItem {
  id: string;
  username: string;
  amount: number;
  symbolName: string;
  symbolIcon: string;
  timestamp: string;
}

export interface LeaderboardEntry {
  rank: number;
  username: string;
  level: number;
  totalWinnings: number;
}
