import React, { useState } from 'react';
import { Settings, Sliders } from 'lucide-react';

const ConfigPanel: React.FC = () => {
    const [risk, setRisk] = useState(5);

    return (
        <div className="bg-slate-900/50 backdrop-blur-xl p-6 rounded-2xl border border-slate-700/50 shadow-xl">
            <div className="flex items-center gap-3 mb-6">
                <Settings className="text-slate-400" size={20} />
                <h2 className="text-xl font-bold text-white">Strategy Config</h2>
            </div>

            <div className="space-y-6">
                <div>
                    <div className="flex justify-between text-sm mb-2">
                        <span className="text-slate-300">Max Risk per Trade</span>
                        <span className="text-cyan-400 font-bold">{risk}%</span>
                    </div>
                    <input
                        type="range"
                        min="1"
                        max="10"
                        value={risk}
                        onChange={(e) => setRisk(Number(e.target.value))}
                        className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-cyan-500"
                    />
                    <p className="text-xs text-slate-500 mt-2">
                        Adjusting this will instantly update the Risk Engine's threshold.
                    </p>
                </div>

                <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700/50">
                    <div className="flex items-center gap-2">
                        <Sliders size={16} className="text-purple-400" />
                        <span className="text-sm text-slate-300">Auto-Scalping</span>
                    </div>
                    <div className="relative inline-block w-10 h-5 align-middle select-none transition duration-200 ease-in">
                        <input type="checkbox" name="toggle" id="toggle" className="toggle-checkbox absolute block w-5 h-5 rounded-full bg-white border-4 appearance-none cursor-pointer" />
                        <label htmlFor="toggle" className="toggle-label block overflow-hidden h-5 rounded-full bg-gray-300 cursor-pointer"></label>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ConfigPanel;
