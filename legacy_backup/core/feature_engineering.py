import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class FeatureEngineer:
    def __init__(self):
        pass

    def calculate_features(self, df: pd.DataFrame, on_chain_data: dict = None) -> pd.DataFrame:
        """
        Expects DataFrame with columns: ['close', 'volume']
        Optional: on_chain_data dict for 'mvrv_ratio' etc.
        """
        if df.empty:
            return df

        df = df.copy()
        
        # 1. Technical Indicators
        df['rsi'] = self.calculate_rsi(df['close'])
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['std_20'] = df['close'].rolling(window=20).std()
        df['bollinger_upper'] = df['sma_20'] + (df['std_20'] * 2)
        df['bollinger_lower'] = df['sma_20'] - (df['std_20'] * 2)

        # 2. Statistical Arbitrage Metrics (Z-Score)
        df['z_score'] = (df['close'] - df['sma_20']) / df['std_20']

        # 3. Micro-Structure: Order Flow Toxicity (Volume Imbalance)
        # Approximation using Tick Rule: if price went up, assume buy volume.
        price_change = df['close'].diff()
        
        # Vectorized calculation of Buy/Sell Volume
        # We use numpy where for speed
        buy_vol = np.where(price_change > 0, df['volume'], 0)
        sell_vol = np.where(price_change < 0, df['volume'], 0)
        
        # Rolling sum for a period (e.g., 5 candles) to get a flow metric, or just instantaneous
        # The user asked for (BuyVol - SellVol) / TotalVol. We'll do it on a rolling basis to be less noisy.
        rolling_window = 5
        buy_vol_roll = pd.Series(buy_vol).rolling(window=rolling_window).sum()
        sell_vol_roll = pd.Series(sell_vol).rolling(window=rolling_window).sum()
        total_vol_roll = df['volume'].rolling(window=rolling_window).sum()
        
        # Avoid division by zero
        df['order_flow_toxicity'] = (buy_vol_roll - sell_vol_roll) / total_vol_roll.replace(0, 1)
        df['order_flow_toxicity'] = df['order_flow_toxicity'].fillna(0)

        # 4. On-Chain Metrics
        # If external data is provided, use it. Otherwise, use a default or fetch.
        if on_chain_data and 'mvrv_ratio' in on_chain_data:
            df['mvrv_ratio'] = on_chain_data['mvrv_ratio']
        else:
            # In a real production system, this would be a Redis call or API fetch
            # For now, we provide the structure to accept it.
            # Defaulting to neutral 1.0 if not available to avoid breaking models
            df['mvrv_ratio'] = 1.0 

        return df.dropna()

    def calculate_rsi(self, series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
