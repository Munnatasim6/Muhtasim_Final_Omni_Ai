import React, { useState } from 'react';
import { Power, ShieldAlert } from 'lucide-react';

interface DashboardControlsProps {
  onSystemStop?: () => void;
}

const DashboardControls: React.FC<DashboardControlsProps> = ({ onSystemStop }) => {
  const [isStopping, setIsStopping] = useState(false);
  const [status, setStatus] = useState<'active' | 'stopping' | 'stopped'>('active');

  const handleKillSwitch = async () => {
    if (!window.confirm("WARNING: This will immediately cancel ALL open orders and stop the bot. Are you sure?")) {
      return;
    }

    setIsStopping(true);
    setStatus('stopping');

    try {
      // API call to backend kill switch
      const response = await fetch('http://localhost:8000/api/system/kill', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setStatus('stopped');
        alert("System Emergency Stop Triggered Successfully.");
        if (onSystemStop) onSystemStop();
      } else {
        alert("Failed to trigger Emergency Stop! Check console.");
        setStatus('active');
      }
    } catch (error) {
      console.error("Emergency Stop Error:", error);
      alert("Network Error: Could not reach backend.");
      setStatus('active');
    } finally {
      setIsStopping(false);
    }
  };

  return (
    <div className="p-4 bg-gray-800 rounded-lg shadow-lg border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <ShieldAlert className="text-yellow-500" />
          System Controls
        </h2>
        <span className={`px-3 py-1 rounded-full text-sm font-bold ${status === 'active' ? 'bg-green-900 text-green-400' :
            status === 'stopping' ? 'bg-yellow-900 text-yellow-400' :
              'bg-red-900 text-red-400'
          }`}>
          {status.toUpperCase()}
        </span>
      </div>

      <div className="grid grid-cols-1 gap-4">
        <button
          onClick={handleKillSwitch}
          disabled={isStopping || status === 'stopped'}
          className={`
            flex items-center justify-center gap-3 px-6 py-4 rounded-lg font-bold text-lg transition-all
            ${status === 'stopped'
              ? 'bg-gray-600 cursor-not-allowed text-gray-400'
              : 'bg-red-600 hover:bg-red-700 text-white shadow-[0_0_15px_rgba(220,38,38,0.5)] hover:shadow-[0_0_25px_rgba(220,38,38,0.7)]'
            }
          `}
        >
          <Power size={24} />
          {isStopping ? 'STOPPING SYSTEM...' : 'EMERGENCY KILL SWITCH'}
        </button>

        <p className="text-xs text-gray-400 text-center mt-2">
          * Triggers immediate cancellation of all open orders and halts execution loop.
        </p>
      </div>
    </div>
  );
};

export default DashboardControls;
