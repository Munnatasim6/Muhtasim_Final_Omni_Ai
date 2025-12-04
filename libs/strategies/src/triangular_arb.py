import asyncio
import logging
import math
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class TriangularArbitrage:
    """
    Multi-Exchange Triangular Arbitrage Strategy.
    Finds profitable paths (e.g., BTC -> ETH -> USDT -> BTC) across exchanges.
    """
    def __init__(self, exchanges: Dict):
        self.exchanges = exchanges # Dict of initialized ccxt exchanges
        self.graph = {} # Adjacency list for currency graph

    def build_graph(self, tickers: Dict):
        """
        Build a graph where nodes are currencies and edges are negative log of exchange rates.
        We use -log(rate) because Bellman-Ford finds shortest paths (min weight), 
        and we want to maximize the product of rates (max profit).
        Product(rates) > 1  <=>  Sum(-log(rates)) < 0
        """
        self.graph = {}
        for symbol, ticker in tickers.items():
            try:
                base, quote = symbol.split('/')
                price = ticker['last']
                
                if price <= 0: continue

                # Edge: Base -> Quote (Sell Base, Buy Quote)
                # Rate = price
                # Weight = -log(price)
                if base not in self.graph: self.graph[base] = []
                self.graph[base].append((quote, -math.log(price)))

                # Edge: Quote -> Base (Sell Quote, Buy Base)
                # Rate = 1 / price
                # Weight = -log(1/price) = log(price)
                if quote not in self.graph: self.graph[quote] = []
                self.graph[quote].append((base, math.log(price)))
                
            except Exception as e:
                continue

    def find_arbitrage_path(self, start_currency: str = 'USDT') -> List[str]:
        """
        Use Bellman-Ford algorithm to detect negative cycles (arbitrage opportunities).
        """
        # Initialize distances
        dist = {node: float('inf') for node in self.graph}
        predecessor = {node: None for node in self.graph}
        dist[start_currency] = 0

        # Relax edges |V| - 1 times
        nodes = list(self.graph.keys())
        for _ in range(len(nodes) - 1):
            for u in nodes:
                if u not in self.graph: continue
                for v, weight in self.graph[u]:
                    if dist[u] + weight < dist[v]:
                        dist[v] = dist[u] + weight
                        predecessor[v] = u

        # Check for negative cycles
        for u in nodes:
            if u not in self.graph: continue
            for v, weight in self.graph[u]:
                if dist[u] + weight < dist[v]:
                    # Negative cycle found! Trace back
                    logger.info("Arbitrage Opportunity Detected!")
                    path = [v, u]
                    curr = predecessor[u]
                    while curr not in path:
                        path.append(curr)
                        curr = predecessor[curr]
                    path.append(curr)
                    path.append(v) # Close the loop
                    return list(reversed(path))
        
        return []

    async def execute_arbitrage(self, path: List[str]):
        """
        Execute the trades in the arbitrage path.
        """
        logger.info(f"Executing Arbitrage Path: {path}")
        # Logic to execute trades sequentially
        # 1. Buy path[1] with path[0]
        # 2. Buy path[2] with path[1]
        # ...
        # Verify profitability after fees!
