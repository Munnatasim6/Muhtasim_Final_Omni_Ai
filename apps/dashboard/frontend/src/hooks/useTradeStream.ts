import { useState, useEffect, useRef } from 'react';

interface TradeData {
    pnl: number;
    active_agents: string[];
    signals: {
        action: string;
        confidence: number;
        agent_decisions: Record<string, string>;
    };
    timestamp: string;
}

export const useTradeStream = (url: string = 'ws://localhost:8000/ws') => {
    const [data, setData] = useState<TradeData | null>(null);
    const [isConnected, setIsConnected] = useState(false);
    const ws = useRef<WebSocket | null>(null);

    useEffect(() => {
        // Initialize WebSocket connection
        ws.current = new WebSocket(url);

        ws.current.onopen = () => {
            console.log('WebSocket Connected');
            setIsConnected(true);
        };

        ws.current.onmessage = (event) => {
            try {
                const parsedData: TradeData = JSON.parse(event.data);
                setData(parsedData);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };

        ws.current.onclose = () => {
            console.log('WebSocket Disconnected');
            setIsConnected(false);
        };

        ws.current.onerror = (error) => {
            console.error('WebSocket Error:', error);
        };

        // Cleanup on unmount
        return () => {
            if (ws.current) {
                ws.current.close();
            }
        };
    }, [url]);

    return { data, isConnected };
};
