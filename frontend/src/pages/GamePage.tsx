import SlotMachine from '../components/game/SlotMachine';
import BetControls from '../components/game/BetControls';
import LevelProgress from '../components/game/LevelProgress';

// 1. Salve a imagem do Freepik na pasta assets e importe aqui:
import bgCassino from '../assets/bg-gif.gif'; 
import InteractiveGorilla from '../components/game/InteractiveGorilla';

export default function GamePage() {
  return (
    <div 
      className="w-full min-h-full p-4 lg:p-8 flex flex-col items-center justify-center relative overflow-hidden bg-[#050508] bg-cover bg-center"
      style={{ backgroundImage: `url(${bgCassino})` }}
    >
      {/* Overlay Escuro com Blur */}
      <div className="absolute inset-0 bg-[#0B0B0F]/90 backdrop-blur-sm pointer-events-none" />

      {/* Container Principal:
          - No mobile/padrão: flex-col (vertical)
          - Em telas 16:9: flex-row-reverse (horizontal, inverte ordem dos grupos)
          - max-w-7xl para dar mais espaço lateral no modo 16:9
      */}
      <div className="relative z-10 w-full max-w-5xl [@media(min-aspect-ratio:16/9)]:max-w-7xl flex flex-col [@media(min-aspect-ratio:16/9)]:flex-row-reverse items-center justify-center gap-8 lg:gap-16">
        
        {/* LADO DIREITO (16:9) / TOPO (OUTROS): Jackpot & Gorila */}
        <div className="flex flex-col items-center gap-6 [@media(min-aspect-ratio:16/9)]:w-1/3">
          <div className="text-center">
            <h2 className="text-gray-400 font-display2 tracking-[0.2em] text-sm md:text-md mb-2 uppercase">Mega Acumulado</h2>
            <div className="text-4xl md:text-5xl lg:text-6xl font-numbers font-black gold-gradient-text animate-pulse-glow drop-shadow-2xl">
              R$ 25.480,90
            </div>
          </div>
          
          <div className="w-full flex justify-center">
            <InteractiveGorilla />
          </div>
        </div>

        {/* LADO ESQUERDO (16:9) / BAIXO (OUTROS): Slot, Level & Controls */}
        <div className="w-full [@media(min-aspect-ratio:16/9)]:w-2/3 flex flex-col items-center gap-8">
          
          {/* Container da Slot Machine */}
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
    </div>
  );
}
