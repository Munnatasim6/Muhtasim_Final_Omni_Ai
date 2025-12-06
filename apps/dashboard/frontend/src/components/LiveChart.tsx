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
import { useTradeStream } from '../hooks/useTradeStream';
import { Activity, TrendingUp, ChevronDown } from 'lucide-react';

interface ChartData {
    time: string;
    price: number;
    volume: number;
}

const ASSETS = [
    { symbol: 'BTC/USDT', name: 'Bitcoin' },
    { symbol: 'ETH/USDT', name: 'Ethereum' },
    { symbol: 'SOL/USDT', name: 'Solana' },
    { symbol: 'BNB/USDT', name: 'Binance Coin' }
];

const LiveChart: React.FC = () => {
    const { market, isConnected } = useTradeStream();
    const [data, setData] = useState<ChartData[]>([]);
    const [selectedAsset, setSelectedAsset] = useState<string>('BTC/USDT');
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);

    // ডেটা হ্যান্ডলিং
    useEffect(() => {
        if (market && market.symbol === selectedAsset) {
            setData(prev => {
                const newPoint = {
                    time: new Date(market.timestamp * 1000).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
                    price: market.price,
                    volume: market.volume
                };
                // Keep last 50 data points per asset
                const newData = [...prev, newPoint];
                if (newData.length > 50) return newData.slice(newData.length - 50);
                return newData;
            });
        }
    }, [market, selectedAsset]);

    // অ্যাসেট পরিবর্তন হলে চার্ট ক্লিয়ার করা
    const handleAssetChange = (symbol: string) => {
        if (symbol !== selectedAsset) {
            setSelectedAsset(symbol);
            setData([]); // Clear old data
            setIsDropdownOpen(false);
        }
    };

    const latestPrice = data.length > 0 ? data[data.length - 1].price : 0;
    const previousPrice = data.length > 1 ? data[data.length - 2].price : 0;
    const isUp = latestPrice >= previousPrice;

    if (!isConnected && data.length === 0) {
        return (
            <div className="w-full h-[400px] bg-slate-900/50 backdrop-blur-xl rounded-2xl border border-slate-700/50 flex items-center justify-center">
                <div className="flex flex-col items-center gap-3 text-slate-500">
                    <Activity className="w-8 h-8 animate-pulse" />
                    <span className="font-mono text-sm">Connecting to {selectedAsset} Feed...</span>
                </div>
            </div>
        );
    }

    return (
        <div className="w-full h-[400px] bg-slate-900/50 backdrop-blur-xl p-4 rounded-2xl border border-slate-700/50 shadow-xl flex flex-col">
            {/* Header controls with Asset Selector */}
            <div className="flex justify-between items-start mb-4 px-2">
                <div>
                    <div className="flex items-center gap-4">
                        <h3 className="text-white font-bold flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                            Live Feed
                        </h3>

                        {/* Custom Dropdown (Preserved Feature) */}
                        <div className="relative">
                            <button
                                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                                className="flex items-center gap-2 px-2 py-1 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded-lg text-xs font-mono text-white transition-colors"
                            >
                                <span className={selectedAsset === 'BTC/USDT' ? 'text-orange-400' : selectedAsset === 'ETH/USDT' ? 'text-purple-400' : 'text-blue-400'}>
                                    {selectedAsset}
                                </span>
                                <ChevronDown className="w-3 h-3 text-slate-400" />
                            </button>

                            {isDropdownOpen && (
                                <div className="absolute top-full left-0 mt-2 w-48 bg-slate-800 border border-slate-700 rounded-xl shadow-2xl z-50 overflow-hidden">
                                    {ASSETS.map((asset) => (
                                        <button
                                            key={asset.symbol}
                                            onClick={() => handleAssetChange(asset.symbol)}
                                            className={`w-full text-left px-4 py-3 text-sm font-medium hover:bg-slate-700 transition-colors flex items-center justify-between ${selectedAsset === asset.symbol ? 'bg-slate-700/50 text-white' : 'text-slate-400'}`}
                                        >
                                            <span>{asset.name}</span>
                                            <span className="text-xs font-mono opacity-50">{asset.symbol}</span>
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">Real-time WebSocket Stream</p>
                </div>

                <div className="text-right">
                    <p className={`text-2xl font-mono font-bold ${isUp ? 'text-emerald-400' : 'text-red-400'}`}>
                        ${latestPrice.toFixed(2)}
                    </p>
                    <p className="text-xs text-slate-400">Vol: {data.length > 0 ? data[data.length - 1].volume.toFixed(0) : '---'}</p>
                </div>
            </div>

            {/* Chart Area */}
            <ResponsiveContainer width="100%" height="85%">
                <AreaChart data={data}>
                    <defs>
                        <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={isUp ? "#10b981" : "#ef4444"} stopOpacity={0.3} />
                            <stop offset="95%" stopColor={isUp ? "#10b981" : "#ef4444"} stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid stroke="#334155" strokeDasharray="3 3" vertical={false} opacity={0.3} />
                    <XAxis
                        dataKey="time"
                        stroke="#64748b"
                        tick={{ fontSize: 10, fill: '#64748b' }}
                        tickLine={false}
                        axisLine={false}
                        minTickGap={30}
                    />
                    <YAxis
                        domain={['auto', 'auto']}
                        stroke="#64748b"
                        tick={{ fontSize: 10, fill: '#64748b' }}
                        tickLine={false}
                        axisLine={false}
                        tickFormatter={(val) => `$${val.toLocaleString()}`}
                        width={60}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#0f172a',
                            border: '1px solid #1e293b',
                            borderRadius: '8px',
                            color: '#f8fafc'
                        }}
                        itemStyle={{ color: isUp ? '#34d399' : '#f87171', fontSize: '12px' }}
                        labelStyle={{ color: '#94a3b8', fontSize: '10px' }}
                        cursor={{ stroke: '#475569', strokeWidth: 1, strokeDasharray: '4 4' }}
                    />
                    <Area
                        type="monotone"
                        dataKey="price"
                        stroke={isUp ? "#10b981" : "#ef4444"}
                        strokeWidth={2}
                        fillOpacity={1}
                        fill="url(#colorPrice)"
                        isAnimationActive={false}
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
};

export default LiveChart;
