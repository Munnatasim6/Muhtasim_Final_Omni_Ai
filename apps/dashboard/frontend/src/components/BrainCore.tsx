import React from 'react';
import { Brain, Zap, Shield, TrendingUp } from 'lucide-react';
import { useTradeStream } from '../hooks/useTradeStream';

const BrainCore: React.FC = () => {
    const { data, isConnected } = useTradeStream();

    // Default values if no data yet
    const activeAgents = data?.active_agents || ['Initializing...'];
    const currentAction = data?.signals?.action || 'HOLD';
    const confidence = data?.signals?.confidence || 0;
    const agentDecisions = data?.signals?.agent_decisions || {};

    return (
        <div className="bg-slate-900/50 backdrop-blur-xl p-6 rounded-2xl border border-slate-700/50 shadow-xl">
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <div className="p-3 bg-indigo-500/20 rounded-xl">
                        <Brain className="w-6 h-6 text-indigo-400" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-white">Swarm Intelligence Core</h2>
                        <div className="flex items-center gap-2">
                            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500' : 'bg-red-500'} animate-pulse`} />
                            <span className="text-xs text-slate-400">{isConnected ? 'Live Swarm Active' : 'Connecting...'}</span>
                        </div>
                    </div>
                </div>
                <div className="flex gap-2">
                    {activeAgents.map((agent, idx) => (
                        <span key={idx} className="px-3 py-1 bg-slate-800 rounded-full text-xs font-medium text-slate-300 border border-slate-700">
                            {agent}
                        </span>
                    ))}
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                {/* Scalper Agent Status */}
                <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700/50">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-slate-400 text-sm">Scalper (DQN)</span>
                        <Zap className="w-4 h-4 text-yellow-400" />
                    </div>
                    <div className="text-lg font-bold text-white">
                        {agentDecisions['scalper'] || 'WAITING'}
                    </div>
                </div>

                {/* Trend Agent Status */}
                <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700/50">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-slate-400 text-sm">Trend (PPO)</span>
                        <TrendingUp className="w-4 h-4 text-blue-400" />
                    </div>
                    <div className="text-lg font-bold text-white">
                        {agentDecisions['trend'] || 'WAITING'}
                    </div>
                </div>

                {/* Risk Engine Status */}
                <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700/50">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-slate-400 text-sm">Risk Engine</span>
                        <Shield className="w-4 h-4 text-emerald-400" />
                    </div>
                    <div className="text-lg font-bold text-white">
                        {agentDecisions['risk'] === 'VETO' ? (
                            <span className="text-red-400">VETO BLOCKED</span>
                        ) : (
                            <span className="text-emerald-400">PASS</span>
                        )}
                    </div>
                </div>
            </div>

            <div className="bg-gradient-to-r from-indigo-500/10 to-purple-500/10 rounded-xl p-6 border border-indigo-500/20">
                <div className="flex items-center justify-between mb-4">
                    <span className="text-slate-300 font-medium">Swarm Consensus</span>
                    <span className="text-2xl font-bold text-white">{currentAction}</span>
                </div>

                <div className="space-y-2">
                    <div className="flex justify-between text-sm text-slate-400">
                        <span>Confidence Score</span>
                        <span>{(confidence * 100).toFixed(1)}%</span>
                    </div>
                    <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500"
                            style={{ width: `${confidence * 100}%` }}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default BrainCore;
