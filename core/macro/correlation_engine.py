import logging
import yfinance as yf
import pandas as pd
import asyncio

logger = logging.getLogger("OmniTrade.MacroMatrix")

class CorrelationEngine:
    def __init__(self):
        # Tickers: BTC-USD, S&P500 (SPY), Gold (GLD), Dollar Index (DX-Y.NYB)
        self.tickers = ["BTC-USD", "SPY", "GLD", "DX-Y.NYB"]
        self.period = "3mo" # 3 Months rolling correlation

    async def analyze_correlations(self):
        """
        Calculates Pearson Correlation Matrix.
        Logic: Check if BTC behaves like Risk-On (Stocks) or Safe Haven (Gold).
        """
        try:
            # Run blocking IO in executor
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, self._fetch_and_calc)
            
            if data is not None:
                self._generate_signals(data)
                
        except Exception as e:
            logger.error(f"Correlation Engine Error: {e}")

    def _fetch_and_calc(self):
        # Fetch data
        df = yf.download(self.tickers, period=self.period, interval="1d", progress=False)['Close']
        if df.empty:
            return None
        
        # Calculate Correlation
        corr_matrix = df.corr(method='pearson')
        return corr_matrix

    def _generate_signals(self, matrix):
        """
        Logic: 
        If DXY (Dollar) is Rising AND BTC has Strong Negative Correlation (<-0.7) 
        -> SELL/SHORT BTC.
        """
        try:
            # Get Correlation between BTC and DXY
            # Note: Ticker names might vary slightly in yfinance columns, adjusting index lookup
            btc_col = [c for c in matrix.columns if "BTC" in c][0]
            dxy_col = [c for c in matrix.columns if "DX" in c][0]
            
            btc_dxy_corr = matrix.loc[btc_col, dxy_col]
            
            logger.info(f"Macro Matrix: BTC vs DXY Correlation = {btc_dxy_corr:.2f}")
            
            # IMPLEMENTING YOUR SPECIFIC SIGNAL LOGIC:
            if btc_dxy_corr < -0.7:
                logger.warning("⚠️ MACRO DANGER: Strong Negative Correlation with DXY.")
                logger.warning("-> If Dollar breaks out, BTC will likely CRASH. Recommendation: HEDGE/SHORT.")
                
        except Exception as e:
            logger.error(f"Signal Generation Error: {e}")

    async def run_cycle(self):
        await self.analyze_correlations()
