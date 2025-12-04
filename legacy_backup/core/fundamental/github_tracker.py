"""
GitHub Sentinel ("Developer Activity Tracker")

This module monitors the GitHub repositories of top crypto assets to gauge
developer activity. It uses the GitHub Public API (Free Tier).

Logic:
    - High Price + Zero Commits = SCAM PUMP (Sell Signal)
    - Low Price + High Commits = UNDERVALUED (Buy Signal)

Dependencies:
    - requests
"""

import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

class GithubTracker:
    """
    Tracks developer activity on GitHub for specific repositories.
    """

    def __init__(self):
        self.base_url = "https://api.github.com"
        # Map asset symbol to GitHub repo (owner/repo)
        self.repos = {
            "ETH": "ethereum/go-ethereum",
            "SOL": "solana-labs/solana",
            "ADA": "input-output-hk/cardano-node",
            "DOT": "paritytech/polkadot",
            "AVAX": "ava-labs/avalanchego"
        }

    def get_commit_activity(self, repo_name: str) -> int:
        """
        Gets the number of commits in the last 30 days.

        Args:
            repo_name (str): "owner/repo" string.

        Returns:
            int: Number of commits.
        """
        try:
            # GitHub API for commit activity stats (returns weekly stats for last year)
            # GET /repos/{owner}/{repo}/stats/commit_activity
            url = f"{self.base_url}/repos/{repo_name}/stats/commit_activity"
            
            logger.info(f"Fetching GitHub activity for {repo_name}...")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Sum the last 4 weeks (approx 30 days)
                    # Data is list of weeks, last one is most recent
                    last_4_weeks = data[-4:]
                    total_commits = sum(week['total'] for week in last_4_weeks)
                    return total_commits
            elif response.status_code == 202:
                # 202 Accepted means GitHub is computing stats, try again later
                logger.warning(f"GitHub stats computing for {repo_name}, try again later.")
                return -1
            else:
                logger.warning(f"Failed to fetch GitHub data: {response.status_code}")
                return 0
                
        except Exception as e:
            logger.error(f"Error fetching GitHub activity: {e}")
            return 0
        
        return 0

    def analyze_activity(self, price_trends: Dict[str, str]) -> Dict[str, Dict]:
        """
        Analyzes developer activity against price trends.

        Args:
            price_trends (Dict[str, str]): Map of Symbol -> Trend ("UP", "DOWN", "FLAT").

        Returns:
            Dict[str, Dict]: Analysis results per asset.
        """
        results = {}
        
        for symbol, repo in self.repos.items():
            commits = self.get_commit_activity(repo)
            trend = price_trends.get(symbol, "FLAT")
            
            signal = "NEUTRAL"
            score = 50 # Base score
            
            if commits == 0:
                if trend == "UP":
                    signal = "SCAM PUMP ALERT (Price Up, No Devs)"
                    score = 10
                else:
                    signal = "DEAD PROJECT"
                    score = 0
            elif commits > 100:
                if trend == "DOWN":
                    signal = "STRONG BUY (Price Down, High Dev Activity)"
                    score = 90
                else:
                    signal = "HEALTHY GROWTH"
                    score = 70
            
            logger.info(f"GitHub Analysis [{symbol}]: {commits} commits (30d). Signal: {signal}")
            
            results[symbol] = {
                "commits_30d": commits,
                "signal": signal,
                "score": score
            }
            
        return results

if __name__ == "__main__":
    tracker = GithubTracker()
    # Mock price trends
    mock_trends = {"ETH": "UP", "SOL": "DOWN", "ADA": "UP"}
    results = tracker.analyze_activity(mock_trends)
    print(results)
