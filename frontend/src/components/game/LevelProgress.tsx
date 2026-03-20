import { memo } from 'react';
import { Trophy, ArrowUpCircle } from 'lucide-react';
import { useGameStore } from '../../store/gameStore';
import { LEVEL_PRIZES } from '../../types/game.types';

const LevelProgress = memo(() => {
  const { level, xp, xpToNextLevel } = useGameStore();

  const progressPercentage = Math.min(100, (xp / xpToNextLevel) * 100);
  
  // Find current tier prize
  const nextPrize = LEVEL_PRIZES.find(p => p.level > level) || LEVEL_PRIZES[LEVEL_PRIZES.length - 1];

  return (
    <div className="w-full flex flex-col md:flex-row items-center justify-between bg-black/50 border border-white/10 rounded-xl p-3 gap-4">
      
      {/* Level Display */}
      <div className="flex flex-col items-center justify-center shrink-0 w-20">
        <Trophy className="w-6 h-6 text-brand-gold mb-1 filter drop-shadow-[0_0_8px_rgba(255,215,0,0.8)]" />
        <span className="font-numbers font-black text-white text-xl">LVL {level}</span>
      </div>

      {/* Main XP Bar Container */}
      <div className="flex-1 w-full relative group">
        <div className="flex justify-between text-[10px] text-gray-400 font-bold mb-1.5 px-1 tracking-wider">
          <span>{xp} XP</span>
          <span>{xpToNextLevel} XP</span>
        </div>
        
        {/* Background Track */}
        <div className="w-full h-4 bg-[#111] rounded-full border border-white/10 overflow-hidden relative shadow-inner">
          {/* Animated Fill gradient */}
          <div 
            className="absolute top-0 left-0 h-full rounded-full transition-all duration-1000 ease-out bg-gradient-to-r from-yellow-600 via-brand-gold to-yellow-300 pattern-diagonal-lines pattern-black pattern-bg-transparent pattern-size-4 pattern-opacity-10"
            style={{ width: `${progressPercentage}%` }}
          >
            {/* Sparkle effect on the leading edge */}
            <div className="absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-l from-white/60 to-transparent"></div>
          </div>
        </div>
      </div>

      {/* Next Prize Preview */}
      <div className="flex items-center gap-3 shrink-0 bg-white/5 rounded-lg border border-white/10 p-2 group hover:bg-white/10 transition-colors cursor-help group/prize">
        <div className="relative">
          <div className="text-3xl filter drop-shadow-[0_0_8px_rgba(255,255,255,0.3)] group-hover/prize:scale-110 transition-transform">
            {nextPrize.icon}
          </div>
          {/* Level indicator for the prize */}
          <div className="absolute -bottom-2 -right-2 bg-brand-red text-white text-[9px] font-bold px-1 rounded-sm shadow border border-red-400">
            L{nextPrize.level}
          </div>
        </div>
        <div className="hidden md:flex flex-col align-start">
          <span className="text-[10px] font-bold text-brand-gold tracking-widest flex items-center gap-1">
            <ArrowUpCircle className="w-3 h-3" /> PRÓX. PRÊMIO
          </span>
          <span className="text-sm font-display2 text-gray-300 truncate max-w-[120px]">
            {nextPrize.name}
          </span>
        </div>
      </div>

    </div>
  );
});

LevelProgress.displayName = 'LevelProgress';
export default LevelProgress;
