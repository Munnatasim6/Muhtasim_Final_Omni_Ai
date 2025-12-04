import gymnasium as gym
from gymnasium import spaces
import numpy as np
import os
from stable_baselines3 import DQN
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DQNScalperAgent")

class DQNScalperAgent:
    """
    Deep Q-Network (DQN) Agent for Scalping.
    Excels at discrete action spaces (Buy/Sell) in short timeframes.
    """
    def __init__(self, model_path: str = "dqn_scalper_model"):
        self.model_path = model_path
        self.model = None
        self.observation_space_size = 10 # Example: 5 levels of bid/ask spread + imbalance
        self.action_space_size = 3 # 0: Hold, 1: Buy, 2: Sell
        
        # Initialize model (load if exists, else create new)
        self._initialize_model()

    def _initialize_model(self):
        if os.path.exists(self.model_path + ".zip"):
            logger.info(f"Loading existing DQN model from {self.model_path}...")
            self.model = DQN.load(self.model_path)
        else:
            logger.info("No existing model found. Creating a new DQN model...")
            # Create a dummy environment to initialize the model structure
            # In production, you would train this offline first.
            env = DummyScalperEnv(self.observation_space_size)
            self.model = DQN("MlpPolicy", env, verbose=1)
            # Save immediately to have a base model
            self.model.save(self.model_path)

    def train(self, env, total_timesteps=10000):
        """
        Train the agent on a given environment.
        """
        logger.info(f"Training DQN Agent for {total_timesteps} steps...")
        self.model.set_env(env)
        self.model.learn(total_timesteps=total_timesteps)
        self.model.save(self.model_path)
        logger.info("Training complete and model saved.")

    def predict(self, observation):
        """
        Predict action based on observation (OrderBook features).
        """
        if self.model:
            # Ensure observation is numpy array and correct shape
            obs = np.array(observation).reshape(1, -1)
            action, _states = self.model.predict(obs, deterministic=True)
            return int(action)
        else:
            logger.error("Model not initialized.")
            return 0 # Default to Hold

class DummyScalperEnv(gym.Env):
    """
    Dummy Environment for initializing DQN model structure.
    """
    def __init__(self, obs_size):
        super(DummyScalperEnv, self).__init__()
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(obs_size,), dtype=np.float32)
        self.action_space = spaces.Discrete(3)

    def reset(self, seed=None, options=None):
        return np.zeros(self.observation_space.shape), {}

    def step(self, action):
        return np.zeros(self.observation_space.shape), 0, False, False, {}
