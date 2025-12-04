import asyncio
import logging
from typing import Dict, List, Optional
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentEngine:
    """
    Advanced Sentiment Analysis Engine using FinBERT.
    Provides asynchronous, context-aware sentiment scoring for financial text.
    """

    def __init__(self, model_name: str = "ProsusAI/finbert"):
        """
        Initialize the SentimentEngine with a specific transformer model.
        
        Args:
            model_name (str): The Hugging Face model hub name for FinBERT or similar.
        """
        self.device = 0 if torch.cuda.is_available() else -1
        logger.info(f"Initializing SentimentEngine with model: {model_name} on device: {self.device}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.pipeline = pipeline(
                "sentiment-analysis", 
                model=self.model, 
                tokenizer=self.tokenizer, 
                device=self.device,
                return_all_scores=True
            )
            logger.info("SentimentEngine initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize SentimentEngine: {e}")
            raise

    async def analyze_text(self, text: str) -> Dict[str, float]:
        """
        Analyze the sentiment of a single text string asynchronously.

        Args:
            text (str): The text to analyze (e.g., news headline, tweet).

        Returns:
            Dict[str, float]: A dictionary containing probabilities for 'positive', 'negative', and 'neutral'.
        """
        if not text:
            return {"positive": 0.0, "negative": 0.0, "neutral": 0.0}

        try:
            # Run the blocking pipeline call in a separate thread to avoid blocking the event loop
            loop = asyncio.get_running_loop()
            results = await loop.run_in_executor(None, self._predict, text)
            
            # Parse results from FinBERT (labels: positive, negative, neutral)
            # Structure: [[{'label': 'positive', 'score': 0.9}, ...]]
            scores = {item['label']: item['score'] for item in results[0]}
            
            return scores
        except Exception as e:
            logger.error(f"Error analyzing text: {text[:50]}... - {e}")
            return {"positive": 0.0, "negative": 0.0, "neutral": 0.0}

    def _predict(self, text: str):
        """Helper method to run the pipeline synchronously."""
        return self.pipeline(text)

    async def analyze_batch(self, texts: List[str]) -> List[Dict[str, float]]:
        """
        Analyze sentiment for a batch of texts.

        Args:
            texts (List[str]): List of texts to analyze.

        Returns:
            List[Dict[str, float]]: List of sentiment score dictionaries.
        """
        tasks = [self.analyze_text(text) for text in texts]
        return await asyncio.gather(*tasks)

    async def get_aggregate_sentiment(self, texts: List[str]) -> Dict[str, float]:
        """
        Calculate the average sentiment scores for a collection of texts.

        Args:
            texts (List[str]): List of texts.

        Returns:
            Dict[str, float]: Aggregated sentiment scores.
        """
        if not texts:
            return {"positive": 0.0, "negative": 0.0, "neutral": 0.0}

        results = await self.analyze_batch(texts)
        
        total_positive = sum(r.get('positive', 0) for r in results)
        total_negative = sum(r.get('negative', 0) for r in results)
        total_neutral = sum(r.get('neutral', 0) for r in results)
        
        count = len(results)
        
        return {
            "positive": total_positive / count,
            "negative": total_negative / count,
            "neutral": total_neutral / count
        }

    async def start(self):
        """Start the sentiment engine (async placeholder)."""
        logger.info("SentimentEngine started.")

    async def stop(self):
        """Stop the sentiment engine (async placeholder)."""
        logger.info("SentimentEngine stopped.")

    async def get_interest_rate(self) -> float:
        """Get current interest rate (placeholder)."""
        # In a real app, this would fetch from FRED or an API
        return 0.05

    async def get_social_sentiment(self) -> float:
        """Get overall social sentiment score (placeholder)."""
        # In a real app, this would aggregate recent tweets/news
        # For now, return a neutral score or random
        return 0.1

if __name__ == "__main__":
    # Simple test
    async def main():
        engine = SentimentEngine()
        text = "Bitcoin hits all-time high as market sentiment turns extremely bullish."
        score = await engine.analyze_text(text)
        print(f"Text: {text}")
        print(f"Score: {score}")

    asyncio.run(main())
