// ========== Game Types ==========

export type SymbolRarity = 'comum' | 'incomum' | 'raro' | 'epico' | 'lendario' | 'especial';

export interface SlotSymbol {
  id: string;
  name: string;
  icon: string;
  color: string;
  rarity: SymbolRarity;
  multiplier: number;
}

export interface SpinResult {
  reels: string[][]; // 5 reels x 3 visible symbols each
  winningLines: WinLine[];
  totalWin: number;
  xpGained: number;
  newLevel?: number;
  jackpot: boolean;
}

export interface WinLine {
  lineIndex: number;
  symbols: string[];
  multiplier: number;
  payout: number;
}

export interface GameState {
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
}

// ========== Level Prize ==========

export interface LevelPrize {
  level: number;
  name: string;
  icon: string;
  description: string;
}

export const LEVEL_PRIZES: LevelPrize[] = [
  { level: 1,  name: 'Pendrive 32GB',       icon: '🔌', description: 'Armazenamento portátil' },
  { level: 5,  name: 'Mouse Gamer',         icon: '🖱️', description: 'Precisão extrema' },
  { level: 10, name: 'Teclado Mecânico',    icon: '⌨️', description: 'Switches Cherry MX' },
  { level: 15, name: 'RAM DDR5 16GB',       icon: '💾', description: 'Velocidade insana' },
  { level: 20, name: 'SSD NVMe 1TB',        icon: '💿', description: 'Boot em 3 segundos' },
  { level: 30, name: 'Monitor 4K 144Hz',    icon: '🖥️', description: 'Visual cinematográfico' },
  { level: 40, name: 'Processador i9',      icon: '🔲', description: 'Poder absoluto' },
  { level: 50, name: 'RTX 4090',            icon: '🎮', description: 'A placa definitiva' },
  { level: 99, name: 'PC Completo Gamer',   icon: '🦍', description: 'O prêmio do Gorila Dourado' },
];

// ========== Symbols Definition ==========

export const SYMBOLS: Record<string, SlotSymbol> = {
  pendrive:       { id: 'pendrive',       name: 'Pendrive',       icon: '🔌', color: '#9CA3AF', rarity: 'comum',    multiplier: 1 },
  mouse:          { id: 'mouse',          name: 'Mouse',          icon: '🖱️', color: '#C0C0C0', rarity: 'comum',    multiplier: 1.5 },
  teclado:        { id: 'teclado',        name: 'Teclado',        icon: '⌨️', color: '#C0C0C0', rarity: 'comum',    multiplier: 2 },
  ram:            { id: 'ram',            name: 'RAM DDR5',       icon: '💾', color: '#00FF88', rarity: 'incomum',  multiplier: 3 },
  ssd:            { id: 'ssd',            name: 'SSD NVMe',       icon: '💿', color: '#00AAFF', rarity: 'incomum',  multiplier: 4 },
  monitor:        { id: 'monitor',        name: 'Monitor 4K',     icon: '🖥️', color: '#0088FF', rarity: 'raro',     multiplier: 6 },
  cpu:            { id: 'cpu',            name: 'Processador i9', icon: '🔲', color: '#FF8800', rarity: 'raro',     multiplier: 8 },
  gpu_rtx:        { id: 'gpu_rtx',        name: 'RTX 4090',       icon: '🎮', color: '#76B900', rarity: 'epico',    multiplier: 15 },
  gorila_dourado: { id: 'gorila_dourado', name: 'Gorila Dourado', icon: '🦍', color: '#FFD700', rarity: 'lendario', multiplier: 50 },
  wild:           { id: 'wild',           name: 'Wild',           icon: '⚡', color: '#FFD700', rarity: 'especial', multiplier: 0 },
  scatter:        { id: 'scatter',        name: 'Scatter',        icon: '🍌', color: '#FFD700', rarity: 'especial', multiplier: 0 },
};

export const SYMBOL_KEYS = Object.keys(SYMBOLS);
