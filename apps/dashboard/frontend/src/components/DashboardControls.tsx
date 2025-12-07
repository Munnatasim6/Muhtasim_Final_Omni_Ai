import React, { useState } from 'react';
import { Power, Play, AlertOctagon } from 'lucide-react';

const DashboardControls: React.FC = () => {
  const [status, setStatus] = useState<'ACTIVE' | 'STOPPED'>('ACTIVE');
  const [loading, setLoading] = useState(false);

  const callApi = async (endpoint: string) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/system/${endpoint}`, { method: 'POST' });
      if (res.ok) {
        if (endpoint === 'kill') setStatus('STOPPED');
        if (endpoint === 'resume') setStatus('ACTIVE');
        alert(`System ${endpoint === 'kill' ? 'HALTED' : 'RESUMED'} successfully!`);
      }
    } catch (err) {
      console.error(err);
      alert('Command Failed! Check console.');
    }
    setLoading(false);
  };

  return (
    <div className="p-6 bg-slate-900/50 backdrop-blur-xl rounded-2xl border border-slate-700/50 shadow-xl">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-white">Emergency Override</h2>
        <span className={`px-3 py-1 rounded-full text-xs font-bold ${status === 'ACTIVE' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'
          }`}>
          {status}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <button
          onClick={() => callApi('resume')}
          disabled={loading || status === 'ACTIVE'}
          className="flex items-center justify-center gap-2 p-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 disabled:text-slate-500 text-white font-bold transition-all shadow-lg shadow-emerald-900/20"
        >
          <Play size={20} />
          RESUME
        </button>

        <button
          onClick={() => callApi('kill')}
          disabled={loading || status === 'STOPPED'}
          className="flex items-center justify-center gap-2 p-4 rounded-xl bg-red-600 hover:bg-red-500 disabled:bg-slate-700 disabled:text-slate-500 text-white font-bold transition-all shadow-lg shadow-red-900/20 animate-pulse hover:animate-none"
        >
          <Power size={20} />
          KILL SWITCH
        </button>
      </div>

      <div className="mt-4 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg flex items-start gap-3">
        <AlertOctagon className="text-yellow-500 shrink-0" size={18} />
        <p className="text-xs text-yellow-200/80">
          Warning: Kill Switch will immediately cancel all open orders and halt the Swarm Engine.
        </p>
      </div>
    </div>
  );
};

export default DashboardControls;
