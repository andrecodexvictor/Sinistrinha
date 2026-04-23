import { useState, useEffect } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';
import WinsFeed from './WinsFeed';
import { useAuthStore } from '../../store/authStore';

export default function AppLayout() {
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { isAuthenticated, isLoading, restoreSession } = useAuthStore();

  useEffect(() => {
    restoreSession();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);



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
