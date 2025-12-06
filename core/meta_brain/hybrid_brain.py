import logging
import os
import json
import google.generativeai as genai

logger = logging.getLogger("HybridBrain")

class HybridBrain:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        
        if not self.api_key:
            logger.warning("⚠️ Gemini API Key missing! Brain runs in dummy mode.")
        else:
            try:
                genai.configure(api_key=self.api_key, transport='rest')
                self.model = self._initialize_dynamic_model()
            except Exception as e:
                logger.error(f"❌ Failed to connect to Gemini: {e}")

    def _initialize_dynamic_model(self):
        """
        Dynamically finds and initializes the best available Gemini model.
        Priority: 1.5 Flash -> 1.5 Pro -> 1.0 Pro -> Any Available
        """
        try:
            logger.info("🔍 Scanning for available Gemini models...")
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            # আপনার পছন্দের মডেলগুলোর তালিকা (Priority অনুযায়ী)
            preferred_order = [
                'models/gemini-1.5-flash',
                'models/gemini-1.5-pro',
                'models/gemini-pro',
                'models/gemini-1.0-pro'
            ]

            selected_model_name = None

            # ১. পছন্দের মডেল আছে কিনা চেক করা
            for pref in preferred_order:
                if pref in available_models:
                    selected_model_name = pref
                    break
            
            # ২. যদি পছন্দের কোনোটি না পাওয়া যায়, তবে তালিকার প্রথমটি নেওয়া হবে
            if not selected_model_name and available_models:
                selected_model_name = available_models[0]
                logger.warning(f"⚠️ Preferred model not found. Fallback to: {selected_model_name}")

            if selected_model_name:
                logger.info(f"✅ Selected Model: {selected_model_name}")
                
                generation_config = {
                    "temperature": 0.5,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 1024,
                    "response_mime_type": "application/json",
                }
                
                return genai.GenerativeModel(
                    model_name=selected_model_name,
                    generation_config=generation_config
                )
            else:
                logger.error("❌ No suitable Gemini model found in your account!")
                return None

        except Exception as e:
            logger.error(f"❌ Error initializing model: {e}")
            return None

    async def get_market_sentiment(self, market_summary: str) -> dict:
        """
        AI কে জিজ্ঞেস করা হবে মার্কেট কন্ডিশন। সে JSON ফরম্যাটে উত্তর দিবে।
        """
        if not self.model:
            return {"sentiment": "NEUTRAL", "score": 0.5, "reason": "AI Brain Offline"}

        prompt = f"""
        Act as a Hedge Fund Risk Manager. Analyze this market summary: "{market_summary}"
        
        Respond with a JSON object containing:
        1. "sentiment": "BULLISH", "BEARISH", or "NEUTRAL"
        2. "score": A float between 0.0 (Extreme Fear) and 1.0 (Extreme Greed). 0.5 is Neutral.
        3. "reason": A short explanation (max 10 words).
        """
        
        try:
            # Async call to Gemini
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
            
        except Exception as e:
            logger.error(f"🧠 Brain Error: {e}")
            return {"sentiment": "NEUTRAL", "score": 0.5, "reason": "AI Error"}