import React from 'react';
import { Brain, Activity, Shield } from 'lucide-react';
import { useTradeStream } from '../hooks/useTradeStream';

const BrainCore: React.FC = () => {
    // আমরা এখন শুধু 'brain' চ্যানেল এবং কানেকশন স্ট্যাটাস ব্যবহার করছি
    const { brain, isConnected } = useTradeStream();

    // ডিফল্ট ভ্যালু (যদি ডেটা না আসে)
    const activeAgents = brain?.active_agents || ['Initializing...'];
    const currentAction = brain?.action || 'HOLD';
    const confidence = brain?.confidence || 0;
    const reason = brain?.reason || 'Waiting for signals...';
    const riskStatus = brain?.risk_status || 'UNKNOWN';

    // কালার কোডিং লজিক
    const actionColor = currentAction === 'BUY' ? 'text-emerald-400' : currentAction === 'SELL' ? 'text-red-400' : 'text-slate-300';
    const progressColor = currentAction === 'BUY' ? 'bg-emerald-500' : currentAction === 'SELL' ? 'bg-red-500' : 'bg-slate-500';

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
                            <span className="text-xs text-slate-400">{isConnected ? 'Live Neural Link' : 'Connecting...'}</span>
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
                {/* AI Reasoning Box */}
                <div className="md:col-span-2 bg-slate-800/50 p-4 rounded-xl border border-slate-700/50">
                    <div className="flex items-center gap-2 mb-2">
                        <Activity className="w-4 h-4 text-purple-400" />
                        <span className="text-slate-400 text-sm">AI Reasoning Engine</span>
                    </div>
                    <p className="text-sm text-slate-200 font-mono leading-relaxed">
                        "{reason}"
                    </p>
                </div>

                {/* Risk Engine Status */}
                <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700/50">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-slate-400 text-sm">Risk Guard</span>
                        <Shield className={`w-4 h-4 ${riskStatus === 'VETO' ? 'text-red-500' : 'text-emerald-400'}`} />
                    </div>
                    <div className="text-lg font-bold text-white">
                        {riskStatus === 'VETO' ? (
                            <span className="text-red-400 animate-pulse">VETO ACTIVE</span>
                        ) : (
                            <span className="text-emerald-400">PASS</span>
                        )}
                    </div>
                </div>
            </div>

            {/* Decision & Confidence Bar */}
            <div className="bg-gradient-to-r from-slate-800 to-slate-900 rounded-xl p-6 border border-slate-700">
                <div className="flex items-center justify-between mb-4">
                    <span className="text-slate-300 font-medium">Swarm Consensus</span>
                    <span className={`text-3xl font-bold ${actionColor}`}>{currentAction}</span>
                </div>

                <div className="space-y-2">
                    <div className="flex justify-between text-sm text-slate-400">
                        <span>Confidence Score</span>
                        <span>{(confidence * 100).toFixed(1)}%</span>
                    </div>
                    <div className="h-3 bg-slate-800 rounded-full overflow-hidden border border-slate-700">
                        <div
                            className={`h-full transition-all duration-500 ${progressColor}`}
                            style={{ width: `${confidence * 100}%` }}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default BrainCore;
