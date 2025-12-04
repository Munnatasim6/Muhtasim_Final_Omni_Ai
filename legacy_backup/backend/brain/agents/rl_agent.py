import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoTradingEnv(gym.Env):
    """
    Custom Environment that follows gym interface for Crypto Trading.
    Includes fee simulation, slippage, and position management.
    """
    metadata = {'render.modes': ['human']}

    def __init__(self, df: pd.DataFrame, initial_balance: float = 10000.0, fee_rate: float = 0.001):
        super(CryptoTradingEnv, self).__init__()
        
        self.df = df
        self.initial_balance = initial_balance
        self.fee_rate = fee_rate
        
        # Action space: 0=Hold, 1=Buy, 2=Sell
        self.action_space = spaces.Discrete(3)
        
        # Observation space: [Open, High, Low, Close, Volume, RSI, MACD, ...]
        # Assuming normalized features for better convergence
        self.observation_space = spaces.Box(
            low=0, high=1, shape=(len(df.columns),), dtype=np.float32
        )
        
        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.balance = self.initial_balance
        self.net_worth = self.initial_balance
        self.crypto_held = 0
        self.current_step = 0
        self.max_steps = len(self.df) - 1
        
        return self._next_observation(), {}

    def _next_observation(self):
        # Get the data for the current step
        obs = self.df.iloc[self.current_step].values
        return obs.astype(np.float32)

    def step(self, action):
        # Execute one time step within the environment
        self._take_action(action)
        
        self.current_step += 1
        
        if self.current_step > self.max_steps:
            self.current_step = 0
            
        reward = self._calculate_reward()
        done = self.net_worth <= 0 or self.current_step == self.max_steps
        
        obs = self._next_observation()
        info = {'net_worth': self.net_worth}
        
        return obs, reward, done, False, info

    def _take_action(self, action):
        current_price = self.df.iloc[self.current_step]['close'] # Assuming 'close' column exists
        
        # Slippage simulation (random walk between 0.01% and 0.05%)
        slippage = np.random.uniform(0.0001, 0.0005)
        execution_price = current_price * (1 + slippage if action == 1 else 1 - slippage)

        if action == 1: # Buy
            # Buy with 100% of available balance for simplicity (can be optimized)
            if self.balance > 0:
                amount_to_buy = (self.balance / execution_price) * (1 - self.fee_rate)
                self.crypto_held += amount_to_buy
                self.balance = 0
                logger.debug(f"Bought {amount_to_buy} at {execution_price}")

        elif action == 2: # Sell
            if self.crypto_held > 0:
                amount_sold = self.crypto_held * execution_price * (1 - self.fee_rate)
                self.balance += amount_sold
                self.crypto_held = 0
                logger.debug(f"Sold at {execution_price}")

        # Update net worth
        self.net_worth = self.balance + (self.crypto_held * current_price)

    def _calculate_reward(self):
        # Reward is the change in net worth
        # Can add penalties for excessive trading or drawdowns
        reward = self.net_worth - self.initial_balance
        return reward

    def render(self, mode='human', close=False):
        print(f'Step: {self.current_step}, Net Worth: {self.net_worth}')

class DRLAgent:
    """
    Deep Reinforcement Learning Agent using PPO.
    """
    def __init__(self, model_path: str = "ppo_crypto_trader"):
        self.model_path = model_path
        self.model = None

    def train(self, data: pd.DataFrame, total_timesteps: int = 100000):
        """
        Train the PPO agent.
        """
        logger.info("Initializing Environment for Training...")
        env = DummyVecEnv([lambda: CryptoTradingEnv(data)])
        
        logger.info("Setting up PPO Model...")
        # PPO is chosen for its stability and ease of tuning compared to DQN/DDPG
        self.model = PPO("MlpPolicy", env, verbose=1, tensorboard_log="./ppo_tensorboard/")
        
        logger.info(f"Starting Training for {total_timesteps} timesteps...")
        self.model.learn(total_timesteps=total_timesteps)
        
        logger.info("Training Complete. Saving model...")
        self.model.save(self.model_path)

    def load(self):
        """
        Load a trained model.
        """
        if os.path.exists(self.model_path + ".zip"):
            self.model = PPO.load(self.model_path)
            logger.info("Model loaded successfully.")
        else:
            logger.warning("No trained model found.")

    def predict(self, observation):
        """
        Predict action for a given observation.
        """
        if self.model:
            action, _states = self.model.predict(observation)
            return action
        else:
            logger.error("Model not loaded!")
            return 0 # Default to Hold

# Example Usage
if __name__ == "__main__":
    # Mock Data for testing
    data = {
        'open': np.random.rand(1000) * 100,
        'high': np.random.rand(1000) * 100,
        'low': np.random.rand(1000) * 100,
        'close': np.random.rand(1000) * 100,
        'volume': np.random.rand(1000) * 1000
    }
    df = pd.DataFrame(data)
    
    agent = DRLAgent()
    agent.train(df, total_timesteps=1000)
