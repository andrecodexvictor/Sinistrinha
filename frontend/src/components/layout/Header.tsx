import { useAuthStore } from '../../store/authStore';
import { useGameStore } from '../../store/gameStore';
import { Wallet, Trophy, User, Menu } from 'lucide-react'; // <- Import do Menu adicionado
import { Link } from 'react-router-dom';

import logoImg from '../../assets/logo.png';

interface HeaderProps {
  onLoginClick: () => void;
  onRegisterClick: () => void;
  onMenuClick?: () => void; // <- Propriedade adicionada
}

export default function Header({ onLoginClick, onRegisterClick, onMenuClick }: HeaderProps) {
  const { isAuthenticated, user, logout } = useAuthStore();
  const { balance, level } = useGameStore();

  return (
    <header className="sticky top-0 z-40 w-full h-16 bg-brand-gray/95 backdrop-blur-md border-b border-white/5 flex items-center justify-between px-4 lg:px-6 shadow-xl">
      <div className="flex items-center gap-3">
        {/* Botão Hambúrguer (Apenas Mobile) */}
        <button 
          onClick={onMenuClick}
          className="lg:hidden p-1.5 -ml-2 text-gray-400 hover:text-white rounded-md hover:bg-white/10 transition-colors"
        >
          <Menu className="w-6 h-6" />
        </button>

        <Link to="/" className="flex items-center gap-2 group">
          <img
            src={logoImg}
            alt="Logo Sinistrinha"
            className="w-10 h-10 object-contain drop-shadow-[0_0_15px_rgba(139,0,0,0.6)] group-hover:drop-shadow-[0_0_25px_rgba(139,0,0,0.9)] transition-all"
          />
          <span className="font-display tracking-wider text-xl lg:text-2xl text-white group-hover:text-glow-gold transition-all duration-300">
            SINISTRINHA
          </span>
        </Link>
      </div>

      <div className="flex items-center gap-4">
        {isAuthenticated ? (
          <>
            {/* Level Badge */}
            <div className="hidden md:flex items-center bg-black/40 px-3 py-1.5 rounded-full border border-brand-gold/30">
              <Trophy className="w-4 h-4 text-brand-gold mr-2" />
              <span className="font-numbers text-brand-gold font-bold">LVL {level}</span>
            </div>

            {/* Balance Display */}
            <div className="flex items-center bg-black/60 px-4 py-1.5 rounded-full border border-white/10 shadow-inner">
              <span className="text-gray-400 text-xs mr-2 font-medium">SALDO</span>
              <span className="font-numbers text-green-400 font-bold tracking-wide">
                R$ {balance.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
              </span>
            </div>

            {/* Deposit Button */}
            <button className="hidden sm:flex items-center justify-center bg-gradient-to-r from-brand-red to-red-600 hover:from-red-500 hover:to-red-400 text-white px-4 py-1.5 rounded-md font-bold text-sm tracking-wide shadow-[0_0_10px_rgba(139,0,0,0.5)] hover:shadow-[0_0_20px_rgba(255,0,0,0.6)] transition-all">
              <Wallet className="w-4 h-4 mr-2" />
              DEPOSITAR
            </button>

            {/* User Profile */}
            <div className="relative group flex items-center gap-2 cursor-pointer ml-2">
              <div className="w-9 h-9 bg-brand-gray border border-brand-gold/50 rounded-full flex items-center justify-center overflow-hidden">
                {user?.avatarUrl ? (
                  <img src={user.avatarUrl} alt="Avatar" className="w-full h-full object-cover" />
                ) : (
                  <User className="w-5 h-5 text-brand-gold/70" />
                )}
              </div>

              <div className="absolute right-0 top-full mt-2 w-48 bg-brand-gray border border-white/10 rounded-lg shadow-2xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all pointer-events-none group-hover:pointer-events-auto">
                <div className="p-3 border-b border-white/10">
                  <p className="font-bold text-sm">{user?.username}</p>
                  <p className="text-xs text-gray-400 truncate">{user?.email}</p>
                </div>
                <div className="p-2">
                  <button className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-white/5 hover:text-white rounded transition-colors">
                    Perfil
                  </button>
                  <button className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-white/5 hover:text-white rounded transition-colors">
                    Histórico
                  </button>
                  <button
                    onClick={logout}
                    className="w-full text-left px-3 py-2 text-sm text-red-400 hover:bg-red-500/10 hover:text-red-300 rounded transition-colors"
                  >
                    Sair
                  </button>
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="flex gap-2">
            <button
              onClick={onLoginClick}
              className="px-4 py-1.5 rounded text-sm font-bold text-gray-300 hover:text-white hover:bg-white/5 transition-colors"
            >
              ENTRAR
            </button>
            <button
              onClick={onRegisterClick}
              className="bg-brand-red hover:bg-red-700 text-white px-4 py-1.5 rounded text-sm font-bold shadow-[0_0_10px_rgba(139,0,0,0.4)] transition-colors"
            >
              REGISTRAR
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
