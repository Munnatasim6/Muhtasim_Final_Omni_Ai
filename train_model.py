import ccxt
import pandas as pd
import numpy as np
import os
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from gym import spaces
import gym
import logging
from core.feature_engineering import FeatureEngineer

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Trainer")

class CryptoTradingEnv(gym.Env):
    """
    Custom Environment that follows gym interface.
    This is a simplified environment for training the PPO agent.
    """
    metadata = {'render.modes': ['human']}

    def __init__(self, df):
        super(CryptoTradingEnv, self).__init__()
        self.df = df
        self.current_step = 0
        self.max_steps = len(df) - 1
        
        # Actions: 0=Hold, 1=Buy, 2=Sell
        self.action_space = spaces.Discrete(3)
        
        # Observation: Feature vector (columns of df)
        # We assume all columns are numeric features
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(len(df.columns),), dtype=np.float32
        )

    def reset(self):
        self.current_step = 0
        return self.df.iloc[self.current_step].values.astype(np.float32)

    def step(self, action):
        self.current_step += 1
        done = self.current_step >= self.max_steps
        
        obs = self.df.iloc[self.current_step].values.astype(np.float32)
        
        # Reward Logic (Simplified)
        # In a real scenario, we track PnL, position, fees, etc.
        # Here we just reward if price went up and we bought, or down and we sold.
        current_price = self.df.iloc[self.current_step]['close']
        prev_price = self.df.iloc[self.current_step - 1]['close']
        price_change = (current_price - prev_price) / prev_price
        
        reward = 0
        if action == 1: # Buy
            reward = price_change * 100
        elif action == 2: # Sell
            reward = -price_change * 100
        else: # Hold
            reward = 0 # or small penalty to encourage activity
            
        return obs, reward, done, {}

    def render(self, mode='human', close=False):
        pass

def fetch_data(symbol='BTC/USDT', timeframe='1h', limit=1000):
    logger.info(f"Fetching {limit} candles for {symbol}...")
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def train():
    # 1. Fetch Data
    try:
        df = fetch_data()
    except Exception as e:
        logger.error(f"Failed to fetch data: {e}")
        return

    # 2. Feature Engineering
    logger.info("Generating features...")
    fe = FeatureEngineer()
    df = fe.calculate_features(df)
    
    # Drop non-feature columns for training (keep only numeric features)
    # We drop timestamp. We keep close/volume as they are features too.
    train_df = df.drop(columns=['timestamp'])
    
    # 3. Create Environment
    env = DummyVecEnv([lambda: CryptoTradingEnv(train_df)])
    
    # 4. Train Model
    logger.info("Starting PPO Training...")
    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=10000)
    
    # 5. Save Model
    os.makedirs("models", exist_ok=True)
    model_path = "models/ppo_agent"
    model.save(model_path)
    logger.info(f"Model saved to {model_path}.zip")

if __name__ == "__main__":
    train()
