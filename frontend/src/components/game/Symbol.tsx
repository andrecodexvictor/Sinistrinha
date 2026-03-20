import { memo } from 'react';
import { SYMBOLS } from '../../types/game.types';

interface SymbolProps {
  symbolKey: string;
  isWinning?: boolean;
}

const Symbol = memo(({ symbolKey, isWinning = false }: SymbolProps) => {
  const symbol = SYMBOLS[symbolKey];

  if (!symbol) return null;

  return (
    <div 
      className={`w-full h-full flex flex-col items-center justify-center p-2 transition-all duration-300 ${
        isWinning ? 'scale-110 z-10' : 'scale-100 z-0'
      }`}
    >
      <div 
        className={`w-full h-full flex items-center justify-center rounded-xl border-2 bg-[#151522] ${
          isWinning 
            ? 'border-brand-gold shadow-[0_0_20px_rgba(255,215,0,0.6)] animate-pulse' 
            : 'border-white/10 shadow-inner'
        }`}
      >
        <span 
          className="text-4xl md:text-5xl lg:text-6xl filter drop-shadow-md"
          role="img" 
          aria-label={symbol.name}
        >
          {symbol.icon}
        </span>
      </div>
    </div>
  );
});

Symbol.displayName = 'Symbol';
export default Symbol;
