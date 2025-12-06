import logging
import asyncio
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

logger = logging.getLogger("OmniTrade.GraphLiquidity")

class GraphLiquidityAnalyzer:
    def __init__(self):
        # Uniswap V3 Subgraph URL (Free Public Endpoint)
        self.url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"
        
        self.query = gql("""
        query GetPools {
          pools(first: 5, orderBy: totalValueLockedUSD, orderDirection: desc) {
            id
            token0 { symbol }
            token1 { symbol }
            totalValueLockedUSD
            liquidity
          }
        }
        """)

    async def analyze_pools(self):
        """
        Query The Graph for liquidity health.
        """
        try:
            transport = AIOHTTPTransport(url=self.url)
            async with Client(transport=transport, fetch_schema_from_transport=True) as client:
                result = await client.execute(self.query)
                
                for pool in result['pools']:
                    tvl = float(pool['totalValueLockedUSD'])
                    pair = f"{pool['token0']['symbol']}-{pool['token1']['symbol']}"
                    
                    # Logic: Rug Pull Detection
                    # If TVL was X yesterday and now is X * 0.5 (50% drop), ALERT.
                    # (Here we just log the current state as a base)
                    
                    if tvl > 1_000_000:
                        logger.info(f"💧 DEEP LIQUIDITY: {pair} has ${tvl:,.2f} TVL. Healthy.")
                    else:
                        logger.warning(f"⚠️ LOW LIQUIDITY RISK: {pair} TVL is low.")

        except Exception as e:
            logger.error(f"The Graph Query Failed: {e}")

    async def run_cycle(self):
        logger.info("Analyzing DEX Liquidity via The Graph...")
        await self.analyze_pools()
