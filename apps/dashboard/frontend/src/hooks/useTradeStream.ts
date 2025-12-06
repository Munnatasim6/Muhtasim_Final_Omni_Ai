import { useState, useEffect, useRef } from 'react';

export interface MarketData {
    symbol: string;
    price: number;
    volume: number;
    timestamp: number;
}

export interface BrainData {
    action: string;
    confidence: number;
    reason: string;
    risk_status: string;
    active_agents: string[];
}

export interface SystemData {
    status: 'ONLINE' | 'OFFLINE';
    cpu_usage: number;
    ram_usage: number;
    risk_level: string;
    uptime: string;
    ai_quota: number;
    ai_quota_max: number;
}

interface MultiChannelData {
    market: MarketData | null;
    brain: BrainData | null;
    system: SystemData | null;
    logs: string[];
    history: any[]; // OHLCV History
    isConnected: boolean;
    changeSymbol: (symbol: string, timeframe?: string) => void;
}

export const useTradeStream = (url: string = 'ws://localhost:8000/ws'): MultiChannelData => {
    const [market, setMarket] = useState<MarketData | null>(null);
    const [brain, setBrain] = useState<BrainData | null>(null);
    const [system, setSystem] = useState<SystemData | null>(null);
    const [history, setHistory] = useState<any[]>([]);
    const [logs, setLogs] = useState<string[]>([]);
    const [isConnected, setIsConnected] = useState(false);

    const ws = useRef<WebSocket | null>(null);
    const lastSymbol = useRef<string>("BTC/USDT");
    const lastTimeframe = useRef<string>("1m");

    useEffect(() => {
        ws.current = new WebSocket(url);

        ws.current.onopen = () => {
            console.log('✅ WebSocket Connected');
            setIsConnected(true);
            addLog('System connected to Neural Core via WebSocket.');
            // Resubscribe if needed
            if (lastSymbol.current) {
                // Initial sub
                ws.current?.send(JSON.stringify({
                    type: 'SUBSCRIBE',
                    symbol: lastSymbol.current,
                    timeframe: lastTimeframe.current
                }));
            }
        };

        ws.current.onmessage = (event) => {
            try {
                const payload = JSON.parse(event.data);

                switch (payload.channel) {
                    case 'market':
                        setMarket(payload.data);
                        break;
                    case 'candle_history':
                        // Received [timestamp, open, high, low, close, volume] list
                        setHistory(payload.data);
                        break;
                    case 'brain':
                        setBrain(payload.data);
                        if (payload.data.action !== 'HOLD') {
                            addLog(`🤖 Brain Signal: ${payload.data.action} (${(payload.data.confidence * 100).toFixed(1)}%) - ${payload.data.reason}`);
                        }
                        break;
                    case 'system':
                        setSystem(payload.data);
                        break;
                    case 'alert':
                        addLog(`🚨 ALERT: ${payload.message}`);
                        break;
                    default:
                        break;
                }
            } catch (error) {
                console.error('Error parsing WS message:', error);
            }
        };

        ws.current.onclose = () => {
            console.log('❌ WebSocket Disconnected');
            setIsConnected(false);
            addLog('⚠️ Connection lost. Attempting reconnect...');
        };

        return () => {
            if (ws.current) ws.current.close();
        };
    }, [url]);

    const addLog = (message: string) => {
        const timestamp = new Date().toLocaleTimeString();
        setLogs(prev => [`[${timestamp}] ${message}`, ...prev].slice(0, 50));
    };

    const changeSymbol = (symbol: string, timeframe: string = '1m') => {
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            lastSymbol.current = symbol;
            lastTimeframe.current = timeframe;
            ws.current.send(JSON.stringify({
                type: 'SUBSCRIBE',
                symbol,
                timeframe
            }));
            addLog(`🔍 Tracking: ${symbol} [${timeframe}]`);
        }
    };

    return { market, brain, system, history, logs, isConnected, changeSymbol };
};
