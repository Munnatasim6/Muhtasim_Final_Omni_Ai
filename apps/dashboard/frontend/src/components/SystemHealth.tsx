import React from 'react';
import { Cpu, Server, Shield, Activity, HardDrive } from 'lucide-react';
import { useTradeStream } from '../hooks/useTradeStream';

const SystemHealth: React.FC = () => {
    // আমাদের মাল্টি-চ্যানেল হুক থেকে 'system' ডেটা নিচ্ছি
    const { system, isConnected } = useTradeStream();

    // ডিফল্ট ভ্যালু (যদি ডেটা না আসে বা লোডিং অবস্থায় থাকে)
    const status = system?.status || 'OFFLINE';
    const cpu = system?.cpu_usage || 0;
    const ram = system?.ram_usage || 0;
    const riskLevel = system?.risk_level || 'N/A';
    const uptime = system?.uptime || 'Connecting...';

    // স্ট্যাটাস অনুযায়ী কালার সেট করা
    const statusColor = status === 'ONLINE' ? 'text-emerald-400' : 'text-red-500';
    const statusBg = status === 'ONLINE' ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-red-500/10 border-red-500/20';

    return (
        <div className="bg-slate-900/50 backdrop-blur-xl p-6 rounded-2xl border border-slate-700/50 shadow-xl h-full">
            {/* হেডার সেকশন */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <div className="p-3 bg-blue-500/20 rounded-xl">
                        <Activity className="w-6 h-6 text-blue-400" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-white">System Health</h2>
                        <div className="flex items-center gap-2">
                            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500' : 'bg-red-500'} animate-pulse`} />
                            <span className="text-xs text-slate-400">{isConnected ? 'Live Telemetry' : 'Disconnected'}</span>
                        </div>
                    </div>
                </div>
                <div className={`px-3 py-1 rounded-full border ${statusBg}`}>
                    <span className={`text-xs font-bold ${statusColor}`}>{status}</span>
                </div>
            </div>

            {/* প্রোগ্রেস বার এবং স্ট্যাটাস */}
            <div className="space-y-6">

                {/* CPU Usage */}
                <div>
                    <div className="flex justify-between mb-2">
                        <div className="flex items-center gap-2 text-slate-300">
                            <Cpu className="w-4 h-4 text-cyan-400" />
                            <span className="text-sm font-medium">Core i3 Load</span>
                        </div>
                        <span className="text-sm font-bold text-white">{cpu.toFixed(1)}%</span>
                    </div>
                    {/* প্রোগ্রেস বার ব্যাকগ্রাউন্ড */}
                    <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                        {/* ডাইনামিক ফিল */}
                        <div
                            className={`h-full rounded-full transition-all duration-500 ease-out ${cpu > 80 ? 'bg-red-500' : 'bg-cyan-500'}`}
                            style={{ width: `${Math.min(cpu, 100)}%` }}
                        />
                    </div>
                </div>

                {/* RAM Usage */}
                <div>
                    <div className="flex justify-between mb-2">
                        <div className="flex items-center gap-2 text-slate-300">
                            <HardDrive className="w-4 h-4 text-purple-400" />
                            <span className="text-sm font-medium">Memory (12GB)</span>
                        </div>
                        <span className="text-sm font-bold text-white">{ram.toFixed(1)}%</span>
                    </div>
                    <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                        <div
                            className={`h-full rounded-full transition-all duration-500 ease-out ${ram > 90 ? 'bg-red-500' : 'bg-purple-500'}`}
                            style={{ width: `${Math.min(ram, 100)}%` }}
                        />
                    </div>
                </div>

                {/* ইনফো গ্রিড */}
                <div className="grid grid-cols-2 gap-4 mt-4">
                    <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700/50">
                        <div className="flex items-center gap-2 mb-1 text-slate-400">
                            <Shield className="w-3 h-3" />
                            <span className="text-xs">Risk Limit</span>
                        </div>
                        <div className="text-lg font-bold text-white">{riskLevel}</div>
                    </div>
                    <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700/50">
                        <div className="flex items-center gap-2 mb-1 text-slate-400">
                            <Server className="w-3 h-3" />
                            <span className="text-xs">Uptime</span>
                        </div>
                        <div className="text-sm font-bold text-white truncate">{uptime}</div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SystemHealth;
