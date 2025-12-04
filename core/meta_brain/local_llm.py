"""
Local LLM Integration Module ("The Free Brain")

This module provides an interface to a locally running Ollama instance for
autonomous reasoning, market summarization, and strategy proposal without
incurring API costs.

Prerequisites:
    1. Install Ollama: https://ollama.com/download
    2. Pull a model (e.g., Llama 3 or Mistral): `ollama pull llama3`
    3. Ensure Ollama is running on port 11434 (default).

Usage:
    generator = LocalStrategyGenerator(model="llama3")
    summary = generator.generate_market_summary("Bitcoin is up 5% due to ETF news...")
    strategy = generator.propose_strategy({"volatility": "high", "trend": "bullish"})
"""

import logging
import json
from typing import Dict, Optional
import requests
from langchain_community.llms import Ollama

# Configure logging
logger = logging.getLogger(__name__)

class LocalStrategyGenerator:
    """
    Connects to a local Ollama instance to generate market insights and trading strategies.
    """

    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434"):
        """
        Initialize the LocalStrategyGenerator.

        Args:
            model (str): The name of the model to use (e.g., "llama3", "mistral").
            base_url (str): The base URL of the Ollama instance.
        """
        self.model = model
        self.base_url = base_url
        self.llm = Ollama(model=model, base_url=base_url)
        
        # Verify connection
        if self._check_connection():
            logger.info(f"Successfully connected to local Ollama instance with model: {model}")
        else:
            logger.warning(f"Failed to connect to Ollama at {base_url}. Ensure it is running.")

    def _check_connection(self) -> bool:
        """Checks if the Ollama instance is reachable."""
        try:
            response = requests.get(self.base_url)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def generate_market_summary(self, news_text: str) -> str:
        """
        Summarizes scraped sentiment data and news text.

        Args:
            news_text (str): Raw text from news or social media.

        Returns:
            str: A concise summary of the market sentiment.
        """
        if not news_text:
            return "No news data provided."

        prompt = (
            f"Analyze the following market news and provide a concise summary "
            f"focusing on market sentiment (Bullish/Bearish/Neutral) and key drivers:\n\n"
            f"{news_text}"
        )

        try:
            logger.info("Generating market summary via Local LLM...")
            summary = self.llm.invoke(prompt)
            return summary.strip()
        except Exception as e:
            logger.error(f"Error generating market summary: {e}")
            return "Error generating summary."

    def propose_strategy(self, market_data: Dict) -> str:
        """
        Outputs Python code snippets for new trading logic based on recent market data.

        Args:
            market_data (Dict): Dictionary containing market metrics (volatility, trend, etc.).

        Returns:
            str: Python code snippet representing the proposed strategy logic.
        """
        data_str = json.dumps(market_data, indent=2)
        prompt = (
            f"You are an expert quantitative trader. Based on the following market data:\n"
            f"{data_str}\n\n"
            f"Propose a Python function `custom_strategy(df)` that implements a trading strategy "
            f"optimized for these conditions. The function should take a pandas DataFrame `df` "
            f"with OHLCV data and return a signal (1 for buy, -1 for sell, 0 for hold). "
            f"Provide ONLY the Python code, no markdown formatting or explanations."
        )

        try:
            logger.info("Proposing new trading strategy via Local LLM...")
            code_snippet = self.llm.invoke(prompt)
            
            # Clean up potential markdown formatting if the model adds it
            code_snippet = code_snippet.replace("```python", "").replace("```", "").strip()
            
            return code_snippet
        except Exception as e:
            logger.error(f"Error proposing strategy: {e}")
            return "# Error generating strategy code."

if __name__ == "__main__":
    # Example usage
    generator = LocalStrategyGenerator()
    
    # Test Summary
    sample_news = "Bitcoin surges past $70k as institutional demand grows. Inflation data comes in lower than expected."
    print("Market Summary:")
    print(generator.generate_market_summary(sample_news))
    
    # Test Strategy Proposal
    sample_data = {"volatility": "high", "trend": "uptrend", "rsi": 75}
    print("\nProposed Strategy:")
    print(generator.propose_strategy(sample_data))
