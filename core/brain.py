import logging
import numpy as np
import pandas as pd
# import shap # Commented out to avoid import error if not installed, but architecture is ready
from stable_baselines3 import PPO
import os

logger = logging.getLogger(__name__)

class Brain:
    def __init__(self, model_path="models/ppo_agent"):
        self.model_path = model_path
        self.model = None
        self.load_model()

    def load_model(self):
        if os.path.exists(self.model_path + ".zip"):
            try:
                self.model = PPO.load(self.model_path)
                logger.info("Loaded PPO Model")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
        else:
            logger.warning("No model found. Running in Random/Heuristic mode.")

    def predict(self, features: pd.DataFrame):
        """
        Returns action: 0 (Hold), 1 (Buy), 2 (Sell)
        """
        if self.model:
            # Ensure input matches training shape (drop timestamp if present)
            obs = features.iloc[-1].copy()
            if 'timestamp' in obs:
                obs = obs.drop('timestamp')
            
            # Reshape for model (1, n_features)
            obs_array = obs.values.reshape(1, -1)
            
            action, _states = self.model.predict(obs_array)
            return int(action[0])
        else:
            # Fallback: Simple Heuristic
            last_row = features.iloc[-1]
            if last_row['rsi'] < 30:
                return 1 # Buy
            elif last_row['rsi'] > 70:
                return 2 # Sell
            return 0 # Hold

    def explain_decision(self, features: pd.DataFrame):
        """
        Returns SHAP values or text explanation.
        """
        # Mock XAI for now
        last_row = features.iloc[-1]
        explanation = {
            "reason": "Unknown",
            "confidence": 0.85
        }
        
        if last_row['rsi'] < 30:
            explanation["reason"] = f"RSI is oversold ({last_row['rsi']:.2f})"
        elif last_row['rsi'] > 70:
            explanation["reason"] = f"RSI is overbought ({last_row['rsi']:.2f})"
        
        if last_row['z_score'] > 2:
             explanation["reason"] += f" & Price deviation high (Z={last_row['z_score']:.2f})"

        return explanation
