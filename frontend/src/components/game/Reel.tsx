import { useEffect, useState, useRef } from 'react';
import { motion, useAnimation } from 'framer-motion';
import Symbol from './Symbol';
import { SYMBOL_KEYS } from '../../types/game.types';

interface ReelProps {
  index: number;
  isSpinning: boolean;
  finalSymbols: string[];
  winningIndices: number[]; // e.g. [1] if center row won
}

const TOTAL_EXTRA_SPINS = 20; // How many symbols to spin through before stopping

export default function Reel({ index, isSpinning, finalSymbols, winningIndices }: ReelProps) {
  const controls = useAnimation();
  const [strip, setStrip] = useState<string[]>([]);
  const isFirstRender = useRef(true);

  // Initialize strip or build the "spinning" strip
  useEffect(() => {
    if (isFirstRender.current) {
      // First render: Show the initial 3 symbols
      setStrip(finalSymbols);
      isFirstRender.current = false;
      return;
    }

    if (isSpinning) {
      // Create a long strip of random symbols + the target final 3 at the top
      const randomFiller = Array.from({ length: TOTAL_EXTRA_SPINS }, () => 
        SYMBOL_KEYS[Math.floor(Math.random() * SYMBOL_KEYS.length)]
      );
      
      // The Framer Motion animation pulls the strip DOWNWARDS.
      // So the layout from bottom to top needs to be [Current View] -> [Random] -> [Final View]
      // To loop seamlessly, we'll construct the array accordingly.
      
      setStrip([...finalSymbols, ...randomFiller, ...strip.slice(0, 3)]);

      // Start the spin animation with staggered delay based on reel index
      controls.set({ y: `-${(TOTAL_EXTRA_SPINS + 3) * 33.33}%` }); // Start near the bottom of strip
      
      controls.start({
        y: '0%', // End showing the top 3 elements (finalSymbols)
        transition: {
          duration: 2.0 + (index * 0.2), // Staggered stop (left to right)
          ease: [0.17, 0.67, 0.83, 0.67], // smooth deceleration
          delay: index * 0.1, // Staggered start
        }
      });
    }
  }, [isSpinning, finalSymbols, index, controls]);

  return (
    <div className="relative w-full h-full overflow-hidden border-r border-[#ffffff10] last:border-r-0 bg-[#0a0a0f]">
      {/* Inner shadow overlay for depth */}
      <div className="absolute inset-0 inner-glow z-20 pointer-events-none rounded-sm"></div>

      <motion.div
        className="absolute top-0 left-0 w-full flex flex-col-reverse" 
        style={{ height: `${(strip.length / 3) * 100}%` }}
        animate={controls}
      >
        {strip.map((symbolKey, idx) => {
          // Determine if this symbol is part of a win.
          // Since final symbols are at idx 0, 1, 2 of the top of the flex-col-reverse list
          const isWinning = !isSpinning && idx < 3 && winningIndices.includes(idx);
          
          return (
            <div 
              key={`${index}-${idx}-${symbolKey}`} 
              className="w-full flex-grow flex items-center justify-center p-1 md:p-2"
              style={{ height: `${100 / strip.length}%` }} 
            >
              <Symbol symbolKey={symbolKey} isWinning={isWinning} />
            </div>
          );
        })}
      </motion.div>
    </div>
  );
}
