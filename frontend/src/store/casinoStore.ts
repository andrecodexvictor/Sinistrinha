import { create } from 'zustand';
import type { WinFeedItem } from '../types/api.types';
import { SYMBOLS, SYMBOL_KEYS } from '../types/game.types';

// Generate fake feed items for demo purposes
function generateFakeWin(): WinFeedItem {
  const names = ['CyberGorila', 'H4ck3rPro', 'ByteKing', 'PixelNinja', 'RAMaster', 'GPUlord', 'CodeMonkey', 'NerdBoss', 'BugHunter', 'BitCrusher'];
  const symKey = SYMBOL_KEYS[Math.floor(Math.random() * (SYMBOL_KEYS.length - 2))]; // exclude wild/scatter
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

  addWin: (win: WinFeedItem) => void;
  setJackpot: (value: number) => void;
  setConnected: (connected: boolean) => void;
  generateFakeWins: (count: number) => void;
}

export const useCasinoStore = create<CasinoState>((set) => ({
  winsFeed: Array.from({ length: 15 }, () => generateFakeWin()),
  jackpotValue: 25000,
  isConnected: false,

  addWin: (win) =>
    set((state) => ({
      winsFeed: [win, ...state.winsFeed].slice(0, 50),
    })),

  setJackpot: (jackpotValue) => set({ jackpotValue }),
  setConnected: (isConnected) => set({ isConnected }),

  generateFakeWins: (count) =>
    set((state) => {
      const newWins = Array.from({ length: count }, () => generateFakeWin());
      return { winsFeed: [...newWins, ...state.winsFeed].slice(0, 50) };
    }),
}));
