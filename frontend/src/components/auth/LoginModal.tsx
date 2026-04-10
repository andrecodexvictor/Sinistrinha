import { useState } from 'react';
import { useForm as useRHForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import Modal from '../ui/Modal';
import { Loader2 } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

const loginSchema = z.object({
  email: z.string().min(1, 'Email é obrigatório'),
  password: z.string().min(6, 'Senha deve ter no mínimo 6 caracteres'),
});

type LoginForm = z.infer<typeof loginSchema>;

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSwitchToRegister: () => void;
}

export default function LoginModal({ isOpen, onClose, onSwitchToRegister }: LoginModalProps) {
  const [error, setError] = useState<string | null>(null);
  const { login, setLoading, isLoading } = useAuthStore();
  
  const { register, handleSubmit, formState: { errors }, reset } = useRHForm<LoginForm>({
    resolver: zodResolver(loginSchema)
  });

  const onSubmit = async (data: LoginForm) => {
    setError(null);
    setLoading(true);
    
    // TODO: Connect to Django API
    // Simulating API call for now
    setTimeout(() => {
      if (data.email === 'demo' && data.password === '123456') {
        login(
          { id: '1', username: 'DemoPlayer', email: 'demo@demo.com', level: 1, xp: 0, balance: 1000, createdAt: new Date().toISOString() },
          { access: 'fake-token', refresh: 'fake-refresh' }
        );
        reset();
        onClose();
      } else {
        setError('Credenciais inválidas. Tente: demo / 123456');
      }
      setLoading(false);
    }, 1500);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="ACESSO RESTRITO">
      
      {error && (
        <div className="bg-red-500/10 border border-brand-red/50 text-brand-red px-4 py-3 rounded mb-6 text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="block text-xs font-bold text-gray-400 mb-1">EMAIL OU USUÁRIO</label>
          <input 
            {...register('email')}
            className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-gray-600 focus:outline-none focus:border-brand-gold/50 focus:ring-1 focus:ring-brand-gold/50 transition-all font-mono text-sm"
            placeholder="hacker@cassino.com"
          />
          {errors.email && <p className="text-brand-red text-xs mt-1">{errors.email.message}</p>}
        </div>

        <div>
          <label className="block text-xs font-bold text-gray-400 mb-1">SENHA</label>
          <input 
            {...register('password')}
            type="password"
            className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-gray-600 focus:outline-none focus:border-brand-gold/50 focus:ring-1 focus:ring-brand-gold/50 transition-all font-mono text-sm"
            placeholder="••••••••"
          />
          {errors.password && <p className="text-brand-red text-xs mt-1">{errors.password.message}</p>}
        </div>

        <button 
          type="submit" 
          disabled={isLoading}
          className="w-full bg-brand-red hover:bg-red-700 text-white font-bold py-3 px-4 rounded-lg shadow-[0_0_15px_rgba(139,0,0,0.4)] hover:shadow-[0_0_25px_rgba(139,0,0,0.6)] transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'CONECTAR'}
        </button>
      </form>

      <div className="mt-6 text-center text-sm text-gray-400 border-t border-white/5 pt-4">
        Não tem uma conta?{' '}
        <button onClick={onSwitchToRegister} className="text-brand-gold hover:text-yellow-400 font-bold underline decoration-brand-gold/30 underline-offset-4">
          Crie uma ágora
        </button>
      </div>
    </Modal>
  );
}
