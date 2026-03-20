import SlotMachine from '../components/game/SlotMachine';
import BetControls from '../components/game/BetControls';
import LevelProgress from '../components/game/LevelProgress';

export default function GamePage() {
  return (
    <div className="w-full h-full p-4 lg:p-8 flex flex-col items-center justify-center relative overflow-hidden bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-[#1A1A2E] via-[#050510] to-[#0A0A0A]">
      
      {/* Background Grid Pattern */}
      <div 
        className="absolute inset-0 opacity-10 pointer-events-none" 
        style={{ backgroundImage: 'linear-gradient(#222 1px, transparent 1px), linear-gradient(90deg, #222 1px, transparent 1px)', backgroundSize: '40px 40px' }}
      ></div>

      <div className="relative z-10 w-full max-w-5xl flex flex-col items-center gap-8">
        {/* Top Header Section: Jackpot & Ticker */}
        <div className="text-center">
          <h2 className="text-gray-400 font-display2 tracking-[0.2em] text-sm md:text-md mb-2">MEGA ACUMULADO</h2>
          <div className="text-5xl md:text-7xl font-numbers font-black gold-gradient-text animate-pulse-glow drop-shadow-2xl">
            R$ 25.480,90
          </div>
        </div>

        {/* Slot Machine Main Container Area */}
        <div className="w-full aspect-[16/9] md:aspect-[21/9] max-h-[500px] bg-black border-2 border-dashed border-transparent rounded-xl flex items-center justify-center">
           <SlotMachine />
        </div>

        {/* Level Progress Area */}
        <div className="w-full max-w-4xl pt-2">
          <LevelProgress />
        </div>

        {/* Bet Controls Area */}
        <div className="w-full flex justify-center">
          <BetControls />
        </div>

      </div>
    </div>
  );
}
