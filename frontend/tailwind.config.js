/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'brand-red': '#8B0000',
        'brand-gold': '#FFD700',
        'brand-black': '#0A0A0A',
        'brand-gray': '#1A1A2E',
      },
      fontFamily: {
        'display': ['"Black Ops One"', 'cursive'],
        'display2': ['"Russo One"', 'sans-serif'],
        'body': ['Rajdhani', 'sans-serif'],
        'numbers': ['Orbitron', 'sans-serif'],
      },
      animation: {
        'marquee': 'marquee 25s linear infinite',
        'pulse-glow': 'pulse-glow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 3s linear infinite',
      },
      keyframes: {
        marquee: {
          '0%': { transform: 'translateX(100%)' },
          '100%': { transform: 'translateX(-100%)' },
        },
        'pulse-glow': {
          '0%, 100%': { opacity: 1, filter: 'drop-shadow(0 0 10px rgba(255, 215, 0, 0.8))' },
          '50%': { opacity: .7, filter: 'drop-shadow(0 0 20px rgba(255, 215, 0, 1))' },
        }
      }
    },
  },
  plugins: [],
}
