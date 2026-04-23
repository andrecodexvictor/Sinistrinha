import React, { useEffect, useState } from 'react';
import { Trophy, Crown, TrendingUp, Loader2 } from 'lucide-react';
import api from '../lib/api';
import type { UserProfile } from '../types/user.types';

import bgCassino from '../assets/bg-gif.gif';

export const RankingPage: React.FC = () => {
  const [ranking, setRanking] = useState<UserProfile[]>([]);
  const [loading, setLoading] = useState(true);

  const formatCurrency = (value: number) => 
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);

  useEffect(() => {
    const fetchRanking = async () => {
      try {
        const { data } = await api.get('/user/leaderboard/');
        setRanking(data.results ?? data);
      } catch { /* ignore */ }
      setLoading(false);
    };
    fetchRanking();
  }, []);

  return (
    <div 
      className="w-full min-h-screen p-6 relative overflow-hidden bg-[#050508] bg-cover bg-center"
      style={{ backgroundImage: `url(${bgCassino})` }}
    >
      <div className="absolute inset-0 bg-[#0B0B0F]/90 backdrop-blur-sm pointer-events-none" />

        <div className="relative z-10 max-w-5xl mx-auto">
          <div className="min-h-screen bg-gray-900 text-white p-6 rounded-lg border border-gray-900 rounded-xl">
            <div className="max-w-4xl mx-auto">
              
              <div className="flex flex-col md:flex-row justify-between items-center mb-8 gap-4">
                <div className="flex items-center gap-3">
                  <Trophy className="w-8 h-8 text-yellow-500" />
                  <h1 className="text-3xl font-bold uppercase tracking-wider">Hall da Fama</h1>
                </div>
              </div>

              <div className="bg-blue-900/30 border border-blue-800/50 rounded-lg p-3 mb-8 flex items-center gap-2 text-blue-200 text-sm">
                <TrendingUp className="w-4 h-4" />
                <span>Ranking por saldo. Continue girando para subir de posição!</span>
              </div>

              {loading ? (
                <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-gray-400" /></div>
              ) : ranking.length === 0 ? (
                <p className="text-gray-500 text-center py-12">Nenhum jogador encontrado.</p>
              ) : (
                <>
                  {/* Podium (Top 3) */}
                  {ranking.length >= 3 && (
                    <div className="flex justify-center items-end gap-2 md:gap-6 mb-12 h-64">
                      {[ranking[1], ranking[0], ranking[2]].map((player, idx) => {
                        if (!player) return null;
                        const isFirst = idx === 1;
                        const isSecond = idx === 0;
                        const username = player.user.username;
                        const totalWon = parseFloat(player.balance);
                        
                        return (
                          <div key={player.id} className="flex flex-col items-center">
                            <div className="relative mb-2">
                              <div className={`w-16 h-16 md:w-20 md:h-20 bg-gray-700 rounded-full border-4 flex items-center justify-center
                                ${isFirst ? 'border-yellow-400' : isSecond ? 'border-gray-300' : 'border-amber-700'}`}>
                                <span className="font-bold text-xl">{username.charAt(0).toUpperCase()}</span>
                              </div>
                              {isFirst && <Crown className="absolute -top-6 left-1/2 -translate-x-1/2 w-8 h-8 text-yellow-400" />}
                            </div>
                            
                            <div className={`w-24 md:w-32 rounded-t-lg flex flex-col items-center p-3
                              ${isFirst ? 'h-40 bg-gradient-to-t from-yellow-600/20 to-yellow-500/10 border-t-2 border-yellow-500' : 
                                isSecond ? 'h-32 bg-gradient-to-t from-gray-500/20 to-gray-400/10 border-t-2 border-gray-400' : 
                                'h-24 bg-gradient-to-t from-amber-800/20 to-amber-700/10 border-t-2 border-amber-700'}`}>
                              <span className="font-bold text-lg mb-1">{isFirst ? '1º' : isSecond ? '2º' : '3º'}</span>
                              <span className="text-xs text-gray-400 truncate w-full text-center">{username}</span>
                              <span className="text-sm font-bold text-green-400 mt-auto">{formatCurrency(totalWon)}</span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}

                  {/* Rest of the list */}
                  {ranking.length > 3 && (
                    <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
                      <table className="w-full text-left border-collapse">
                        <thead>
                          <tr className="bg-gray-900/50 text-gray-400 text-sm uppercase">
                            <th className="p-4 font-medium">Posição</th>
                            <th className="p-4 font-medium">Jogador</th>
                            <th className="p-4 font-medium text-center">Nível</th>
                            <th className="p-4 font-medium text-right">Saldo</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-700">
                          {ranking.slice(3).map((player, index) => (
                            <tr key={player.id} className="hover:bg-gray-700/50 transition-colors">
                              <td className="p-4 font-bold text-gray-400">#{index + 4}</td>
                              <td className="p-4 font-medium flex items-center gap-3">
                                <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center text-xs">
                                  {player.user.username.charAt(0).toUpperCase()}
                                </div>
                                {player.user.username}
                              </td>
                              <td className="p-4 text-center">
                                <span className="bg-indigo-900/50 text-indigo-300 px-2 py-1 rounded text-xs border border-indigo-700">
                                  Lvl {player.level}
                                </span>
                              </td>
                              <td className="p-4 text-right font-bold text-green-400">
                                {formatCurrency(parseFloat(player.balance))}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </>
              )}
          </div>
        </div>
      </div>
    </div>
  );
};
