import { useCasinoStore } from '../../store/casinoStore';
import { useEffect } from 'react';
import type { WinFeedItem } from '../../types/api.types';

export default function WinsFeed() {
  const { winsFeed, generateFakeWins } = useCasinoStore();

  // Generate fake simulated wins dynamically
  useEffect(() => {
    const interval = setInterval(() => {
      generateFakeWins(1); // Add 1 new win every 5s
    }, 5000);
    return () => clearInterval(interval);
  }, [generateFakeWins]);

  return (
    <div className="w-full bg-black border-b border-brand-gold/40 h-8 flex items-center overflow-hidden relative shadow-[0_2px_15px_rgba(0,0,0,0.8)] z-50">
      
      {/* Decorative gradient overlay ends to blend marquee */}
      <div className="absolute left-0 top-0 bottom-0 w-8 md:w-16 bg-gradient-to-r from-black to-transparent z-10 pointer-events-none" />
      <div className="absolute right-0 top-0 bottom-0 w-8 md:w-16 bg-gradient-to-l from-black to-transparent z-10 pointer-events-none" />

      {/* Marquee Animation Container */}
      <div className="flex whitespace-nowrap animate-marquee hover:[animation-play-state:paused] w-[200%] sm:w-[150%] md:w-[100%]">
        <div className="flex items-center gap-8 px-4">
          {winsFeed.map((win: WinFeedItem, idx: number) => {
            
            // Color logic based on rules
            let textColor = 'text-gray-400';
            let shadowClass = '';
            
            if (win.amount >= 1000) {
              textColor = 'text-brand-gold font-bold';
              shadowClass = 'animate-pulse-glow';
            } else if (win.amount >= 500) {
              textColor = 'text-blue-400 font-bold';
            } else if (win.amount >= 100) {
              textColor = 'text-green-500';
            }

            return (
              <div 
                key={`${win.id}-${idx}`} 
                className={`flex items-center gap-2 text-xs md:text-sm cursor-pointer hover:bg-white/5 px-2 rounded transition-colors ${shadowClass}`}
              >
                <span className="opacity-80">🦍</span>
                <span className="font-bold text-gray-200">{win.username}</span>
                <span className="text-gray-500 mx-1">ganhou</span>
                <span className={`${textColor}`}>
                  R$ {win.amount.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </span>
                <span className="text-gray-500 mx-1">em</span>
                <div className="flex items-center bg-white/10 px-1.5 py-0.5 rounded border border-white/5">
                  <span className="mr-1">{win.symbolIcon}</span>
                  <span className="font-bold text-white/90 font-display2 text-[10px] tracking-wider uppercase">
                    {win.symbolName}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
