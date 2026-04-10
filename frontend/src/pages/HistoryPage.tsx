import React, { useState } from 'react';
import { History, Filter, Coins, Star, Zap } from 'lucide-react';

import bgCassino from '../assets/bg-gif.gif';

// Mock baseado na tabela game_spinhistory
const mockSpins = [
  { id: 1, bet: 2.50, payout: 125.00, isFreeSpin: true, combination: '5x Gorila', date: 'Hoje, 14:32' },
  { id: 2, bet: 5.00, payout: 0.00, isFreeSpin: false, combination: 'Nenhuma', date: 'Hoje, 14:30' },
  { id: 3, bet: 5.00, payout: 15.00, isFreeSpin: false, combination: '3x Banana', date: 'Hoje, 14:29' },
  { id: 4, bet: 1.00, payout: 0.00, isFreeSpin: false, combination: 'Nenhuma', date: 'Ontem, 21:15' },
  { id: 5, bet: 1.00, payout: 50.00, isFreeSpin: false, combination: 'Big Win', date: 'Ontem, 21:10' },
];

export const HistoryPage: React.FC = () => {
  const [filter, setFilter] = useState<'all' | 'wins'>('all');

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);

  const filteredSpins = mockSpins.filter(spin => filter === 'all' || spin.payout > 0);

  return (
    <div 
      className="w-full min-h-screen p-4 md:p-6 lg:p-8 relative overflow-hidden bg-[#050508] bg-cover bg-center"
      style={{ backgroundImage: `url(${bgCassino})` }}
    >
      {/* Overlay */}
      <div className="absolute inset-0 bg-[#0B0B0F]/90 backdrop-blur-sm pointer-events-none" />

      {/* Conteúdo z-10 */}
      <div className="relative z-10 max-w-5xl mx-auto">
        <div className="min-h-screen bg-gray-900 text-white p-4 md:p-6 lg:p-8 border border-gray-900 rounded-xl">
          <div className="max-w-4xl mx-auto">
            
            {/* Cabeçalho e Filtros */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
              <div className="flex items-center gap-3">
                <History className="w-8 h-8 text-purple-500" />
                <h1 className="text-2xl md:text-3xl font-bold uppercase tracking-wide">Histórico de Giros</h1>
              </div>

              <div className="flex bg-gray-800 p-1 rounded-lg border border-gray-700 w-full sm:w-auto">
                <button
                  onClick={() => setFilter('all')}
                  className={`flex-1 sm:flex-none px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    filter === 'all' ? 'bg-purple-600 text-white' : 'text-gray-400 hover:text-white'
                  }`}
                >
                  Todos
                </button>
                <button
                  onClick={() => setFilter('wins')}
                  className={`flex-1 sm:flex-none px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center justify-center gap-2 ${
                    filter === 'wins' ? 'bg-green-600 text-white' : 'text-gray-400 hover:text-white'
                  }`}
                >
                  <Star className="w-4 h-4" /> Ganhos
                </button>
              </div>
            </div>

            {/* Lista de Giros */}
            <div className="space-y-3">
              {filteredSpins.map((spin) => {
                const isWin = spin.payout > 0;
                const multiplier = isWin ? (spin.payout / spin.bet).toFixed(1) : 0;

                return (
                  <div 
                    key={spin.id}
                    className={`flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-xl border transition-all hover:bg-opacity-80
                      ${isWin 
                        ? 'bg-gradient-to-r from-green-900/20 to-gray-800 border-green-800/50' 
                        : 'bg-gray-800 border-gray-700'
                      }`}
                  >
                    {/* Info Básica do Giro */}
                    <div className="flex items-center gap-4 mb-3 sm:mb-0">
                      <div className={`p-3 rounded-full ${isWin ? 'bg-green-500/20 text-green-400' : 'bg-gray-700 text-gray-400'}`}>
                        <Coins className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-lg">{spin.combination}</span>
                          {spin.isFreeSpin && (
                            <span className="flex items-center gap-1 bg-orange-500/20 text-orange-400 text-xs px-2 py-0.5 rounded border border-orange-500/30">
                              <Zap className="w-3 h-3" /> Grátis
                            </span>
                          )}
                        </div>
                        <span className="text-xs text-gray-400">{spin.date}</span>
                      </div>
                    </div>

                    {/* Valores */}
                    <div className="flex items-center justify-between sm:justify-end gap-6 border-t border-gray-700 sm:border-t-0 pt-3 sm:pt-0">
                      <div className="text-left sm:text-right">
                        <p className="text-xs text-gray-400 mb-1">Aposta</p>
                        <p className="font-medium">{formatCurrency(spin.bet)}</p>
                      </div>
                      
                      <div className="text-right">
                        <p className="text-xs text-gray-400 mb-1">Retorno</p>
                        <div className="flex items-center justify-end gap-2">
                          {isWin && (
                            <span className="text-xs font-bold text-green-400 bg-green-400/10 px-1.5 py-0.5 rounded">
                              {multiplier}x
                            </span>
                          )}
                          <span className={`font-bold text-lg ${isWin ? 'text-green-400' : 'text-gray-500'}`}>
                            {formatCurrency(spin.payout)}
                          </span>
                        </div>
                      </div>
                    </div>

                  </div>
                );
              })}
              
              {filteredSpins.length === 0 && (
                <div className="text-center py-12 bg-gray-800 rounded-xl border border-gray-700">
                  <Filter className="w-12 h-12 text-gray-500 mx-auto mb-3" />
                  <p className="text-gray-400">Nenhum giro encontrado para este filtro.</p>
                </div>
              )}
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};
