import { useState, useEffect, useRef } from 'react';
import { MarketData } from './useTradeStream';

export const useFixedTicker = (symbol: string = 'BTC/USDT', url: string = 'ws://localhost:8000/ws') => {
    const [ticker, setTicker] = useState<MarketData | null>(null);
    const [isConnected, setIsConnected] = useState(false);
    const ws = useRef<WebSocket | null>(null);

    useEffect(() => {
        ws.current = new WebSocket(url);

        ws.current.onopen = () => {
            console.log(`✅ Ticker Connected (${symbol})`);
            setIsConnected(true);
            ws.current?.send(JSON.stringify({
                type: 'SUBSCRIBE',
                symbol: symbol,
                timeframe: '1m' // Ticker updates are independent of timeframe usually, but API needs it
            }));
        };

        ws.current.onmessage = (event) => {
            try {
                const payload = JSON.parse(event.data);
                if (payload.channel === 'market') {
                    // Only update if symbol matches (though backend sends what we subbed)
                    if (payload.data.symbol === symbol) {
                        setTicker(payload.data);
                    }
                }
            } catch (error) {
                console.error('Ticker Parse Error:', error);
            }
        };

        ws.current.onclose = () => {
            setIsConnected(false);
        };

        return () => {
            if (ws.current) ws.current.close();
        };
    }, [url, symbol]);

    return { ticker, isConnected };
};
