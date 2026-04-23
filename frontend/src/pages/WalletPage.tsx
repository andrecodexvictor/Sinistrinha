import React, { useEffect, useState } from 'react';
import { Wallet, ArrowDownCircle, ArrowUpCircle, Clock, CreditCard, Landmark, Loader2 } from 'lucide-react';
import api from '../lib/api';
import { useAuthStore } from '../store/authStore';
import type { Transaction } from '../types/api.types';

import bgCassino from '../assets/bg-gif.gif';

export const WalletPage: React.FC = () => {
  const { user } = useAuthStore();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [depositAmount, setDepositAmount] = useState('');
  const [withdrawAmount, setWithdrawAmount] = useState('');
  const [actionLoading, setActionLoading] = useState(false);
  const [actionMsg, setActionMsg] = useState<string | null>(null);

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);

  const fetchTransactions = async () => {
    setLoading(true);
    try {
      const { data } = await api.get('/payments/transactions/');
      setTransactions(data.results ?? data);
    } catch { /* ignore */ }
    setLoading(false);
  };

  useEffect(() => {
    fetchTransactions();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleDeposit = async () => {
    const amount = parseFloat(depositAmount);
    if (!amount || amount <= 0) return;
    setActionLoading(true);
    setActionMsg(null);
    try {
      await api.post('/payments/deposit/', { amount: amount.toFixed(2) });
      setActionMsg(`Depósito de ${formatCurrency(amount)} realizado!`);
      setDepositAmount('');
      await useAuthStore.getState().fetchProfile();
      await fetchTransactions();
    } catch {
      setActionMsg('Erro ao depositar.');
    }
    setActionLoading(false);
  };

  const handleWithdraw = async () => {
    const amount = parseFloat(withdrawAmount);
    if (!amount || amount <= 0) return;
    setActionLoading(true);
    setActionMsg(null);
    try {
      await api.post('/payments/withdraw/', { amount: amount.toFixed(2) });
      setActionMsg(`Saque de ${formatCurrency(amount)} solicitado!`);
      setWithdrawAmount('');
      await useAuthStore.getState().fetchProfile();
      await fetchTransactions();
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { error?: string } } })?.response?.data?.error || 'Erro ao sacar.';
      setActionMsg(msg);
    }
    setActionLoading(false);
  };

  return (
    <div 
      className="w-full min-h-screen p-4 md:p-6 lg:p-8 relative overflow-hidden bg-[#050508] bg-cover bg-center"
      style={{ backgroundImage: `url(${bgCassino})` }}
    >
      <div className="absolute inset-0 bg-[#0B0B0F]/90 backdrop-blur-sm pointer-events-none" />

      <div className="relative z-10 max-w-5xl mx-auto space-y-6">
        <div className="min-h-screen bg-gray-900 text-white p-4 md:p-6 lg:p-8 border border-gray-900 rounded-xl">
          <div className="max-w-5xl mx-auto space-y-6">
            
            <div className="flex items-center gap-3 mb-6">
              <Wallet className="w-8 h-8 text-teal-500" />
              <h1 className="text-2xl md:text-3xl font-bold uppercase tracking-wide">Minha Carteira</h1>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
              <div className="md:col-span-2 bg-gradient-to-br from-teal-900/50 to-teal-800/20 border border-teal-700/50 rounded-2xl p-6 flex flex-col justify-between">
                <span className="text-teal-200 font-medium mb-2">Saldo Disponível</span>
                <div className="text-4xl md:text-5xl font-extrabold text-white mb-6">
                  {formatCurrency(user?.balance ?? 0)}
                </div>
                
                {actionMsg && (
                  <div className="bg-teal-900/30 border border-teal-700/50 rounded-lg p-3 mb-4 text-sm text-teal-200">
                    {actionMsg}
                  </div>
                )}

                <div className="flex flex-col sm:flex-row gap-3">
                  <div className="flex-1 flex gap-2">
                    <input
                      type="number" min="1" step="0.01"
                      value={depositAmount}
                      onChange={(e) => setDepositAmount(e.target.value)}
                      placeholder="Valor"
                      className="flex-1 bg-black/40 border border-teal-600/30 rounded-lg px-3 py-3 text-white text-sm"
                    />
                    <button
                      onClick={handleDeposit}
                      disabled={actionLoading}
                      className="bg-teal-500 hover:bg-teal-400 text-gray-900 font-bold py-3 px-4 rounded-xl flex items-center gap-2 transition-colors disabled:opacity-50"
                    >
                      {actionLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowDownCircle className="w-5 h-5" />}
                      Depositar
                    </button>
                  </div>
                  <div className="flex-1 flex gap-2">
                    <input
                      type="number" min="1" step="0.01"
                      value={withdrawAmount}
                      onChange={(e) => setWithdrawAmount(e.target.value)}
                      placeholder="Valor"
                      className="flex-1 bg-black/40 border border-gray-600/30 rounded-lg px-3 py-3 text-white text-sm"
                    />
                    <button
                      onClick={handleWithdraw}
                      disabled={actionLoading}
                      className="bg-gray-800 hover:bg-gray-700 border border-gray-600 font-bold py-3 px-4 rounded-xl flex items-center gap-2 transition-colors disabled:opacity-50"
                    >
                      {actionLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowUpCircle className="w-5 h-5" />}
                      Sacar
                    </button>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6 flex flex-col gap-4">
                <h3 className="text-gray-400 font-medium border-b border-gray-700 pb-2">Informações</h3>
                <div className="flex items-center gap-3 bg-gray-900 p-3 rounded-lg border border-gray-700">
                  <CreditCard className="w-6 h-6 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium">Nível {user?.level ?? 1}</p>
                    <p className="text-xs text-gray-500">XP: {user?.xp ?? 0}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 bg-gray-900 p-3 rounded-lg border border-gray-700">
                  <Landmark className="w-6 h-6 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium">Free Spins</p>
                    <p className="text-xs text-gray-500">{user?.freeSpins ?? 0} disponíveis</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gray-800 border border-gray-700 rounded-2xl p-4 md:p-6 mt-8">
              <div className="flex items-center gap-2 mb-6 border-b border-gray-700 pb-4">
                <Clock className="w-5 h-5 text-gray-400" />
                <h2 className="text-xl font-bold">Últimas Transações</h2>
              </div>

              {loading ? (
                <div className="flex justify-center py-8"><Loader2 className="w-8 h-8 animate-spin text-gray-400" /></div>
              ) : transactions.length === 0 ? (
                <p className="text-gray-500 text-center py-8">Nenhuma transação encontrada.</p>
              ) : (
                <div className="space-y-3 md:space-y-0 md:divide-y md:divide-gray-700">
                  {transactions.map((tx) => (
                    <div 
                      key={tx.id} 
                      className="flex flex-col md:flex-row md:items-center justify-between p-4 md:py-4 md:px-2 bg-gray-900 md:bg-transparent rounded-xl md:rounded-none gap-3"
                    >
                      <div className="flex items-center gap-4">
                        <div className={`p-2 rounded-full ${tx.transaction_type === 'deposit' || tx.transaction_type === 'win' || tx.transaction_type === 'bonus' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                          {tx.transaction_type === 'deposit' || tx.transaction_type === 'win' || tx.transaction_type === 'bonus' ? <ArrowDownCircle className="w-5 h-5" /> : <ArrowUpCircle className="w-5 h-5" />}
                        </div>
                        <div>
                          <p className="font-bold capitalize">{tx.transaction_type}</p>
                          <p className="text-xs text-gray-400">{new Date(tx.created_at).toLocaleString('pt-BR')}</p>
                        </div>
                      </div>

                      <div className="flex md:flex-col items-center md:items-end justify-between border-t border-gray-700 md:border-t-0 pt-3 md:pt-0 mt-1 md:mt-0">
                        <span className={`text-xs font-bold px-2 py-1 rounded mb-0 md:mb-1 ${
                          tx.status === 'completed' ? 'bg-green-900/50 text-green-400 border border-green-800' : 
                          tx.status === 'pending' ? 'bg-yellow-900/50 text-yellow-400 border border-yellow-800' :
                          'bg-red-900/50 text-red-400 border border-red-800'
                        }`}>
                          {tx.status === 'completed' ? 'Concluído' : tx.status === 'pending' ? 'Pendente' : tx.status}
                        </span>
                        <span className={`font-bold ${tx.transaction_type === 'deposit' || tx.transaction_type === 'win' || tx.transaction_type === 'bonus' ? 'text-green-400' : 'text-white'}`}>
                          {tx.transaction_type === 'deposit' || tx.transaction_type === 'win' || tx.transaction_type === 'bonus' ? '+' : '-'}{formatCurrency(parseFloat(tx.amount))}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};
