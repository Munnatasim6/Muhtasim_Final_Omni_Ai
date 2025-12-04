import React, { useState } from 'react';
import { Cpu, CloudLightning, Terminal, Play, Activity } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface TrainingJob {
  id: string;
  type: 'LOCAL' | 'CLOUD';
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
  progress: number;
  logs: string[];
  accuracy: number;
}

interface ChartData {
  epoch: number;
  accuracy: number;
}

const TrainingNexus: React.FC = () => {
  const [activeJob, setActiveJob] = useState<TrainingJob | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [chartData] = useState<ChartData[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  const startTraining = async (type: 'LOCAL' | 'CLOUD') => {
    setLoading(true);
    setLogs(prev => [...prev, `Initializing ${type} training sequence...`]);

    try {
      const response = await fetch('http://localhost:8000/train', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model_id: "lstm_v1",
          type: type,
          epochs: 10
        }),
      });

      if (!response.ok) {
        throw new Error(`Training failed to start: ${response.statusText}`);
      }

      const data = await response.json();
      const jobId = data.job_id || data.id || "unknown_id";
      const status = data.status || "PENDING";

      setLogs(prev => [...prev, `Job Started! ID: ${jobId}`, `Status: ${status}`]);

      setActiveJob({
        id: jobId,
        type,
        status: 'RUNNING', // Assume running if started successfully
        progress: 0,
        logs: [],
        accuracy: 0
      });

    } catch (error: any) {
      console.error("Training Error:", error);
      setLogs(prev => [...prev, `Error: ${error.message}`]);
    } finally {
      setLoading(false);
    }
  };

  // Optional: Poll for job status if backend supports it
  // For now, we just display the logs of the action taken

  return (
    <div className="p-6 bg-slate-900 text-slate-100 min-h-screen font-mono">
      <header className="mb-8 flex items-center justify-between border-b border-slate-700 pb-4">
        <div>
          <h1 className="text-3xl font-bold text-cyan-400 flex items-center gap-2">
            <Activity className="w-8 h-8" />
            NEURAL TRAINING NEXUS
          </h1>
          <p className="text-slate-400 mt-1">Manage Model Training & Optimization</p>
        </div>
        <div className="flex gap-4">
          <div className="flex items-center gap-2 px-4 py-2 bg-slate-800 rounded border border-slate-700">
            <Cpu className="w-4 h-4 text-green-400" />
            <span className="text-sm">Local GPU: RTX 4090 (Idle)</span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-slate-800 rounded border border-slate-700">
            <CloudLightning className="w-4 h-4 text-yellow-400" />
            <span className="text-sm">Vertex AI: Connected</span>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Control Panel */}
        <div className="space-y-6">
          {/* Local Training Card */}
          <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 hover:border-cyan-500/50 transition-colors">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                  <Cpu className="text-cyan-400" /> Local Training
                </h3>
                <p className="text-sm text-slate-400 mt-1">CUDA Accelerated (cuDNN 8.9)</p>
              </div>
              <button
                onClick={() => startTraining('LOCAL')}
                disabled={loading || activeJob?.status === 'RUNNING'}
                className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-600 rounded font-bold text-white flex items-center gap-2 transition-all"
              >
                {loading ? <Activity className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />} START
              </button>
            </div>
            <div className="text-xs text-slate-500">
              <p>• Batch Size: 64</p>
              <p>• Precision: FP16</p>
              <p>• Workers: 8</p>
            </div>
          </div>

          {/* Cloud Training Card */}
          <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 hover:border-yellow-500/50 transition-colors">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                  <CloudLightning className="text-yellow-400" /> Cloud Training
                </h3>
                <p className="text-sm text-slate-400 mt-1">Google Vertex AI (Tesla T4)</p>
              </div>
              <button
                onClick={() => startTraining('CLOUD')}
                disabled={loading || activeJob?.status === 'RUNNING'}
                className="px-4 py-2 bg-yellow-600 hover:bg-yellow-500 disabled:bg-slate-600 rounded font-bold text-white flex items-center gap-2 transition-all"
              >
                {loading ? <Activity className="w-4 h-4 animate-spin" /> : <CloudLightning className="w-4 h-4" />} DEPLOY JOB
              </button>
            </div>
            <div className="text-xs text-slate-500">
              <p>• Region: us-central1</p>
              <p>• Container: PyTorch 1.13</p>
              <p>• Cost Est: $0.35/hr</p>
            </div>
          </div>

          {/* Performance Chart */}
          <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 h-64">
            <h4 className="text-sm font-bold text-slate-300 mb-4">Real-time Accuracy</h4>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="epoch" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" domain={[0, 1]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }}
                  itemStyle={{ color: '#cbd5e1' }}
                />
                <Line type="monotone" dataKey="accuracy" stroke="#22d3ee" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Terminal / Logs */}
        <div className="bg-black rounded-lg border border-slate-700 flex flex-col h-[600px] font-mono text-sm">
          <div className="bg-slate-800 px-4 py-2 rounded-t-lg border-b border-slate-700 flex items-center gap-2">
            <Terminal className="w-4 h-4 text-slate-400" />
            <span className="text-slate-300">System Logs</span>
          </div>
          <div className="flex-1 p-4 overflow-y-auto space-y-1 text-green-400">
            {logs.map((log, i) => (
              <div key={i} className="break-all font-mono opacity-90 hover:opacity-100">
                <span className="text-slate-500 mr-2">[{new Date().toLocaleTimeString()}]</span>
                {log}
              </div>
            ))}
            {activeJob?.status === 'RUNNING' && (
              <div className="animate-pulse">_</div>
            )}
          </div>

          {/* Progress Bar */}
          {activeJob && (
            <div className="p-4 border-t border-slate-800 bg-slate-900">
              <div className="flex justify-between text-xs text-slate-400 mb-1">
                <span>Status: {activeJob.status}</span>
                <span>{activeJob.progress}%</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-500 ${activeJob.type === 'CLOUD' ? 'bg-yellow-500' : 'bg-cyan-500'
                    }`}
                  style={{ width: `${activeJob.progress}%` }}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TrainingNexus;
