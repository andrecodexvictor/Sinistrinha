import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm as useRHForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Loader2 } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { motion } from 'framer-motion';

import logoImg from '../assets/logo.png';

const registerSchema = z.object({
    username: z.string().min(3, 'Usuário deve ter no mínimo 3 caracteres'),
    email: z.string().email('Email inválido'),
    password: z.string().min(6, 'Senha deve ter no mínimo 6 caracteres'),
    confirmPassword: z.string().min(6, 'Confirmação obrigatória'),
}).refine((data) => data.password === data.confirmPassword, {
    message: "Senhas não conferem",
    path: ["confirmPassword"],
});

type RegisterForm = z.infer<typeof registerSchema>;

export default function RegisterPage() {
    const navigate = useNavigate();
    const { registerAsync, isLoading, error } = useAuthStore();
    const [localError, setLocalError] = useState<string | null>(null);

    const { register, handleSubmit, formState: { errors } } = useRHForm<RegisterForm>({
        resolver: zodResolver(registerSchema)
    });

    const onSubmit = async (data: RegisterForm) => {
        setLocalError(null);
        const success = await registerAsync(data.username, data.email, data.password);
        if (success) {
            navigate('/');
        } else {
            setLocalError(useAuthStore.getState().error);
        }
    };

    const displayError = localError || error;

    return (
        <div className="min-h-screen bg-[#050508] bg-[url('https://images.unsplash.com/photo-1596838132731-3301c3fd4317?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center flex items-center justify-center p-6 relative overflow-hidden py-12">

            <div className="absolute inset-0 bg-[#0B0B0F]/90 backdrop-blur-sm" />

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="relative z-10 w-full max-w-lg bg-brand-gray/95 border-2 border-brand-red/40 rounded-3xl shadow-[0_0_80px_rgba(139,0,0,0.15)] overflow-hidden backdrop-blur-sm mt-8"
            >
                <div className="p-8 md:p-10 flex flex-col items-center">

                    <div className="mb-4 flex justify-center items-center">
                        <Link to="/" className="inline-block cursor-pointer">
                            <img
                                src= {logoImg}
                                alt="Logo do Jogo"
                                className="w-32 mx-auto mb-6"
                            />
                        </Link>
                    </div>

                    <h1 className="text-2xl md:text-3xl font-bold text-center font-display2 text-brand-gold mb-2 tracking-wider">
                        CRIAR CONTA
                    </h1>

                    <p className="text-xs text-gray-400 mb-6 font-body">SINISTRINHA CASSINO</p>

                    {displayError && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="w-full bg-red-500/10 border border-brand-red/50 text-brand-red px-4 py-3 rounded mb-6 text-sm font-body"
                        >
                            {displayError}
                        </motion.div>
                    )}

                    <form onSubmit={handleSubmit(onSubmit)} className="w-full space-y-4">
                        <div>
                            <label className="block text-xs font-bold text-gray-400 mb-2 font-display2">NOME DE USUÁRIO</label>
                            <input
                                {...register('username')}
                                className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-gray-600 focus:outline-none focus:border-brand-gold/50 focus:ring-1 focus:ring-brand-gold/50 transition-all font-body text-sm"
                                placeholder="seu_usuario"
                            />
                            {errors.username && <p className="text-brand-red text-xs mt-1 font-body">{errors.username.message}</p>}
                        </div>

                        <div>
                            <label className="block text-xs font-bold text-gray-400 mb-2 font-display2">EMAIL</label>
                            <input
                                {...register('email')}
                                type="email"
                                className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-gray-600 focus:outline-none focus:border-brand-gold/50 focus:ring-1 focus:ring-brand-gold/50 transition-all font-body text-sm"
                                placeholder="seu@email.com"
                            />
                            {errors.email && <p className="text-brand-red text-xs mt-1 font-body">{errors.email.message}</p>}
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-xs font-bold text-gray-400 mb-2 font-display2">SENHA</label>
                                <input
                                    {...register('password')}
                                    type="password"
                                    className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-gray-600 focus:outline-none focus:border-brand-gold/50 focus:ring-1 focus:ring-brand-gold/50 transition-all font-body text-sm"
                                    placeholder="••••••••"
                                />
                                {errors.password && <p className="text-brand-red text-xs mt-1 font-body">{errors.password.message}</p>}
                            </div>

                            <div>
                                <label className="block text-xs font-bold text-gray-400 mb-2 font-display2">CONFIRMAR SENHA</label>
                                <input
                                    {...register('confirmPassword')}
                                    type="password"
                                    className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-gray-600 focus:outline-none focus:border-brand-gold/50 focus:ring-1 focus:ring-brand-gold/50 transition-all font-body text-sm"
                                    placeholder="••••••••"
                                />
                                {errors.confirmPassword && <p className="text-brand-red text-xs mt-1 font-body">{errors.confirmPassword.message}</p>}
                            </div>
                        </div>

                        <div className="pt-4 space-y-3">
                            <motion.button
                                type="submit"
                                disabled={isLoading}
                                whileHover={{ scale: isLoading ? 1 : 1.02 }}
                                whileTap={{ scale: isLoading ? 1 : 0.98 }}
                                className="w-full bg-brand-red hover:bg-red-700 text-white font-bold py-3 px-4 rounded-lg shadow-[0_0_15px_rgba(139,0,0,0.4)] hover:shadow-[0_0_25px_rgba(139,0,0,0.6)] transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed font-display2 tracking-wider"
                            >
                                {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'CRIAR CONTA'}
                            </motion.button>

                            <motion.button
                                type="button"
                                onClick={() => navigate('/login')}
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                className="w-full bg-transparent border border-brand-gold/30 hover:border-brand-gold/60 text-brand-gold hover:text-yellow-300 font-bold py-3 px-4 rounded-lg transition-all font-display2 tracking-wider"
                            >
                                JÁ TEM CONTA?
                            </motion.button>
                        </div>
                    </form>

                    <p className="text-center text-xs text-gray-500 mt-6 font-mono">
                        Projeto Acadêmico - Sem Dinheiro Real
                    </p>
                </div>
            </motion.div>
        </div>
    );
}
