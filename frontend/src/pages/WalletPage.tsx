import React from 'react';
import { Wallet, ArrowDownCircle, ArrowUpCircle, Clock, CreditCard, Landmark } from 'lucide-react';

import bgCassino from '../assets/bg-gif.gif';

// Dados simulados baseados no seu modelo payments_transaction
const mockTransactions = [
  { id: 1, type: 'DEPOSIT', amount: 500.00, status: 'SUCCESS', date: '2026-03-31 14:20' },
  { id: 2, type: 'WITHDRAW', amount: 150.00, status: 'PENDING', date: '2026-03-30 09:15' },
  { id: 3, type: 'DEPOSIT', amount: 100.00, status: 'SUCCESS', date: '2026-03-28 18:45' },
];

export const WalletPage: React.FC = () => {
  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);

  return (
    <div 
      className="w-full min-h-screen p-4 md:p-6 lg:p-8 relative overflow-hidden bg-[#050508] bg-cover bg-center"
      style={{ backgroundImage: `url(${bgCassino})` }}
    >
      {/* Overlay */}
      <div className="absolute inset-0 bg-[#0B0B0F]/90 backdrop-blur-sm pointer-events-none" />

      {/* Conteúdo z-10 */}
      <div className="relative z-10 max-w-5xl mx-auto space-y-6">
        <div className="min-h-screen bg-gray-900 text-white p-4 md:p-6 lg:p-8 border border-gray-900 rounded-xl">
          <div className="max-w-5xl mx-auto space-y-6">
            
            {/* Cabeçalho */}
            <div className="flex items-center gap-3 mb-6">
              <Wallet className="w-8 h-8 text-teal-500" />
              <h1 className="text-2xl md:text-3xl font-bold uppercase tracking-wide">Minha Carteira</h1>
            </div>

            {/* Grade Superior: Saldo e Ações Rápidas */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
              
              {/* Card de Saldo Principal */}
              <div className="md:col-span-2 bg-gradient-to-br from-teal-900/50 to-teal-800/20 border border-teal-700/50 rounded-2xl p-6 flex flex-col justify-between">
                <span className="text-teal-200 font-medium mb-2">Saldo Disponível</span>
                <div className="text-4xl md:text-5xl font-extrabold text-white mb-6">
                  {formatCurrency(1250.75)}
                </div>
                
                {/* Botões Responsivos: Lado a lado no desktop, empilhados no mobile se muito estreito */}
                <div className="flex flex-col sm:flex-row gap-3">
                  <button className="flex-1 bg-teal-500 hover:bg-teal-400 text-gray-900 font-bold py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-colors">
                    <ArrowDownCircle className="w-5 h-5" />
                    Depositar
                  </button>
                  <button className="flex-1 bg-gray-800 hover:bg-gray-700 border border-gray-600 font-bold py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-colors">
                    <ArrowUpCircle className="w-5 h-5" />
                    Sacar
                  </button>
                </div>
              </div>

              {/* Card de Informações/Métodos */}
              <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6 flex flex-col gap-4">
                <h3 className="text-gray-400 font-medium border-b border-gray-700 pb-2">Métodos Salvos</h3>
                <div className="flex items-center gap-3 bg-gray-900 p-3 rounded-lg border border-gray-700">
                  <CreditCard className="w-6 h-6 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium">Cartão Final 4321</p>
                    <p className="text-xs text-gray-500">Expira em 12/29</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 bg-gray-900 p-3 rounded-lg border border-gray-700">
                  <Landmark className="w-6 h-6 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium">Chave PIX</p>
                    <p className="text-xs text-gray-500">***.123.456-**</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Histórico de Transações Responsivo */}
            <div className="bg-gray-800 border border-gray-700 rounded-2xl p-4 md:p-6 mt-8">
              <div className="flex items-center gap-2 mb-6 border-b border-gray-700 pb-4">
                <Clock className="w-5 h-5 text-gray-400" />
                <h2 className="text-xl font-bold">Últimas Transações</h2>
              </div>

              <div className="space-y-3 md:space-y-0 md:divide-y md:divide-gray-700">
                {mockTransactions.map((tx) => (
                  <div 
                    key={tx.id} 
                    className="flex flex-col md:flex-row md:items-center justify-between p-4 md:py-4 md:px-2 bg-gray-900 md:bg-transparent rounded-xl md:rounded-none gap-3"
                  >
                    {/* Ícone e Tipo */}
                    <div className="flex items-center gap-4">
                      <div className={`p-2 rounded-full ${tx.type === 'DEPOSIT' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                        {tx.type === 'DEPOSIT' ? <ArrowDownCircle className="w-5 h-5" /> : <ArrowUpCircle className="w-5 h-5" />}
                      </div>
                      <div>
                        <p className="font-bold">{tx.type === 'DEPOSIT' ? 'Depósito' : 'Saque'}</p>
                        <p className="text-xs text-gray-400">{tx.date}</p>
                      </div>
                    </div>

                    {/* Status e Valor */}
                    <div className="flex md:flex-col items-center md:items-end justify-between border-t border-gray-700 md:border-t-0 pt-3 md:pt-0 mt-1 md:mt-0">
                      <span className={`text-xs font-bold px-2 py-1 rounded mb-0 md:mb-1 ${
                        tx.status === 'SUCCESS' ? 'bg-green-900/50 text-green-400 border border-green-800' : 
                        'bg-yellow-900/50 text-yellow-400 border border-yellow-800'
                      }`}>
                        {tx.status === 'SUCCESS' ? 'Concluído' : 'Pendente'}
                      </span>
                      <span className={`font-bold ${tx.type === 'DEPOSIT' ? 'text-green-400' : 'text-white'}`}>
                        {tx.type === 'DEPOSIT' ? '+' : '-'}{formatCurrency(tx.amount)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};
