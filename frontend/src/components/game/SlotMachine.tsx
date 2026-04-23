import { useGameStore } from '../../store/gameStore';
import Reel from './Reel';

export default function SlotMachine() {
  const { reels, isSpinning, lastResult } = useGameStore();

  // Highlight winning symbols. We need to pass down which row index won per reel.
  const getWinningIndicesForReel = (): number[] => {
    if (isSpinning || !lastResult) return [];
    
    const indices: number[] = [];
    
    if (lastResult.totalWin > 0) {
      // In this version, we're only simulating Center Line wins (index 1)
      indices.push(1);
    }

    return indices;
  };

  return (
    <div className="relative w-full h-full max-h-[500px] slot-machine-casing p-2 md:p-4 perspective-1000">
      
      {/* Decorative Outer Frame Elements */}
      <div className="absolute -top-3 left-1/2 -translate-x-1/2 w-32 h-6 bg-brand-gold rounded-b-xl border-x-4 border-b-4 border-yellow-700 flex items-center justify-center shadow-[0_5px_15px_rgba(255,215,0,0.5)] z-20">
        <span className="text-[10px] font-black tracking-widest text-black">PAYLINE</span>
      </div>
      
      {/* Main Reels Container */}
      <div className="w-full h-full bg-[#0a0a0a] rounded-lg border-2 border-white/10 shadow-inner overflow-hidden flex relative">
        
        {/* Payline Indicator (Center Line visible overlay) */}
        {!isSpinning && (
          <div className="absolute top-1/2 -translate-y-1/2 left-0 w-full h-1/3 border-y-2 border-brand-red/30 bg-brand-red/5 pointer-events-none z-10 flex items-center">
             <div className="w-full h-[1px] bg-brand-red/50 shadow-[0_0_8px_rgba(139,0,0,0.8)]"></div>
          </div>
        )}

        {/* 5 Reels Render */}
        {reels.map((reelSymbols, idx) => (
          <div key={`reel-col-${idx}`} className="flex-1 h-full relative">
            <Reel 
              index={idx} 
              isSpinning={isSpinning} 
              finalSymbols={reelSymbols} 
              winningIndices={getWinningIndicesForReel()}
            />
          </div>
        ))}

        {/* Inner Glass Reflection */}
        <div className="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent pointer-events-none z-30 rounded-lg"></div>
      </div>
    </div>
  );
}
