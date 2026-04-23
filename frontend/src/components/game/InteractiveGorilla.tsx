import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGameStore } from '../../store/gameStore';

// Importe o seu vídeo (ajuste o caminho se necessário)
import gorillaVideo from '../../assets/Vídeo_de_Dança_Gerado.mp4'; 

export default function InteractiveGorilla() {
  const { isSpinning, showWinAnimation, lastResult } = useGameStore();
  const [isHovered, setIsHovered] = useState(false);
  const [clickCount, setClickCount] = useState(0);
  const [showTooltip, setShowTooltip] = useState(false);
  
  // Referência para controlar o elemento de vídeo
  const videoRef = useRef<HTMLVideoElement>(null);

  // Lógica para determinar o estado atual e fazer efeitos
  let currentState = 'idle';
  if (isSpinning) currentState = 'spinning';
  else if (showWinAnimation) {
    if (lastResult?.jackpot) currentState = 'jackpot';
    else currentState = 'win';
  } else if (isHovered) currentState = 'hover';

  // Podemos alterar a velocidade do vídeo baseado no estado do jogo!
  useEffect(() => {
    if (videoRef.current) {
      if (isSpinning) {
        videoRef.current.playbackRate = 1.5; // Fica mais rápido e ansioso
      } else if (showWinAnimation) {
        videoRef.current.playbackRate = 2.0; // Fica muito animado quando ganha
      } else {
        videoRef.current.playbackRate = 1.0; // Velocidade normal
      }
    }
  }, [isSpinning, showWinAnimation]);

  const animations = {
    idle: { scale: 1, y: 0 },
    hover: { scale: 1.1, y: -5, transition: { duration: 0.3 } },
    spinning: { y: [0, -5, 0], transition: { duration: 0.5, repeat: Infinity } },
    win: { scale: 1.2, y: -15, transition: { duration: 0.5 } },
    jackpot: { scale: 1.3, y: -20, transition: { duration: 0.8 } }
  };

  const handleGorillaClick = () => {
    setClickCount(prev => prev + 1);
    setShowTooltip(true);
    setTimeout(() => setShowTooltip(false), 3000);
  };

  const getGorillaQuote = () => {
    if (showWinAnimation) return "ISSO AÍ! GANHAMOS!";
    if (clickCount % 4 === 0) return "Aperta logo esse botão de SPIN!";
    if (clickCount % 3 === 0) return "A sorte está com a gente hoje!";
    if (clickCount % 2 === 0) return "Bora multiplicar esse saldo!";
    return "Uhh ah ah! Bora jogar!";
  };

  return (
    <motion.div 
      className="relative z-50 cursor-pointer flex justify-center mt-4 mb-2"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleGorillaClick}
      animate={animations[currentState as keyof typeof animations]}
    >
      <div className="relative">
        <div className={`absolute inset-0 bg-brand-gold rounded-full blur-2xl transition-opacity duration-300 -z-10 ${isHovered || showWinAnimation ? 'opacity-40' : 'opacity-0'}`} />
        
        {/* Aqui usamos a tag <video> ao invés de <img> */}
        <video 
          ref={videoRef}
          src={gorillaVideo} 
          autoPlay 
          loop 
          muted 
          playsInline
          className="w-32 h-32 md:w-48 md:h-48 object-cover rounded-full mix-blend-screen drop-shadow-[0_0_15px_rgba(255,215,0,0.3)]"
          style={{
            // Um truque para remover o fundo preto do vídeo caso ele não tenha canal alpha (fundo transparente)
            // maskImage pode ser usado se o vídeo for muito quadrado, ou o mix-blend-screen acima ajuda com fundos pretos puros.
          }}
        />
        
        <AnimatePresence>
          {showTooltip && (
            <motion.div 
              initial={{ opacity: 0, y: 10, scale: 0.8 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className="absolute -top-16 -right-20 bg-brand-gray border-2 border-brand-gold text-xs text-white p-3 rounded-2xl rounded-bl-none shadow-2xl w-40 font-body z-50"
            >
              <p className="font-bold text-center">"{getGorillaQuote()}"</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}