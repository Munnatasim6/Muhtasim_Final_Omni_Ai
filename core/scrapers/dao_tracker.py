"""
DAO & Governance Tracker Module ("Insider Signals")

This module monitors governance proposals on Snapshot.org to detect upcoming
market-moving events (e.g., Fee Switches, Token Burns, Incentives) before
they are widely known.

Dependencies:
    - gql
    - requests
"""

import logging
from typing import List, Dict, Optional
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Configure logging
logger = logging.getLogger(__name__)

# Snapshot GraphQL Endpoint
SNAPSHOT_API_URL = "https://hub.snapshot.org/graphql"

class GovernanceWatcher:
    """
    Watches DAO proposals for key governance events.
    """

    def __init__(self):
        self.transport = RequestsHTTPTransport(
            url=SNAPSHOT_API_URL,
            verify=True,
            retries=3,
        )
        self.client = Client(transport=self.transport, fetch_schema_from_transport=True)
        
        self.keywords = ["burn", "fee switch", "incentive", "buyback", "revenue share"]
        self.target_daos = ["uniswap", "aave.eth", "arbitrum-foundation.eth", "ens.eth"]

    def fetch_active_proposals(self) -> List[Dict]:
        """
        Fetches active proposals for target DAOs.

        Returns:
            List[Dict]: A list of relevant proposals.
        """
        query = gql("""
        query Proposals($space_in: [String], $state: String) {
          proposals(
            first: 20,
            skip: 0,
            where: {
              space_in: $space_in,
              state: $state
            },
            orderBy: "created",
            orderDirection: desc
          ) {
            id
            title
            body
            choices
            start
            end
            snapshot
            state
            author
            space {
              id
              name
            }
            scores
            scores_total
          }
        }
        """)

        params = {
            "space_in": self.target_daos,
            "state": "active"
        }

        try:
            logger.info("Fetching active DAO proposals...")
            result = self.client.execute(query, variable_values=params)
            return result.get("proposals", [])
        except Exception as e:
            logger.error(f"Error fetching proposals: {e}")
            return []

    def analyze_proposals(self, proposals: List[Dict]) -> List[Dict]:
        """
        Analyzes proposals for keywords and voting sentiment.

        Args:
            proposals (List[Dict]): List of proposals to analyze.

        Returns:
            List[Dict]: List of actionable signals.
        """
        signals = []

        for p in proposals:
            title = p.get("title", "").lower()
            body = p.get("body", "").lower()
            
            # Check for keywords
            matched_keyword = next((k for k in self.keywords if k in title or k in body), None)
            
            if matched_keyword:
                logger.info(f"Found relevant proposal: {p['title']} (Keyword: {matched_keyword})")
                
                # Analyze Sentiment (Voting)
                scores = p.get("scores", [])
                choices = p.get("choices", [])
                total_score = p.get("scores_total", 0)
                
                if total_score > 0:
                    # Assume choice 0 is "Yes" or "For" (Generic assumption, needs refinement per DAO)
                    # In reality, we'd check the choice text.
                    winning_choice_idx = scores.index(max(scores))
                    winning_choice = choices[winning_choice_idx]
                    
                    # Calculate dominance
                    dominance = max(scores) / total_score
                    
                    signal = {
                        "dao": p["space"]["name"],
                        "proposal": p["title"],
                        "keyword": matched_keyword,
                        "winning_choice": winning_choice,
                        "dominance": dominance,
                        "action": "WATCH"
                    }

                    if dominance > 0.90 and "burn" in matched_keyword:
                        signal["action"] = "STRONG BUY"
                    elif dominance > 0.80:
                        signal["action"] = "BUY"
                    
                    signals.append(signal)

        return signals

    def run_cycle(self):
        """
        Runs a full check cycle.
        """
        proposals = self.fetch_active_proposals()
        signals = self.analyze_proposals(proposals)
        
        for s in signals:
            logger.info(f"GOVERNANCE SIGNAL: {s}")
            # Here we would push this signal to the Swarm Manager

if __name__ == "__main__":
    watcher = GovernanceWatcher()
    watcher.run_cycle()
