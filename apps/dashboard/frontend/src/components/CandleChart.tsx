import React, { useState, useEffect, useRef } from 'react';
import { createChart, ColorType, ISeriesApi, Time } from 'lightweight-charts';
import { useTradeStream } from '../hooks/useTradeStream';
import { Activity, Search, BarChart2, TrendingUp } from 'lucide-react';
import { RSI, EMA, MACD, StochasticRSI, IchimokuCloud } from 'technicalindicators';

const TIMEFRAMES = ['1m', '5m', '15m', '1h', '4h', '12h', '1d', '1w', '1M'];

const CandleChart: React.FC = () => {
    const { market, history, isConnected, changeSymbol } = useTradeStream();
    const [activeSymbol, setActiveSymbol] = useState<string>('BTC/USDT');
    const [activeTimeframe, setActiveTimeframe] = useState<string>('1m');
    const [chartType, setChartType] = useState<'standard' | 'heiken'>('heiken');
    const [searchInput, setSearchInput] = useState('');
    const [currentTime, setCurrentTime] = useState(new Date());
    const [indicators, setIndicators] = useState<any>(null);

    const chartContainerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<any>(null);
    const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
    const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);
    const lastRawCandleRef = useRef<any>(null);
    const lastHACandleRef = useRef<any>(null);

    // Clock Tick
    useEffect(() => {
        const timer = setInterval(() => setCurrentTime(new Date()), 1000);
        return () => clearInterval(timer);
    }, []);

    // Initialize Chart
    useEffect(() => {
        if (!chartContainerRef.current) return;

        const chart = createChart(chartContainerRef.current, {
            layout: {
                background: { type: ColorType.Solid, color: 'transparent' },
                textColor: '#94a3b8',
            },
            grid: {
                vertLines: { color: '#334155', visible: false },
                horzLines: { color: '#334155', visible: false },
            },
            width: chartContainerRef.current.clientWidth,
            height: chartContainerRef.current.clientHeight,
            handleScale: {
                axisPressedMouseMove: true,
                mouseWheel: true,
                pinch: true,
            },
            crosshair: {
                mode: 1,
            },
            timeScale: {
                timeVisible: true,
                secondsVisible: false,
                borderColor: '#475569',
            },
            rightPriceScale: {
                borderColor: '#475569',
                scaleMargins: {
                    top: 0.05,
                    bottom: 0.35,
                },
            },
        });

        const candlestickSeries = chart.addCandlestickSeries({
            upColor: '#10b981',
            downColor: '#ef4444',
            borderVisible: false,
            wickUpColor: '#10b981',
            wickDownColor: '#ef4444',
        });

        const volumeSeries = chart.addHistogramSeries({
            color: '#26a69a',
            priceFormat: { type: 'volume' },
            priceScaleId: 'volume',
        });

        chart.priceScale('volume').applyOptions({
            scaleMargins: {
                top: 0.75,
                bottom: 0,
            },
            visible: false,
        });

        chartRef.current = chart;
        candlestickSeriesRef.current = candlestickSeries;
        volumeSeriesRef.current = volumeSeries;

        const resizeObserver = new ResizeObserver((entries) => {
            if (entries.length === 0 || !entries[0].target) return;
            const newRect = entries[0].contentRect;
            chart.applyOptions({ width: newRect.width, height: newRect.height });
        });

        resizeObserver.observe(chartContainerRef.current);

        return () => {
            resizeObserver.disconnect();
            chart.remove();
        };
    }, []);

    // Handle Data & Indicators
    useEffect(() => {
        if (!history || history.length === 0 || !candlestickSeriesRef.current || !volumeSeriesRef.current) return;

        // Process Indicators (Safe Mode)
        try {
            const closes = history.map(c => c[4]);
            const highs = history.map(c => c[2]);
            const lows = history.map(c => c[3]);

            let computed = {
                rsi: 0,
                ema: 0,
                macd: { MACD: 0, signal: 0, histogram: 0 },
                stoch: { k: 0, d: 0 },
                cloud: { spanA: 0, spanB: 0 }
            };

            const rsiRes = RSI.calculate({ values: closes, period: 14 });
            if (rsiRes.length > 0) computed.rsi = rsiRes[rsiRes.length - 1];

            const emaRes = EMA.calculate({ values: closes, period: 20 });
            if (emaRes.length > 0) computed.ema = emaRes[emaRes.length - 1];

            const macdRes = MACD.calculate({ values: closes, fastPeriod: 12, slowPeriod: 26, signalPeriod: 9, SimpleMAOscillator: false, SimpleMASignal: false });
            if (macdRes.length > 0) computed.macd = macdRes[macdRes.length - 1];

            const stochRes = StochasticRSI.calculate({ values: closes, rsiPeriod: 14, stochasticPeriod: 14, kPeriod: 3, dPeriod: 3 });
            if (stochRes.length > 0) computed.stoch = stochRes[stochRes.length - 1];

            // Ichimoku Cloud sometimes fails if data is too short (needs 52+ candles)
            if (highs.length > 52) {
                const ichiRes = IchimokuCloud.calculate({ high: highs, low: lows, conversionPeriod: 9, basePeriod: 26, spanPeriod: 52, displacement: 26 });
                if (ichiRes.length > 0) computed.cloud = ichiRes[ichiRes.length - 1];
            }

            setIndicators(computed);
        } catch (error) {
            console.warn("Indicator Calc Failed:", error);
            // Non-blocking error
        }

        const rawObjects = history.map(candle => ({
            time: (candle[0] / 1000) as Time,
            open: candle[1],
            high: candle[2],
            low: candle[3],
            close: candle[4],
            volume: candle[5]
        }));

        volumeSeriesRef.current.setData(rawObjects.map(c => ({
            time: c.time,
            value: c.volume,
            color: c.close >= c.open ? 'rgba(16, 185, 129, 0.4)' : 'rgba(239, 68, 68, 0.4)',
        })));

        let processedData = [];
        let prevHA: any = null;

        if (chartType === 'standard') {
            processedData = rawObjects;
        } else {
            for (const candle of rawObjects) {
                let haOpen, haClose, haHigh, haLow;
                if (!prevHA) {
                    haOpen = (candle.open + candle.close) / 2;
                    haClose = (candle.open + candle.high + candle.low + candle.close) / 4;
                    haHigh = candle.high;
                    haLow = candle.low;
                } else {
                    haOpen = (prevHA.open + prevHA.close) / 2;
                    haClose = (candle.open + candle.high + candle.low + candle.close) / 4;
                    haHigh = Math.max(candle.high, haOpen, haClose);
                    haLow = Math.min(candle.low, haOpen, haClose);
                }
                const haCandle: any = { time: candle.time, open: haOpen, high: haHigh, low: haLow, close: haClose };
                processedData.push(haCandle);
                prevHA = haCandle;
            }
        }

        candlestickSeriesRef.current.setData(processedData);

        lastRawCandleRef.current = rawObjects[rawObjects.length - 1];
        lastHACandleRef.current = chartType === 'heiken' ? prevHA : null;

    }, [history, chartType]);

    // Live Update
    useEffect(() => {
        if (!market || !candlestickSeriesRef.current || !lastRawCandleRef.current) return;

        const currentPrice = market.price;
        let targetRaw = { ...lastRawCandleRef.current };

        targetRaw.close = currentPrice;
        targetRaw.high = Math.max(targetRaw.high, currentPrice);
        targetRaw.low = Math.min(targetRaw.low, currentPrice);

        if (chartType === 'standard') {
            candlestickSeriesRef.current.update(targetRaw);
        } else {
            const prevHA = lastHACandleRef.current;
            const haOpen = prevHA ? prevHA.open : (targetRaw.open + targetRaw.close) / 2;
            const haClose = (targetRaw.open + targetRaw.high + targetRaw.low + targetRaw.close) / 4;
            const haHigh = Math.max(targetRaw.high, haOpen, haClose);
            const haLow = Math.min(targetRaw.low, haOpen, haClose);

            const newHACandle = { time: targetRaw.time, open: haOpen, high: haHigh, low: haLow, close: haClose };
            candlestickSeriesRef.current.update(newHACandle);
            lastHACandleRef.current = newHACandle; // Update HA ref for next tick
        }

        lastRawCandleRef.current = targetRaw; // Update raw ref

        if (market.symbol !== activeSymbol) setActiveSymbol(market.symbol);

    }, [market, activeSymbol, chartType]);

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        changeSymbol(searchInput.toUpperCase(), activeTimeframe);
        setSearchInput('');
    };

    const handleTimeframeChange = (tf: string) => {
        setActiveTimeframe(tf);
        changeSymbol(activeSymbol, tf);
    };

    const currentPrice = market?.price || 0;

    const formatVolume = (num?: number) => {
        if (!num) return '---';
        if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
        if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
        if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
        return num.toLocaleString();
    };

    return (
        <div className="w-full h-[660px] bg-slate-900/50 backdrop-blur-xl p-4 rounded-2xl border border-slate-700/50 shadow-xl flex flex-col">
            <div className="flex flex-col xl:flex-row justify-between items-start xl:items-center mb-4 gap-4 px-2">
                <div className="flex items-center gap-4 flex-wrap">
                    <div className="flex flex-col">
                        <h3 className="text-white font-bold text-lg flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                            {activeSymbol}
                        </h3>
                        <div className="flex bg-slate-800 rounded-lg p-1">
                            <button onClick={() => setChartType('standard')} className={`px-2 py-1 text-xs rounded ${chartType === 'standard' ? 'bg-blue-600 text-white' : 'text-slate-400'}`}>Standard</button>
                            <button onClick={() => setChartType('heiken')} className={`px-2 py-1 text-xs rounded ${chartType === 'heiken' ? 'bg-purple-600 text-white' : 'text-slate-400'}`}>Heiken Ashi</button>
                        </div>
                    </div>

                    <form onSubmit={handleSearch} className="flex items-center h-8 bg-slate-800 rounded-lg border border-slate-700 focus-within:border-emerald-500 transition-colors">
                        <input type="text" placeholder="Search..." value={searchInput} onChange={(e) => setSearchInput(e.target.value)} className="bg-transparent border-none text-xs text-white px-3 w-24 focus:outline-none placeholder:text-slate-500 font-mono" />
                        <button type="submit" className="px-2 h-full text-slate-400 hover:text-emerald-400"><Search className="w-3.5 h-3.5" /></button>
                    </form>
                </div>

                <div className="flex flex-col gap-2 w-full xl:w-auto">
                    <div className="flex flex-wrap justify-end gap-1">
                        {TIMEFRAMES.map(tf => (
                            <button key={tf} onClick={() => handleTimeframeChange(tf)} className={`px-2 py-1 text-[10px] font-mono rounded-md border ${activeTimeframe === tf ? 'bg-slate-700 border-slate-500 text-emerald-400 font-bold' : 'bg-transparent border-transparent text-slate-400'}`}>{tf}</button>
                        ))}
                    </div>

                    <div className="text-right">
                        <span className="text-[10px] text-slate-400 font-mono block">REAL PRICE</span>
                        <p className="text-2xl font-mono font-bold text-white">
                            ${currentPrice.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 8 })}
                        </p>
                    </div>
                </div>
            </div>

            {/* Technical Indicators Panel */}
            <div className="grid grid-cols-2 lg:grid-cols-5 gap-2 text-[10px] font-mono mb-2 bg-slate-800/20 p-2 rounded border border-slate-700/50">
                <div className="text-emerald-400 flex flex-col">
                    <span className="text-slate-500">RSI (14)</span>
                    <span className="font-bold">{indicators?.rsi ? indicators.rsi.toFixed(2) : '--'}</span>
                </div>
                <div className="text-blue-400 flex flex-col">
                    <span className="text-slate-500">EMA (20)</span>
                    <span className="font-bold">{indicators?.ema ? indicators.ema.toFixed(2) : '--'}</span>
                </div>
                <div className="text-purple-400 flex flex-col">
                    <span className="text-slate-500">MACD (12,26,9)</span>
                    <span className="font-bold">
                        {indicators?.macd ? `${indicators.macd.MACD.toFixed(2)}` : '--'}
                    </span>
                </div>
                <div className="text-orange-400 flex flex-col">
                    <span className="text-slate-500">StochRSI (14,3,3)</span>
                    <span className="font-bold">
                        {indicators?.stoch ? `K:${indicators.stoch.k.toFixed(2)} D:${indicators.stoch.d.toFixed(2)}` : '--'}
                    </span>
                </div>
                <div className="text-cyan-400 flex flex-col">
                    <span className="text-slate-500">Cloud (9,26,52)</span>
                    <span className="font-bold">
                        {indicators?.cloud ? `A:${indicators.cloud.spanA.toFixed(2)} B:${indicators.cloud.spanB.toFixed(2)}` : '--'}
                    </span>
                </div>
            </div>

            <div ref={chartContainerRef} className="w-full flex-1 rounded-lg overflow-hidden relative">
                {!isConnected && (
                    <div className="absolute inset-0 flex items-center justify-center bg-slate-900/20 z-10">
                        <div className="flex items-center gap-2 text-slate-400 animate-pulse">
                            <Activity className="w-5 h-5" />
                            <span className="text-sm font-mono">Syncing Feed...</span>
                        </div>
                    </div>
                )}
            </div>

            <div className="mt-2 flex justify-between text-[10px] text-slate-500 font-mono px-2 bg-slate-800/20 py-1 rounded">
                <span className="text-emerald-500/80">Local: {currentTime.toLocaleTimeString()}</span>
                <span>Last Data: {market?.timestamp ? new Date(market.timestamp * 1000).toLocaleTimeString() : '--:--'}</span>
                <span>Vol: {formatVolume(market?.volume)}</span>
            </div>
        </div>
    );
};

export default CandleChart;
