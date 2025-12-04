import numpy as np
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class OrderBookAnalyzer:
    """
    Analyzes Order Book L2/L3 data to detect micro-structure patterns.
    """
    def __init__(self):
        pass

    def calculate_obi(self, bids: List[List[float]], asks: List[List[float]]) -> float:
        """
        Calculate Order Book Imbalance (OBI).
        OBI = (Bid_Vol - Ask_Vol) / (Bid_Vol + Ask_Vol)
        Range: [-1, 1]. Positive means buy pressure, Negative means sell pressure.
        """
        try:
            # Sum top 5 levels for immediate pressure
            bid_vol = sum([float(b[1]) for b in bids[:5]])
            ask_vol = sum([float(a[1]) for a in asks[:5]])
            
            if bid_vol + ask_vol == 0:
                return 0.0
            
            obi = (bid_vol - ask_vol) / (bid_vol + ask_vol)
            return obi
        except Exception as e:
            logger.error(f"Error calculating OBI: {e}")
            return 0.0

    def detect_whale_walls(self, bids: List[List[float]], asks: List[List[float]], threshold_multiplier: float = 3.0) -> Dict[str, bool]:
        """
        Detect large "Whale Walls" (Buy/Sell Walls) that are significantly larger than average depth.
        """
        walls = {'buy_wall': False, 'sell_wall': False}
        
        try:
            # Calculate average volume per level
            avg_bid_vol = np.mean([float(b[1]) for b in bids])
            avg_ask_vol = np.mean([float(a[1]) for a in asks])
            
            # Check for outliers (Walls)
            max_bid = max([float(b[1]) for b in bids])
            max_ask = max([float(a[1]) for a in asks])
            
            if max_bid > avg_bid_vol * threshold_multiplier:
                walls['buy_wall'] = True
                logger.info(f"Whale Buy Wall Detected! Size: {max_bid}")
                
            if max_ask > avg_ask_vol * threshold_multiplier:
                walls['sell_wall'] = True
                logger.info(f"Whale Sell Wall Detected! Size: {max_ask}")
                
            return walls
        except Exception as e:
            logger.error(f"Error detecting walls: {e}")
            return walls

    def get_microstructure_features(self, order_book: Dict) -> Dict:
        """
        Extract all features for the RL Agent.
        """
        bids = order_book.get('bids', [])
        asks = order_book.get('asks', [])
        
        if not bids or not asks:
            return {}

        return {
            'obi': self.calculate_obi(bids, asks),
            'walls': self.detect_whale_walls(bids, asks),
            'spread': float(asks[0][0]) - float(bids[0][0])
        }
