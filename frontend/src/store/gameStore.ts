import { create } from 'zustand';
import type { SpinResult } from '../types/game.types';
import { SYMBOLS, SYMBOL_KEYS } from '../types/game.types';

// Generate a random reel column (3 visible symbols)
function randomReelColumn(): string[] {
  return Array.from({ length: 3 }, () =>
    SYMBOL_KEYS[Math.floor(Math.random() * SYMBOL_KEYS.length)]
  );
}

// Generate all 5 reels
function generateRandomReels(): string[][] {
  return Array.from({ length: 5 }, () => randomReelColumn());
}

// Simple local win check (client-side simulation; real results come from backend)
function checkWin(reels: string[][], bet: number): SpinResult {
  const middleRow = reels.map((col) => col[1]); // center symbol of each reel
  const winningLines: SpinResult['winningLines'] = [];

  // Check consecutive matches from left
  let matchCount = 1;
  const firstSym = middleRow[0];
  for (let i = 1; i < 5; i++) {
    if (middleRow[i] === firstSym || middleRow[i] === 'wild') {
      matchCount++;
    } else {
      break;
    }
  }

  let totalWin = 0;
  if (matchCount >= 3) {
    const symbol = SYMBOLS[firstSym];
    const payout = bet * symbol.multiplier * (matchCount - 2);
    totalWin = payout;
    winningLines.push({
      lineIndex: 0,
      symbols: middleRow.slice(0, matchCount),
      multiplier: symbol.multiplier,
      payout,
    });
  }

  // Scatter bonus: 3+ scatters anywhere
  const scatterCount = middleRow.filter((s) => s === 'scatter').length;
  if (scatterCount >= 3) {
    const scatterPay = bet * 5 * scatterCount;
    totalWin += scatterPay;
    winningLines.push({
      lineIndex: -1,
      symbols: Array(scatterCount).fill('scatter'),
      multiplier: 5,
      payout: scatterPay,
    });
  }

  const xpGained = Math.max(10, Math.floor(totalWin / 10));
  const jackpot = matchCount === 5 && firstSym === 'gorila_dourado';

  return { reels, winningLines, totalWin, xpGained, jackpot };
}

interface GameStoreState {
  balance: number;
  bet: number;
  minBet: number;
  maxBet: number;
  level: number;
  xp: number;
  xpToNextLevel: number;
  isSpinning: boolean;
  reels: string[][];
  lastResult: SpinResult | null;
  jackpotValue: number;
  showWinAnimation: boolean;
  showLevelUp: boolean;

  setBet: (bet: number) => void;
  increaseBet: () => void;
  decreaseBet: () => void;
  maxBetAction: () => void;
  spin: () => void;
  collect: () => void;
  setBalance: (balance: number) => void;
  setReels: (reels: string[][]) => void;
  setSpinning: (spinning: boolean) => void;
  applyResult: (result: SpinResult) => void;
  dismissWinAnimation: () => void;
  dismissLevelUp: () => void;
}

export const useGameStore = create<GameStoreState>((set, get) => ({
  balance: 1000,
  bet: 10,
  minBet: 1,
  maxBet: 500,
  level: 1,
  xp: 0,
  xpToNextLevel: 100,
  isSpinning: false,
  reels: generateRandomReels(),
  lastResult: null,
  jackpotValue: 25000,
  showWinAnimation: false,
  showLevelUp: false,

  setBet: (bet) => set({ bet: Math.max(get().minBet, Math.min(get().maxBet, bet)) }),
  increaseBet: () => {
    const { bet, maxBet } = get();
    const steps = [1, 2, 5, 10, 25, 50, 100, 250, 500];
    const next = steps.find((s) => s > bet) ?? maxBet;
    set({ bet: Math.min(next, maxBet) });
  },
  decreaseBet: () => {
    const { bet, minBet } = get();
    const steps = [1, 2, 5, 10, 25, 50, 100, 250, 500];
    const prev = [...steps].reverse().find((s) => s < bet) ?? minBet;
    set({ bet: Math.max(prev, minBet) });
  },
  maxBetAction: () => set({ bet: get().maxBet }),

  spin: () => {
    const { balance, bet, isSpinning } = get();
    if (isSpinning || balance < bet) return;

    set({ isSpinning: true, balance: balance - bet, lastResult: null, showWinAnimation: false });

    // Simulate spin delay, then resolve
    setTimeout(() => {
      const newReels = generateRandomReels();
      const result = checkWin(newReels, bet);

      const state = get();
      let newXp = state.xp + result.xpGained;
      let newLevel = state.level;
      let newXpToNext = state.xpToNextLevel;
      let leveledUp = false;

      while (newXp >= newXpToNext) {
        newXp -= newXpToNext;
        newLevel++;
        newXpToNext = Math.floor(newXpToNext * 1.5);
        leveledUp = true;
      }

      set({
        reels: newReels,
        isSpinning: false,
        lastResult: result,
        balance: state.balance + result.totalWin,
        xp: newXp,
        level: newLevel,
        xpToNextLevel: newXpToNext,
        showWinAnimation: result.totalWin > 0,
        showLevelUp: leveledUp,
      });
    }, 2800); // Total spin animation time
  },

  collect: () => {
    set({ showWinAnimation: false });
  },

  setBalance: (balance) => set({ balance }),
  setReels: (reels) => set({ reels }),
  setSpinning: (spinning) => set({ isSpinning: spinning }),

  applyResult: (result) => {
    set((state) => ({
      reels: result.reels,
      lastResult: result,
      balance: state.balance + result.totalWin,
      showWinAnimation: result.totalWin > 0,
    }));
  },

  dismissWinAnimation: () => set({ showWinAnimation: false }),
  dismissLevelUp: () => set({ showLevelUp: false }),
}));
