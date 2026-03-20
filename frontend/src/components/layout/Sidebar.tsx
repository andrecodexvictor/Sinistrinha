import { Gamepad2, Trophy, Wallet, History, Settings } from 'lucide-react';
import { NavLink } from 'react-router-dom';

interface SidebarProps {
  className?: string;
}

const NAV_ITEMS = [
  { icon: Gamepad2, label: 'Cassino', path: '/' },
  { icon: Trophy, label: 'Ranking', path: '/leaderboard' },
  { icon: Wallet, label: 'Carteira', path: '/wallet' },
  { icon: History, label: 'Histórico', path: '/history' },
  { icon: Settings, label: 'Opções', path: '/settings' },
];

export default function Sidebar({ className = '' }: SidebarProps) {
  return (
    <aside className={`w-20 lg:w-64 bg-brand-gray/50 border-r border-white/5 flex flex-col pt-6 ${className}`}>
      <nav className="flex-1 flex flex-col gap-2 px-3">
        {NAV_ITEMS.map(({ icon: Icon, label, path }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) =>
              `flex items-center gap-4 px-3 py-3 rounded-lg transition-all duration-200 group ${
                isActive
                  ? 'bg-brand-red/20 text-brand-gold border border-brand-red/30 shadow-[inset_0_0_15px_rgba(139,0,0,0.5)]'
                  : 'text-gray-400 hover:bg-white/5 hover:text-white'
              }`
            }
          >
            <Icon className={`w-6 h-6 shrink-0 transition-transform group-hover:scale-110`} />
            <span className="hidden lg:block font-bold tracking-wide">{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Decorative footer area inside sidebar */}
      <div className="p-4 mt-auto border-t border-white/5 hidden lg:block">
        <div className="bg-black/40 rounded-lg p-4 border border-white/5 text-center">
          <p className="text-xs text-gray-500 mb-2 font-display2">MODO DEMO</p>
          <div className="flex justify-center gap-1 opacity-50">
            <span>🚀</span>
            <span>👾</span>
            <span>💎</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
