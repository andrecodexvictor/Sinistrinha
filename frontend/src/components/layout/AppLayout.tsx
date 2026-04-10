import { useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';
import WinsFeed from './WinsFeed';

export default function AppLayout() {
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-brand-black flex flex-col text-white font-body selection:bg-brand-red selection:text-white relative">
      <WinsFeed />
      <Header 
        onLoginClick={() => navigate('/login')} 
        onRegisterClick={() => navigate('/register')} 
        onMenuClick={() => setIsMobileMenuOpen(true)}
      />
      
      {/* Overlay escuro para mobile */}
      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/80 z-40 lg:hidden backdrop-blur-sm"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}
      
      <div className="flex flex-1 overflow-hidden relative">
        <Sidebar 
          isOpen={isMobileMenuOpen}
          onClose={() => setIsMobileMenuOpen(false)}
        />
        
        <main className="flex-1 overflow-y-auto w-full">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
