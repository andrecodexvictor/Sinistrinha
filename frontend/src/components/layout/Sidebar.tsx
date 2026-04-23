import { Gamepad2, Trophy, Wallet, History, Settings, X } from 'lucide-react'; // <- Import do X adicionado
import { NavLink } from 'react-router-dom';

interface SidebarProps {
  className?: string;
  isOpen?: boolean;     // <- Adicionado
  onClose?: () => void; // <- Adicionado
}

const NAV_ITEMS = [
  { icon: Gamepad2, label: 'Cassino', path: '/' },
  { icon: Trophy, label: 'Ranking', path: '/ranking' },
  { icon: Wallet, label: 'Carteira', path: '/wallet' },
  { icon: History, label: 'Histórico', path: '/history' },
  { icon: Settings, label: 'Opções', path: '/settings' },
];

export default function Sidebar({ className = '', isOpen = false, onClose }: SidebarProps) {
  return (
    <aside 
      className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-brand-gray border-r border-white/5 flex flex-col pt-6 
        transition-transform duration-300 ease-in-out shadow-2xl
        lg:relative lg:translate-x-0 lg:w-20 lg:bg-brand-gray/50 lg:shadow-none xl:w-64
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        ${className}
      `}
    >
      {/* Header Mobile com botão Fechar */}
      <div className="flex items-center justify-between px-6 mb-6 lg:hidden">
        <span className="font-bold text-xl text-brand-gold">Menu</span>
        <button onClick={onClose} className="p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors">
          <X className="w-6 h-6" />
        </button>
      </div>

      <nav className="flex-1 flex flex-col gap-2 px-3">
        {NAV_ITEMS.map(({ icon: Icon, label, path }) => (
          <NavLink
            key={path}
            to={path}
            onClick={onClose} // <- Fecha a gaveta no mobile ao clicar
            className={({ isActive }) =>
              `flex items-center gap-4 px-3 py-3 rounded-lg transition-all duration-200 group ${
                isActive
                  ? 'bg-brand-red/20 text-brand-gold border border-brand-red/30 shadow-[inset_0_0_15px_rgba(139,0,0,0.5)]'
                  : 'text-gray-400 hover:bg-white/5 hover:text-white'
              }`
            }
          >
            <Icon className={`w-6 h-6 shrink-0 transition-transform group-hover:scale-110`} />
            <span className="block xl:block font-bold tracking-wide lg:hidden">{label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
