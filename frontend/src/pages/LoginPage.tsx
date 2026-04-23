import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm as useRHForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Loader2 } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { motion } from 'framer-motion';

import logoImg from '../assets/logo.png';

const loginSchema = z.object({
    username: z.string().min(1, 'Usuário é obrigatório'),
    password: z.string().min(6, 'Senha deve ter no mínimo 6 caracteres'),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
    const navigate = useNavigate();
    const { loginAsync, isLoading, error } = useAuthStore();
    const [localError, setLocalError] = useState<string | null>(null);

    const { register, handleSubmit, formState: { errors } } = useRHForm<LoginForm>({
        resolver: zodResolver(loginSchema)
    });

    const onSubmit = async (data: LoginForm) => {
        setLocalError(null);
        const success = await loginAsync(data.username, data.password);
        if (success) {
            navigate('/');
        } else {
            setLocalError(useAuthStore.getState().error);
        }
    };

    const displayError = localError || error;

    return (
        <div className="min-h-screen bg-[#050508] bg-[url('https://images.unsplash.com/photo-1596838132731-3301c3fd4317?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center flex items-center justify-center p-6 relative overflow-hidden">
            <div className="absolute inset-0 bg-[#0B0B0F]/90 backdrop-blur-sm" />

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="relative z-10 w-full max-w-md bg-brand-gray/95 border-2 border-brand-red/40 rounded-3xl shadow-[0_0_80px_rgba(139,0,0,0.15)] overflow-hidden backdrop-blur-sm"
            >
                <div className="p-8 md:p-10 flex flex-col items-center">
                    <div className="mb-6 flex justify-center items-center">
                        <Link to="/" className="inline-block cursor-pointer">
                            <img
                                src= {logoImg}
                                alt="Logo do Jogo"
                                className="w-32 mx-auto mb-6"
                            />
                        </Link>
                    </div>

                    <h1 className="text-2xl md:text-3xl font-bold text-center font-display2 text-brand-gold mb-2 tracking-wider">
                        SINISTRINHA
                    </h1>

                    <p className="text-xs text-gray-400 mb-8 font-body">CASSINO</p>

                    {displayError && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="w-full bg-red-500/10 border border-brand-red/50 text-brand-red px-4 py-3 rounded mb-6 text-sm font-body"
                        >
                            {displayError}
                        </motion.div>
                    )}

                    <form onSubmit={handleSubmit(onSubmit)} className="w-full space-y-5">
                        <div>
                            <label className="block text-xs font-bold text-gray-400 mb-2 font-display2">USUÁRIO</label>
                            <input
                                {...register('username')}
                                className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-600 focus:outline-none focus:border-brand-gold/50 focus:ring-1 focus:ring-brand-gold/50 transition-all font-body text-sm"
                                placeholder="seu_usuario"
                            />
                            {errors.username && <p className="text-brand-red text-xs mt-1 font-body">{errors.username.message}</p>}
                        </div>

                        <div>
                            <label className="block text-xs font-bold text-gray-400 mb-2 font-display2">SENHA</label>
                            <input
                                {...register('password')}
                                type="password"
                                className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-600 focus:outline-none focus:border-brand-gold/50 focus:ring-1 focus:ring-brand-gold/50 transition-all font-body text-sm"
                                placeholder="••••••••"
                            />
                            {errors.password && <p className="text-brand-red text-xs mt-1 font-body">{errors.password.message}</p>}
                        </div>

                        <motion.button
                            type="submit"
                            disabled={isLoading}
                            whileHover={{ scale: isLoading ? 1 : 1.02 }}
                            whileTap={{ scale: isLoading ? 1 : 0.98 }}
                            className="w-full bg-brand-red hover:bg-red-700 text-white font-bold py-3 px-4 rounded-lg shadow-[0_0_15px_rgba(139,0,0,0.4)] hover:shadow-[0_0_25px_rgba(139,0,0,0.6)] transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed font-display2 tracking-wider"
                        >
                            {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'CONECTAR'}
                        </motion.button>

                        <motion.button
                            type="button"
                            onClick={() => navigate('/register')}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            className="w-full bg-transparent border border-brand-gold/30 hover:border-brand-gold/60 text-brand-gold hover:text-yellow-300 font-bold py-3 px-4 rounded-lg transition-all font-display2 tracking-wider"
                        >
                            CRIAR CONTA
                        </motion.button>
                    </form>

                    <p className="text-center text-xs text-gray-500 mt-8 font-mono">
                        Projeto Acadêmico - Sem Dinheiro Real
                    </p>
                </div>
            </motion.div>
        </div>
    );
}
