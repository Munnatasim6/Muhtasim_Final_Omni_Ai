import logging
import yfinance as yf
import pandas as pd
import tempfile
import os
from typing import Dict, List, Optional

logger = logging.getLogger("MacroCorrelator")

class MacroCorrelator:
    """
    Global Macro-Economic Correlation Engine.
    Fetches data for S&P500, Gold, DXY, and Bond Yields.
    """
    def __init__(self, crypto_symbol: str = "BTC-USD"):
        # Fix for Docker Permission Issue with yFinance
        try:
            cache_dir = os.path.join(tempfile.gettempdir(), "py-yfinance")
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir, exist_ok=True)
            yf.set_tz_cache_location(cache_dir)
        except Exception as e:
            logger.warning(f"Could not set yfinance cache: {e}")

        self.crypto_symbol = crypto_symbol
        self.macro_symbols = {
            "SP500": "SPY",
            "Gold": "GLD",
            "DXY": "DX-Y.NYB",
            "10Y_Treasury": "^TNX"
        }
        self.data_cache = pd.DataFrame()

    async def fetch_macro_data(self, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
        logger.info(f"Fetching macro data for {list(self.macro_symbols.keys())}...")
        
        tickers = list(self.macro_symbols.values()) + [self.crypto_symbol]
        try:
            # Auto_adjust=True is now default, explicit call helps avoid warnings
            data = yf.download(tickers, period=period, interval=interval, progress=False, auto_adjust=True)['Close']
            
            rename_map = {v: k for k, v in self.macro_symbols.items()}
            rename_map[self.crypto_symbol] = "Crypto"
            data = data.rename(columns=rename_map)
            
            self.data_cache = data
            return data
        except Exception as e:
            logger.error(f"Failed to fetch macro data: {e}")
            return pd.DataFrame()

    def calculate_correlations(self) -> Dict[str, float]:
        if self.data_cache.empty:
            return {}

        logger.info("Calculating macro correlations...")
        correlations = {}
        for asset in self.macro_symbols.keys():
            if asset in self.data_cache.columns and "Crypto" in self.data_cache.columns:
                corr = self.data_cache["Crypto"].corr(self.data_cache[asset])
                correlations[asset] = round(corr, 4)
        
        logger.info(f"Correlations: {correlations}")
        return correlations

    def analyze_risk_regime(self, correlations: Dict[str, float]) -> str:
        dxy_corr = correlations.get("DXY", 0)
        sp500_corr = correlations.get("SP500", 0)
        
        if dxy_corr < -0.5 and sp500_corr > 0.5:
            return "RISK_ON"
        elif dxy_corr > 0.5 and sp500_corr < -0.5:
            return "RISK_OFF"
        else:
            return "NEUTRAL"
