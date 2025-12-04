import React from 'react';
import {
    ComposedChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Scatter
} from 'recharts';

interface ChartData {
    time: string;
    open: number;
    high: number;
    low: number;
    close: number;
    signal?: 'buy' | 'sell' | null;
}

interface LiveChartProps {
    data: ChartData[];
}

const LiveChart: React.FC<LiveChartProps> = ({ data }) => {

    return (
        <div className="w-full h-[500px] bg-gray-900 p-4 rounded-xl border border-gray-800">
            <h3 className="text-white font-bold mb-4">Live Market Data & AI Signals</h3>
            <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={data}>
                    <defs>
                        <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8} />
                            <stop offset="95%" stopColor="#8884d8" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid stroke="#374151" strokeDasharray="3 3" vertical={false} />
                    <XAxis
                        dataKey="time"
                        stroke="#9CA3AF"
                        tick={{ fontSize: 12 }}
                        tickLine={false}
                        axisLine={false}
                    />
                    <YAxis
                        domain={['auto', 'auto']}
                        stroke="#9CA3AF"
                        tick={{ fontSize: 12 }}
                        tickLine={false}
                        axisLine={false}
                        tickFormatter={(value) => `$${value}`}
                    />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px', color: '#fff' }}
                        itemStyle={{ color: '#fff' }}
                    />

                    {/* Price Line */}
                    <Line
                        type="monotone"
                        dataKey="close"
                        stroke="#8884d8"
                        strokeWidth={2}
                        dot={false}
                        activeDot={{ r: 8 }}
                    />

                    {/* Buy Signals */}
                    <Scatter
                        name="Buy Signal"
                        data={data.filter(d => d.signal === 'buy')}
                        fill="#10B981"
                        shape={(props: any) => {
                            const { cx, cy } = props;
                            return (
                                <g>
                                    <circle cx={cx} cy={cy} r={6} fill="#10B981" fillOpacity={0.5} />
                                    <polygon points={`${cx},${cy + 4} ${cx - 4},${cy + 10} ${cx + 4},${cy + 10}`} fill="#10B981" />
                                </g>
                            );
                        }}
                    />

                    {/* Sell Signals */}
                    <Scatter
                        name="Sell Signal"
                        data={data.filter(d => d.signal === 'sell')}
                        fill="#EF4444"
                        shape={(props: any) => {
                            const { cx, cy } = props;
                            return (
                                <g>
                                    <circle cx={cx} cy={cy} r={6} fill="#EF4444" fillOpacity={0.5} />
                                    <polygon points={`${cx},${cy - 4} ${cx - 4},${cy - 10} ${cx + 4},${cy - 10}`} fill="#EF4444" />
                                </g>
                            );
                        }}
                    />
                </ComposedChart>
            </ResponsiveContainer>
        </div>
    );
};

export default LiveChart;
