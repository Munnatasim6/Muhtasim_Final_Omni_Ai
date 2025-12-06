import logging
import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional

logger = logging.getLogger("MacroCorrelator")

class MacroCorrelator:
    """
    Global Macro-Economic Correlation Engine.
    Fetches data for S&P500, Gold, DXY, and Bond Yields to calculate correlations with Crypto assets.
    """
    def __init__(self, crypto_symbol: str = "BTC-USD"):
        self.crypto_symbol = crypto_symbol
        self.macro_symbols = {
            "SP500": "SPY",
            "Gold": "GLD",
            "DXY": "DX-Y.NYB",
            "10Y_Treasury": "^TNX"
        }
        self.data_cache = pd.DataFrame()

    async def fetch_macro_data(self, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
        """
        Fetches historical data for macro assets and the target crypto asset.
        """
        logger.info(f"Fetching macro data for {list(self.macro_symbols.keys())} and {self.crypto_symbol}...")
        
        tickers = list(self.macro_symbols.values()) + [self.crypto_symbol]
        try:
            data = yf.download(tickers, period=period, interval=interval, progress=False)['Close']
            
            # Rename columns for clarity
            rename_map = {v: k for k, v in self.macro_symbols.items()}
            rename_map[self.crypto_symbol] = "Crypto"
            data = data.rename(columns=rename_map)
            
            self.data_cache = data
            return data
        except Exception as e:
            logger.error(f"Failed to fetch macro data: {e}")
            return pd.DataFrame()

    def calculate_correlations(self) -> Dict[str, float]:
        """
        Calculates the rolling correlation matrix between Crypto and Macro assets.
        Returns a dictionary of correlation coefficients.
        """
        if self.data_cache.empty:
            logger.warning("No data to calculate correlations. Fetch data first.")
            return {}

        logger.info("Calculating macro correlations...")
        correlations = {}
        
        # Calculate correlation of Crypto with each macro asset
        for asset in self.macro_symbols.keys():
            if asset in self.data_cache.columns and "Crypto" in self.data_cache.columns:
                corr = self.data_cache["Crypto"].corr(self.data_cache[asset])
                correlations[asset] = round(corr, 4)
        
        logger.info(f"Correlations: {correlations}")
        return correlations

    def analyze_risk_regime(self, correlations: Dict[str, float]) -> str:
        """
        Determines the current risk regime based on correlations.
        Example: If BTC is inversely correlated to DXY, it might be a 'Risk-On' environment.
        """
        dxy_corr = correlations.get("DXY", 0)
        sp500_corr = correlations.get("SP500", 0)
        
        if dxy_corr < -0.5 and sp500_corr > 0.5:
            return "RISK_ON"
        elif dxy_corr > 0.5 and sp500_corr < -0.5:
            return "RISK_OFF"
        else:
            return "NEUTRAL"
