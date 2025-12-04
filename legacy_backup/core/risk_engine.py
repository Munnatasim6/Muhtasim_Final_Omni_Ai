import numpy as np
from scipy.stats import norm
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RiskEngine")

class RiskEngine:
    """
    Advanced Risk Engine calculating VaR (Value at Risk) and CVaR (Conditional VaR).
    Acts as a gatekeeper for all trades.
    """
    def __init__(self, confidence_level: float = 0.95, max_drawdown_limit: float = 0.02):
        self.confidence_level = confidence_level
        self.max_drawdown_limit = max_drawdown_limit # 2% max drawdown allowed per trade/day

    def calculate_var(self, returns: List[float], method: str = "historical") -> float:
        """
        Calculate Value at Risk (VaR).
        """
        if not returns:
            return 0.0

        if method == "historical":
            # Historical Simulation
            var = np.percentile(returns, (1 - self.confidence_level) * 100)
            return abs(var)
        
        elif method == "parametric":
            # Parametric (Variance-Covariance)
            mu = np.mean(returns)
            sigma = np.std(returns)
            var = norm.ppf(1 - self.confidence_level, mu, sigma)
            return abs(var)
        
        return 0.0

    def calculate_cvar(self, returns: List[float]) -> float:
        """
        Calculate Conditional Value at Risk (CVaR) / Expected Shortfall.
        """
        if not returns:
            return 0.0
            
        var = self.calculate_var(returns, method="historical")
        # CVaR is the average of losses exceeding VaR
        losses = [r for r in returns if r < -var]
        if not losses:
            return var
        return abs(np.mean(losses))

    def check_risk(self, portfolio_value: float, positions: List[Dict], historical_returns: List[float] = None) -> bool:
        """
        Check if the current state allows for a new trade.
        Returns True if Risk is too high (VETO), False otherwise.
        """
        # 1. Check Max Drawdown
        # This would typically track peak equity, here we simplify
        # Assuming we get historical returns passed in or we mock them
        if not historical_returns:
            # Mock returns if not provided (e.g. for initial testing)
            historical_returns = np.random.normal(0.001, 0.02, 100).tolist()

        var = self.calculate_var(historical_returns)
        cvar = self.calculate_cvar(historical_returns)

        logger.info(f"Risk Assessment: VaR={var:.4f}, CVaR={cvar:.4f}")

        # If potential loss (VaR) exceeds limit relative to portfolio
        # e.g. if VaR is > 2% of portfolio
        if var > self.max_drawdown_limit:
            logger.warning(f"Risk VETO: VaR ({var:.2%}) exceeds limit ({self.max_drawdown_limit:.2%})")
            return True # Risk is HIGH

        return False # Risk is ACCEPTABLE
