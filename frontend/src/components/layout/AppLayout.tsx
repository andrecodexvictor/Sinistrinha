import { Outlet } from 'react-router-dom';
import { useState } from 'react';
import Header from './Header';
import Sidebar from './Sidebar';
import WinsFeed from './WinsFeed';
import LoginModal from '../auth/LoginModal';

export default function AppLayout() {
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  // const [isRegisterOpen, setIsRegisterOpen] = useState(false);

  return (
    <div className="min-h-screen bg-brand-black flex flex-col text-white font-body selection:bg-brand-red selection:text-white">
      <WinsFeed />
      <Header onLoginClick={() => setIsLoginOpen(true)} onRegisterClick={() => {}} />
      
      <div className="flex flex-1 overflow-hidden">
        <Sidebar className="hidden md:flex" />
        
        <main className="flex-1 overflow-y-auto w-full">
          <Outlet />
        </main>
      </div>

      <LoginModal 
        isOpen={isLoginOpen} 
        onClose={() => setIsLoginOpen(false)} 
        onSwitchToRegister={() => {
          setIsLoginOpen(false);
        }} 
      />
      {/* <RegisterModal isOpen={isRegisterOpen} ... /> */}
    </div>
  );
}
