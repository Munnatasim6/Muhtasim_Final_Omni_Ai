import React, { useState } from 'react';
import { Server, Activity, AlertTriangle } from 'lucide-react';

const ScraperControls: React.FC = () => {
  const [replicas, setReplicas] = useState<number>(4);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleScale = async () => {
    if (replicas < 4) {
      setMessage("Minimum 4 scrapers required!");
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const response = await fetch('http://localhost:8000/api/system/scale-scraper', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ replicas }),
      });

      const data = await response.json();
      
      if (response.ok) {
        setMessage(`✅ Success: ${data.message}`);
      } else {
        setMessage(`❌ Error: ${data.detail}`);
      }
    } catch (error) {
      setMessage("❌ Network Error: Could not reach backend.");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-gray-800 rounded-xl shadow-lg border border-gray-700 mt-6">
      <div className="flex items-center gap-3 mb-4">
        <Server className="text-blue-400" size={24} />
        <h2 className="text-xl font-bold text-white">Scraper Microservice Scaling</h2>
      </div>

      <div className="flex flex-col md:flex-row items-center gap-6">
        <div className="flex-1">
          <label className="block text-gray-400 text-sm mb-2">Target Replicas (Min: 4)</label>
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setReplicas(Math.max(4, replicas - 1))}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-white font-bold transition-colors"
            >
              -
            </button>
            <span className="text-2xl font-mono text-blue-300 w-12 text-center">{replicas}</span>
            <button 
              onClick={() => setReplicas(replicas + 1)}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-white font-bold transition-colors"
            >
              +
            </button>
          </div>
        </div>

        <button
          onClick={handleScale}
          disabled={loading || replicas < 4}
          className={`
            px-6 py-3 rounded-lg font-bold text-white flex items-center gap-2 transition-all
            ${loading ? 'bg-gray-600 cursor-wait' : 'bg-blue-600 hover:bg-blue-500 shadow-[0_0_15px_rgba(37,99,235,0.5)]'}
          `}
        >
          {loading ? <Activity className="animate-spin" /> : <Server size={20} />}
          {loading ? 'Scaling...' : 'Apply Scale'}
        </button>
      </div>

      {message && (
        <div className={`mt-4 p-3 rounded-lg text-sm font-medium flex items-center gap-2 ${message.includes('Error') || message.includes('Minimum') ? 'bg-red-900/50 text-red-200' : 'bg-green-900/50 text-green-200'}`}>
          {message.includes('Error') || message.includes('Minimum') ? <AlertTriangle size={16} /> : <Activity size={16} />}
          {message}
        </div>
      )}
      
      <p className="text-xs text-gray-500 mt-4">
        * Scaling operations may take a few seconds. Ensure Docker is running.
      </p>
    </div>
  );
};

export default ScraperControls;
