import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm as useRHForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Loader2 } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { motion } from 'framer-motion';

import logoImg from '../assets/logo.png';

// Schema atualizado com os novos campos
const registerSchema = z.object({
    nomeCompleto: z.string().min(5, 'Digite seu nome completo'),
    cpf: z.string().min(11, 'CPF inválido').max(14, 'CPF inválido'),
    email: z.string().email('Email inválido'),
    telefone: z.string().min(10, 'Telefone inválido'),
    dataNascimento: z.string().min(1, 'Data de nascimento é obrigatória'),
    password: z.string().min(6, 'Senha deve ter no mínimo 6 caracteres'),
    confirmPassword: z.string().min(6, 'Confirmação obrigatória'),
}).refine((data) => data.password === data.confirmPassword, {
    message: "Senhas não conferem",
    path: ["confirmPassword"],
});

type RegisterForm = z.infer<typeof registerSchema>;

export default function RegisterPage() {
    const navigate = useNavigate();
    const [error, setError] = useState<string | null>(null);
    const { login, setLoading, isLoading } = useAuthStore();

    const { register, handleSubmit, formState: { errors }, reset } = useRHForm<RegisterForm>({
        resolver: zodResolver(registerSchema)
    });

    const onSubmit = async (data: RegisterForm) => {
        setError(null);
        setLoading(true);

        // Simulating API call
        setTimeout(() => {
            login(
                {
                    id: '2',
                    username: data.nomeCompleto.split(' ')[0], // Usa o primeiro nome como username provisório
                    email: data.email,
                    level: 1,
                    xp: 0,
                    balance: 500,
                    createdAt: new Date().toISOString()
                },
                { access: 'fake-token', refresh: 'fake-refresh' }
            );
            reset();
            navigate('/');
            setLoading(false);
        }, 1500);
    };

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

                    {error && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="w-full bg-red-500/10 border border-brand-red/50 text-brand-red px-4 py-3 rounded mb-6 text-sm font-body"
                        >
                            {error}
                        </motion.div>
                    )}

                    <form onSubmit={handleSubmit(onSubmit)} className="w-full space-y-4">
                        
                        {/* Nome Completo - Ocupa linha inteira */}
                        <div>
                            <label className="block text-xs font-bold text-gray-400 mb-2 font-display2">NOME COMPLETO</label>
                            <input
                                {...register('nomeCompleto')}
                                className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-gray-600 focus:outline-none focus:border-brand-gold/50 focus:ring-1 focus:ring-brand-gold/50 transition-all font-body text-sm"
                                placeholder="João da Silva"
                            />
                            {errors.nomeCompleto && <p className="text-brand-red text-xs mt-1 font-body">{errors.nomeCompleto.message}</p>}
                        </div>

                        {/* Grid para CPF e Data de Nascimento dividirem a mesma linha em telas maiores */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-xs font-bold text-gray-400 mb-2 font-display2">CPF</label>
                                <input
                                    {...register('cpf')}
                                    className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-gray-600 focus:outline-none focus:border-brand-gold/50 focus:ring-1 focus:ring-brand-gold/50 transition-all font-body text-sm"
                                    placeholder="000.000.000-00"
                                />
                                {errors.cpf && <p className="text-brand-red text-xs mt-1 font-body">{errors.cpf.message}</p>}
                            </div>

                            <div>
                                <label className="block text-xs font-bold text-gray-400 mb-2 font-display2">NASCIMENTO</label>
                                <input
                                    {...register('dataNascimento')}
                                    type="date"
                                    className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-2.5 text-gray-300 focus:outline-none focus:border-brand-gold/50 focus:ring-1 focus:ring-brand-gold/50 transition-all font-body text-sm [color-scheme:dark]"
                                />
                                {errors.dataNascimento && <p className="text-brand-red text-xs mt-1 font-body">{errors.dataNascimento.message}</p>}
                            </div>
                        </div>

                        {/* Grid para Email e Telefone */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
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

                            <div>
                                <label className="block text-xs font-bold text-gray-400 mb-2 font-display2">TELEFONE</label>
                                <input
                                    {...register('telefone')}
                                    className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-gray-600 focus:outline-none focus:border-brand-gold/50 focus:ring-1 focus:ring-brand-gold/50 transition-all font-body text-sm"
                                    placeholder="(11) 99999-9999"
                                />
                                {errors.telefone && <p className="text-brand-red text-xs mt-1 font-body">{errors.telefone.message}</p>}
                            </div>
                        </div>

                        {/* Grid para as Senhas */}
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
