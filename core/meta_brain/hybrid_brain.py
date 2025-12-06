import logging
import os
import json
import google.generativeai as genai

logger = logging.getLogger("HybridBrain")

class HybridBrain:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("⚠️ Gemini API Key missing! Brain runs in dummy mode.")
            self.model = None
        else:
            genai.configure(api_key=self.api_key, transport='rest')
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("✅ Gemini 1.5 Flash Connected")

    async def get_market_sentiment(self, market_summary: str) -> dict:
        """
        AI কে জিজ্ঞেস করা হবে মার্কেট কন্ডিশন। সে JSON ফরম্যাটে উত্তর দিবে।
        """
        if not self.model:
            return {"sentiment": "NEUTRAL", "score": 0.5, "reason": "No API Key"}

        prompt = f"""
        Act as a Hedge Fund Risk Manager. Analyze this market summary: "{market_summary}"
        
        Return a strictly valid JSON string (no markdown) with:
        1. "sentiment": "BULLISH", "BEARISH", or "NEUTRAL"
        2. "score": A float between 0.0 (Extreme Fear) and 1.0 (Extreme Greed). 0.5 is Neutral.
        3. "reason": A short explanation (max 10 words).
        
        JSON Example: {{"sentiment": "BULLISH", "score": 0.8, "reason": "High volume breakout"}}
        """
        
        try:
            # Async call to Gemini (running in thread executor to avoid blocking)
            # Note: In production, consider using true async client if available or threadpool
            response = self.model.generate_content(prompt)
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except Exception as e:
            logger.error(f"Brain Error: {e}")
            return {"sentiment": "NEUTRAL", "score": 0.5, "reason": "AI Error"}
