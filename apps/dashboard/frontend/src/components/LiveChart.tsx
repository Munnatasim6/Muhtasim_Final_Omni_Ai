import React, { useState, useEffect } from 'react';
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from 'recharts';
import { useFixedTicker } from '../hooks/useFixedTicker';
import { Activity } from 'lucide-react';

interface ChartData {
    time: string;
    price: number;
    volume: number;
}

const LiveChart: React.FC = () => {
    const { ticker, isConnected } = useFixedTicker('BTC/USDT');
    const [data, setData] = useState<ChartData[]>([]);

    // Data Handling
    useEffect(() => {
        if (ticker) {
            setData(prev => {
                const newPoint = {
                    time: new Date(ticker.timestamp * 1000).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
                    price: ticker.price,
                    volume: ticker.volume
                };
                // Keep last 60 data points (1 minute of history roughly)
                const newData = [...prev, newPoint];
                if (newData.length > 60) return newData.slice(newData.length - 60);
                return newData;
            });
        }
    }, [ticker]);

    const currentPrice = ticker?.price || 0;
    const priceColor = (data.length > 1 && data[data.length - 1].price >= data[data.length - 2].price)
        ? '#10B981'
        : '#EF4444';

    return (
        <div className="w-full h-[350px] bg-slate-900/50 backdrop-blur-xl p-4 rounded-2xl border border-slate-700/50 shadow-xl flex flex-col">
            <div className="flex justify-between items-center mb-4 px-2">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-slate-800 rounded-lg">
                        <Activity className="w-5 h-5 text-emerald-400" />
                    </div>
                    <div>
                        <h3 className="text-white font-bold text-lg">Bitcoin (BTC) - Live Trend</h3>
                        <div className="flex items-center gap-2">
                            <span className="relative flex h-2 w-2">
                                {isConnected && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>}
                                <span className={`relative inline-flex rounded-full h-2 w-2 ${isConnected ? 'bg-emerald-500' : 'bg-red-500'}`}></span>
                            </span>
                            <span className="text-xs text-slate-400 font-mono">
                                {isConnected ? 'LIVE FEED (1s)' : 'DISCONNECTED'}
                            </span>
                        </div>
                    </div>
                </div>
                <div className="text-right">
                    <p className="text-2xl font-mono font-bold text-white transition-colors duration-300" style={{ color: priceColor }}>
                        ${currentPrice.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </p>
                    <p className="text-xs text-slate-500 font-mono">Last Update: {ticker?.timestamp ? new Date(ticker.timestamp * 1000).toLocaleTimeString() : '--:--'}</p>
                </div>
            </div>

            <div className="w-full flex-1 min-h-0">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data}>
                        <defs>
                            <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor={priceColor} stopOpacity={0.3} />
                                <stop offset="95%" stopColor={priceColor} stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                        <XAxis
                            dataKey="time"
                            stroke="#475569"
                            fontSize={10}
                            tickLine={false}
                            axisLine={false}
                            minTickGap={30}
                        />
                        <YAxis
                            domain={['auto', 'auto']}
                            orientation="right"
                            stroke="#475569"
                            fontSize={11}
                            tickLine={false}
                            axisLine={false}
                            tickFormatter={(val) => val.toLocaleString()}
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: '#0f172a',
                                border: '1px solid #1e293b',
                                borderRadius: '8px',
                                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                            }}
                            itemStyle={{ color: '#e2e8f0', fontSize: '12px', fontFamily: 'monospace' }}
                            labelStyle={{ color: '#94a3b8', fontSize: '10px', marginBottom: '4px' }}
                        />
                        <Area
                            type="monotone"
                            dataKey="price"
                            stroke={priceColor}
                            strokeWidth={2}
                            fillOpacity={1}
                            fill="url(#colorPrice)"
                            isAnimationActive={false}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default LiveChart;
