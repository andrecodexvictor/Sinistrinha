import { useGameStore } from '../../store/gameStore';
import { Coins, Minus, Plus, Maximize, CheckCircle2 } from 'lucide-react';

export default function BetControls() {
  const { 
    bet, minBet, maxBet, balance, isSpinning, 
    increaseBet, decreaseBet, maxBetAction, spin, 
    showWinAnimation, lastResult, collect 
  } = useGameStore();

  const canSpin = !isSpinning && balance >= bet;

  return (
    <div className="w-full max-w-5xl bg-brand-gray border border-white/10 rounded-2xl p-4 md:p-6 shadow-2xl flex flex-col md:flex-row items-center justify-between gap-6 relative z-10">
      
      {/* Balance Block */}
      <div className="flex flex-col items-center md:items-start p-3 bg-black/40 rounded-xl border border-white/5 w-full md:w-48 shrink-0">
        <span className="text-gray-400 text-xs font-bold tracking-wider mb-1 flex items-center">
          <Coins className="w-3 h-3 mr-1 text-green-500" />
          SALDO
        </span>
        <span className="font-numbers text-xl md:text-2xl text-white">
          R$ {balance.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
        </span>
      </div>

      {/* Center Controls: Bet Size */}
      <div className="flex-1 flex flex-col items-center justify-center gap-2 w-full">
        <span className="text-gray-400 text-xs font-bold tracking-wider">VALOR DA APOSTA</span>
        
        <div className="flex items-center gap-2 bg-black/60 p-1.5 rounded-xl border border-white/10 shadow-inner">
          <button 
            onClick={decreaseBet}
            disabled={isSpinning || bet <= minBet}
            className="w-10 h-10 md:w-12 md:h-12 flex items-center justify-center rounded-lg bg-white/5 hover:bg-white/10 text-white disabled:opacity-30 transition-colors"
          >
            <Minus className="w-5 h-5" />
          </button>

          <div className="w-24 md:w-32 text-center font-numbers text-xl md:text-2xl text-brand-gold font-bold">
            R$ {bet}
          </div>

          <button 
            onClick={increaseBet}
            disabled={isSpinning || bet >= maxBet}
            className="w-10 h-10 md:w-12 md:h-12 flex items-center justify-center rounded-lg bg-white/5 hover:bg-white/10 text-white disabled:opacity-30 transition-colors"
          >
            <Plus className="w-5 h-5" />
          </button>
          
          <button 
            onClick={maxBetAction}
            disabled={isSpinning || bet >= maxBet}
            className="hidden md:flex flex-col items-center justify-center w-12 h-12 rounded-lg bg-white/5 hover:bg-white/10 text-brand-gold border border-brand-gold/30 disabled:opacity-30 transition-all font-display2 text-[10px]"
          >
            <Maximize className="w-4 h-4 mb-0.5" />
            MAX
          </button>
        </div>
      </div>

      {/* Main Action Area */}
      <div className="w-full md:w-auto shrink-0 flex items-center justify-center">
        {showWinAnimation ? (
          <button 
            onClick={collect}
            className="group relative w-full md:w-48 h-16 md:h-20 rounded-xl overflow-hidden shadow-[0_0_20px_rgba(255,215,0,0.4)] transition-all hover:scale-105"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-yellow-600 via-brand-gold to-yellow-500 hover:brightness-110 transition-all"></div>
            <div className="absolute inset-0 flex flex-col items-center justify-center text-black">
              <span className="font-display2 text-xs opacity-70 mb-0.5">GANHO!</span>
              <span className="font-numbers text-xl md:text-2xl font-black">
                R$ {lastResult?.totalWin.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
              </span>
              <div className="absolute inset-x-0 bottom-1 flex justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                <span className="text-[10px] font-bold flex items-center gap-1"><CheckCircle2 className="w-3 h-3"/> COLETAR</span>
              </div>
            </div>
          </button>
        ) : (
          <button 
            onClick={spin}
            disabled={!canSpin}
            className="group relative w-full md:w-48 h-16 md:h-20 rounded-xl overflow-hidden shadow-[0_0_30px_rgba(139,0,0,0.6)] disabled:opacity-50 disabled:shadow-none disabled:cursor-not-allowed transition-all hover:scale-105 active:scale-95"
          >
             {/* Red Glow Spin Button */}
            <div className="absolute inset-0 bg-gradient-to-t from-red-900 via-brand-red to-red-600 group-hover:brightness-110"></div>
            
            {/* Inner top highlight */}
            <div className="absolute top-0 inset-x-0 h-1/2 bg-gradient-to-b from-white/20 to-transparent"></div>
            
            <div className="absolute inset-0 flex items-center justify-center gap-3">
              <span className="text-3xl filter group-hover:drop-shadow-[0_0_8px_rgba(255,255,255,0.8)] transition-all delay-75">🦍</span>
              <span className="font-display tracking-[0.1em] text-3xl text-white drop-shadow-[0_2px_4px_rgba(0,0,0,0.5)]">SPIN</span>
            </div>
            
            {/* Pulsing ring */}
            <div className={`absolute inset-0 rounded-xl border border-white/40 ${!isSpinning && 'animate-pulse'}`}></div>
          </button>
        )}
      </div>

    </div>
  );
}
