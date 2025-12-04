"""
Stablecoin Minting Tracker ("Liquidity Injection")

This module monitors the USDT (Tether) contract on Ethereum for large minting events.
It listens for `Issue` events (or Transfer from 0x0 address) to detect fresh capital
entering the market.

Dependencies:
    - web3
"""

import logging
import time
from typing import Optional
from web3 import Web3

# Configure logging
logger = logging.getLogger(__name__)

# USDT Contract Address (Ethereum Mainnet)
USDT_ADDRESS = "0xdAC17F958D2ee523a2206206994597C13D831ec7"

# Minimal ABI for USDT (Issue event and Transfer event)
# Note: USDT uses "Issue" event for minting, but standard ERC20 uses Transfer from 0x0
USDT_ABI = [
    {
        "anonymous": False,
        "inputs": [{"indexed": True, "name": "amount", "type": "uint256"}],
        "name": "Issue",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "from", "type": "address"},
            {"indexed": True, "name": "to", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256"}
        ],
        "name": "Transfer",
        "type": "event"
    }
]

class StablecoinWatch:
    """
    Monitors Stablecoin contracts for large minting events (Whale Activity).
    """

    def __init__(self, rpc_url: str):
        """
        Initialize the StablecoinWatch.

        Args:
            rpc_url (str): The RPC URL for Ethereum Mainnet (e.g., Infura/Alchemy).
        """
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.contract = self.w3.eth.contract(address=USDT_ADDRESS, abi=USDT_ABI)
        self.whale_threshold = 10_000_000 * 10**6 # $10M USDT (6 decimals)
        
        if self.w3.is_connected():
            logger.info(f"Connected to Ethereum RPC for Stablecoin Watch")
        else:
            logger.error(f"Failed to connect to RPC: {rpc_url}")

    def check_recent_mints(self, lookback_blocks: int = 100):
        """
        Checks for minting events in the last N blocks.

        Args:
            lookback_blocks (int): Number of blocks to look back.
        """
        try:
            current_block = self.w3.eth.block_number
            from_block = current_block - lookback_blocks
            
            logger.info(f"Scanning for USDT Mints from block {from_block} to {current_block}...")
            
            # Filter for 'Issue' events (Tether specific)
            issue_filter = self.contract.events.Issue.create_filter(fromBlock=from_block, toBlock=current_block)
            issue_events = issue_filter.get_all_entries()
            
            for event in issue_events:
                amount = event['args']['amount']
                if amount >= self.whale_threshold:
                    amount_usd = amount / 10**6
                    logger.warning(f"WHALE ALERT: {amount_usd:,.0f} USDT Minted! (Bullish Signal)")
                    # Trigger Swarm Signal here
            
            # Also check Transfer from 0x0 (Standard ERC20 Mint)
            # Some stablecoins or wrapped tokens use this
            transfer_filter = self.contract.events.Transfer.create_filter(
                fromBlock=from_block, 
                toBlock=current_block,
                argument_filters={'from': "0x0000000000000000000000000000000000000000"}
            )
            transfer_events = transfer_filter.get_all_entries()
            
            for event in transfer_events:
                amount = event['args']['value']
                if amount >= self.whale_threshold:
                    amount_usd = amount / 10**6
                    logger.warning(f"WHALE ALERT: {amount_usd:,.0f} USDT Transferred from Null! (Minting)")

        except Exception as e:
            logger.error(f"Error checking stablecoin mints: {e}")

    def run_monitor(self):
        """
        Continuous monitoring loop.
        """
        while True:
            self.check_recent_mints(lookback_blocks=50)
            time.sleep(60) # Check every minute (approx 4-5 blocks)

if __name__ == "__main__":
    # Example Usage (Public RPC - might be rate limited)
    ETH_RPC = "https://eth.public-rpc.com"
    watcher = StablecoinWatch(ETH_RPC)
    watcher.check_recent_mints()
