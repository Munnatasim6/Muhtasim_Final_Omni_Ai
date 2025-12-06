import React from 'react';
import { Terminal } from 'lucide-react';
import { useTradeStream } from '../hooks/useTradeStream';

const LogTerminal: React.FC = () => {
    const { logs } = useTradeStream();

    return (
        <div className="bg-black rounded-2xl border border-slate-800 font-mono text-sm overflow-hidden h-full flex flex-col shadow-2xl">
            <div className="bg-slate-900 px-4 py-3 border-b border-slate-800 flex items-center gap-2">
                <Terminal className="w-4 h-4 text-slate-400" />
                <span className="text-slate-300 font-bold">System Logs</span>
                <div className="ml-auto flex gap-1.5">
                    <div className="w-3 h-3 rounded-full bg-red-500/20 border border-red-500/50" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500/20 border border-yellow-500/50" />
                    <div className="w-3 h-3 rounded-full bg-emerald-500/20 border border-emerald-500/50" />
                </div>
            </div>

            <div className="flex-1 p-4 overflow-y-auto space-y-1.5 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
                {logs.length === 0 && (
                    <span className="text-slate-600 italic">Waiting for system events...</span>
                )}
                {logs.map((log, i) => (
                    <div key={i} className="text-slate-300 break-all hover:bg-slate-900/50 px-1 rounded">
                        <span className="text-slate-500 mr-2">{log.split(']')[0]}]</span>
                        <span className={log.includes('ALERT') ? 'text-red-400' : log.includes('Brain') ? 'text-purple-400' : 'text-emerald-400'}>
                            {log.split(']')[1]}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default LogTerminal;
