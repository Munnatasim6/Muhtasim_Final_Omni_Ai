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
    status: string;
    cpu_usage: number;
    ram_usage: number;
    risk_level: string;
    uptime: string;
}

interface MultiChannelData {
    market: MarketData | null;
    brain: BrainData | null;
    system: SystemData | null;
    logs: string[]; // লগ টার্মিনালের জন্য
    isConnected: boolean;
}

export const useTradeStream = (url: string = 'ws://localhost:8000/ws'): MultiChannelData => {
    const [market, setMarket] = useState<MarketData | null>(null);
    const [brain, setBrain] = useState<BrainData | null>(null);
    const [system, setSystem] = useState<SystemData | null>(null);
    const [logs, setLogs] = useState<string[]>([]);
    const [isConnected, setIsConnected] = useState(false);

    const ws = useRef<WebSocket | null>(null);

    useEffect(() => {
        ws.current = new WebSocket(url);

        ws.current.onopen = () => {
            console.log('✅ WebSocket Connected');
            setIsConnected(true);
            addLog('System connected to Neural Core via WebSocket.');
        };

        ws.current.onmessage = (event) => {
            try {
                const payload = JSON.parse(event.data);

                switch (payload.channel) {
                    case 'market':
                        setMarket(payload.data);
                        break;
                    case 'brain':
                        setBrain(payload.data);
                        // ব্রেইনের সিদ্ধান্ত লগে যোগ করা
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

    // লগ ম্যানেজমেন্ট (সর্বশেষ ৫০টি লগ রাখা)
    const addLog = (message: string) => {
        const timestamp = new Date().toLocaleTimeString();
        setLogs(prev => [`[${timestamp}] ${message}`, ...prev].slice(0, 50));
    };

    return { market, brain, system, logs, isConnected };
};
