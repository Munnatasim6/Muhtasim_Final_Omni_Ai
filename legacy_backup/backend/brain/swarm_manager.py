import asyncio
import logging
from typing import Dict, List, Any
import numpy as np

# Import Agents
# Assuming Trend Agent (PPO) exists in backend.brain.agents.rl_agent
try:
    from backend.brain.agents.rl_agent import DRLAgent
except ImportError:
    DRLAgent = None

# Placeholder for DQN Agent (to be implemented)
try:
    from backend.brain.agents.dqn_agent import DQNScalperAgent
except ImportError:
    DQNScalperAgent = None

# Placeholder for Risk Engine (to be implemented)
try:
    from core.risk_engine import RiskEngine
except ImportError:
    RiskEngine = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SwarmManager")

class SwarmManager:
    """
    Orchestrates multiple agents (Scalper, Trend, Risk) using a Mixture of Experts approach.
    """
    def __init__(self):
        self.agents = {}
        self.weights = {
            "scalper": 0.4,
            "trend": 0.4,
            "risk": 0.2 # Risk acts as a veto or penalty
        }
        self.risk_engine = None
        self.active_agents = []
        
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize all agents."""
        logger.info("Initializing Swarm Agents...")
        
        # 1. Scalper Agent (DQN)
        if DQNScalperAgent:
            try:
                self.agents["scalper"] = DQNScalperAgent()
                self.active_agents.append("Scalper (DQN)")
                logger.info("Scalper Agent initialized.")
            except Exception as e:
                logger.error(f"Failed to init Scalper Agent: {e}")
        
        # 2. Trend Agent (PPO)
        if DRLAgent:
            try:
                self.agents["trend"] = DRLAgent()
                self.agents["trend"].load() # Load pre-trained model
                self.active_agents.append("Trend (PPO)")
                logger.info("Trend Agent initialized.")
            except Exception as e:
                logger.error(f"Failed to init Trend Agent: {e}")

        # 3. Risk Engine
        if RiskEngine:
            try:
                self.risk_engine = RiskEngine()
                self.active_agents.append("Risk Engine")
                logger.info("Risk Engine initialized.")
            except Exception as e:
                logger.error(f"Failed to init Risk Engine: {e}")

    async def get_swarm_decision(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregates votes from all agents to make a final trading decision.
        Returns: { "action": "BUY"|"SELL"|"HOLD", "confidence": float, "details": {} }
        """
        votes = {"BUY": 0.0, "SELL": 0.0, "HOLD": 0.0}
        agent_decisions = {}

        # 1. Get Scalper Vote
        if "scalper" in self.agents:
            # Assuming scalper takes order book features
            scalper_action = self.agents["scalper"].predict(market_data.get("orderbook_features", []))
            # Map action ID to string (0: HOLD, 1: BUY, 2: SELL)
            action_map = {0: "HOLD", 1: "BUY", 2: "SELL"}
            decision = action_map.get(scalper_action, "HOLD")
            votes[decision] += self.weights["scalper"]
            agent_decisions["scalper"] = decision

        # 2. Get Trend Vote
        if "trend" in self.agents:
            # Assuming trend agent takes OHLCV data
            trend_action = self.agents["trend"].predict(market_data.get("ohlcv_features", []))
            # Map action ID to string (0: HOLD, 1: BUY, 2: SELL) - verify mapping with PPO agent
            # Assuming same mapping for now
            action_map = {0: "HOLD", 1: "BUY", 2: "SELL"}
            decision = action_map.get(trend_action, "HOLD")
            votes[decision] += self.weights["trend"]
            agent_decisions["trend"] = decision

        # 3. Risk Check (Veto Power)
        risk_veto = False
        if self.risk_engine:
            # Check VaR/CVaR
            is_risky = self.risk_engine.check_risk(market_data.get("portfolio_value", 0), market_data.get("positions", []))
            if is_risky:
                logger.warning("Risk Engine triggered VETO. Forcing HOLD/SELL.")
                risk_veto = True
                votes["BUY"] = 0.0 # Nullify buy votes
                votes["SELL"] += self.weights["risk"] # Encourage selling/reducing risk
                votes["HOLD"] += self.weights["risk"]
                agent_decisions["risk"] = "VETO"
            else:
                agent_decisions["risk"] = "PASS"

        # Final Decision Logic
        best_action = max(votes, key=votes.get)
        confidence = votes[best_action]

        # Normalize confidence roughly
        total_weight = sum(self.weights.values())
        normalized_confidence = min(confidence / total_weight, 1.0)

        logger.info(f"Swarm Decision: {best_action} (Conf: {normalized_confidence:.2f}) | Votes: {votes}")

        return {
            "action": best_action,
            "confidence": normalized_confidence,
            "agent_decisions": agent_decisions,
            "active_agents": self.active_agents
        }
