import logging
import asyncio
from web3 import Web3

logger = logging.getLogger("OmniTrade.BridgeWatcher")

class BridgeWatcher:
    def __init__(self):
        # Using a free public RPC for Ethereum Mainnet (Cloudflare/PublicNode)
        self.rpc_url = "https://eth.merkle.io" 
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # Contract Addresses (ETH Mainnet Gateways)
        self.bridges = {
            "Arbitrum": "0x8315177aB297bA92A06054cE80a67Ed4DBd7ed3a", # Arbitrum One Bridge
            "Optimism": "0x99C9fc46f92E8a1c0dEC1b1747d7109ca542c038"  # Optimism Portal
        }
        
        self.last_balances = {}

    async def monitor_inflow(self):
        """
        Monitors ETH balance of bridge contracts.
        Significant increase = Money flowing INTO L2 = Bullish for L2 Tokens.
        """
        if not self.w3.is_connected():
            logger.warning("Web3 RPC not connected. Retrying...")
            return

        for chain, address in self.bridges.items():
            try:
                # Run sync web3 call in executor to not block async loop
                loop = asyncio.get_event_loop()
                balance_wei = await loop.run_in_executor(None, self.w3.eth.get_balance, address)
                balance_eth = self.w3.from_wei(balance_wei, 'ether')
                
                prev_balance = self.last_balances.get(chain, balance_eth)
                delta = balance_eth - prev_balance
                
                # Logic: If > 1000 ETH flows in within check interval
                if delta > 1000:
                    logger.warning(f"🚀 BRIDGE ALERT: {chain} Inflow Detected!")
                    logger.warning(f"Amount: {delta:.2f} ETH. Signal: {chain.upper()} ROTATION SEASON.")
                
                self.last_balances[chain] = balance_eth
                logger.info(f"Bridge Status [{chain}]: {balance_eth:.2f} ETH (Delta: {delta:.4f})")

            except Exception as e:
                logger.error(f"Error monitoring {chain} bridge: {e}")

    async def run_cycle(self):
        """Polls every 60 seconds."""
        while True:
            await self.monitor_inflow()
            await asyncio.sleep(60)
