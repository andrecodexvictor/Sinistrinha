import { create } from 'zustand';
import type { WinFeedItem } from '../types/api.types';
import { SYMBOLS, SYMBOL_KEYS } from '../types/game.types';
import { getTokens } from '../lib/api';

// Generate fake feed items for initial display
function generateFakeWin(): WinFeedItem {
  const names = ['CyberGorila', 'H4ck3rPro', 'ByteKing', 'PixelNinja', 'RAMaster', 'GPUlord', 'CodeMonkey', 'NerdBoss', 'BugHunter', 'BitCrusher'];
  const symKey = SYMBOL_KEYS[Math.floor(Math.random() * (SYMBOL_KEYS.length - 2))];
  const symbol = SYMBOLS[symKey];
  const amount = Math.random() < 0.1
    ? Math.floor(Math.random() * 5000) + 1000
    : Math.random() < 0.3
      ? Math.floor(Math.random() * 500) + 100
      : Math.floor(Math.random() * 100) + 5;

  return {
    id: crypto.randomUUID(),
    username: names[Math.floor(Math.random() * names.length)],
    amount,
    symbolName: symbol.name,
    symbolIcon: symbol.icon,
    timestamp: new Date().toISOString(),
  };
}

interface CasinoState {
  winsFeed: WinFeedItem[];
  jackpotValue: number;
  isConnected: boolean;
  ws: WebSocket | null;

  addWin: (win: WinFeedItem) => void;
  setJackpot: (value: number) => void;
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
  generateFakeWins: (count: number) => void;
}

export const useCasinoStore = create<CasinoState>((set, get) => ({
  winsFeed: Array.from({ length: 15 }, () => generateFakeWin()),
  jackpotValue: 25000,
  isConnected: false,
  ws: null,

  addWin: (win) =>
    set((state) => ({
      winsFeed: [win, ...state.winsFeed].slice(0, 50),
    })),

  setJackpot: (jackpotValue) => set({ jackpotValue }),

  /** Connect to the public casino_live WebSocket for real-time wins */
  connectWebSocket: () => {
    const existing = get().ws;
    if (existing && existing.readyState === WebSocket.OPEN) return;

    const wsBase = import.meta.env.VITE_WS_URL || window.location.origin.replace('http', 'ws');
    const ws = new WebSocket(`${wsBase}/ws/casino/`);

    ws.onopen = () => {
      set({ isConnected: true, ws });
    };

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === 'recent_win') {
          const msg = payload.message;
          const win: WinFeedItem = {
            id: crypto.randomUUID(),
            username: msg.username || 'Anônimo',
            amount: msg.amount || 0,
            symbolName: msg.symbol || '🎰',
            symbolIcon: msg.symbol || '🎰',
            timestamp: new Date().toISOString(),
          };
          get().addWin(win);
        }
        if (payload.type === 'jackpot_update') {
          set({ jackpotValue: payload.message.jackpot_amount });
        }
      } catch { /* ignore malformed messages */ }
    };

    ws.onclose = () => {
      set({ isConnected: false, ws: null });
      // Reconnect after 3 seconds
      setTimeout(() => get().connectWebSocket(), 3000);
    };

    ws.onerror = () => {
      ws.close();
    };
  },

  disconnectWebSocket: () => {
    const ws = get().ws;
    if (ws) ws.close();
    set({ ws: null, isConnected: false });
  },

  generateFakeWins: (count) => {
    const newWins = Array.from({ length: count }, () => generateFakeWin());
    set((state) => ({
      winsFeed: [...newWins, ...state.winsFeed].slice(0, 50),
    }));
  },
}));

/**
 * Connect to the private player WebSocket channel.
 * Used for balance/level/free-spins real-time updates.
 */
export function connectPlayerWebSocket(
  userId: number,
  callbacks: {
    onBalanceUpdate?: (balance: number) => void;
    onLevelUp?: (data: Record<string, unknown>) => void;
    onFreeSpinsUpdate?: (freeSpins: number) => void;
  },
): WebSocket | null {
  const tokens = getTokens();
  if (!tokens?.access) return null;

  const wsBase = import.meta.env.VITE_WS_URL || window.location.origin.replace('http', 'ws');
  const ws = new WebSocket(`${wsBase}/ws/user/${userId}/?token=${tokens.access}`);

  ws.onmessage = (event) => {
    try {
      const payload = JSON.parse(event.data);
      if (payload.type === 'balance_update' && callbacks.onBalanceUpdate) {
        callbacks.onBalanceUpdate(payload.data?.balance ?? payload.message?.balance);
      }
      if (payload.type === 'level_up' && callbacks.onLevelUp) {
        callbacks.onLevelUp(payload.data ?? payload.message);
      }
      if (payload.type === 'free_spins_update' && callbacks.onFreeSpinsUpdate) {
        callbacks.onFreeSpinsUpdate(payload.data?.free_spins ?? payload.message?.free_spins);
      }
    } catch { /* ignore */ }
  };

  return ws;
}
