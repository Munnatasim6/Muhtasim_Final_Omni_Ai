import asyncio
import logging
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ১. পাথ সেটআপ: যাতে legacy_backup ফোল্ডারের কোডগুলো খুঁজে পাওয়া যায়
sys.path.append(os.path.abspath("legacy_backup"))

# ২. SwarmManager ইমপোর্ট করার চেষ্টা
try:
    from backend.brain.swarm_manager import SwarmManager
except ImportError as e:
    print(f"❌ Error importing SwarmManager: {e}")
    print("Tip: নিশ্চিত করুন 'legacy_backup' ফোল্ডারটি ঠিক আছে এবং 'backend/brain/swarm_manager.py' ফাইলটি সেখানে আছে।")
    sys.exit(1)

# ৩. লগিং কনফিগারেশন (সুন্দর আউটপুটের জন্য)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("TestRun")

async def run_test():
    print("\n" + "="*60)
    print("🚀 STARTING DRY RUN: Swarm Intelligence Test")
    print("   লক্ষ্য: টেকনিক্যাল এজেন্ট এবং Gemini AI-এর সংযোগ পরীক্ষা")
    print("="*60 + "\n")

    # Check API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️  WARNING: GEMINI_API_KEY not found in .env file!")
        print("   Please create a .env file with GEMINI_API_KEY=your_key_here")
    else:
        print("✅ GEMINI_API_KEY found in environment.")

    # ধাপ ১: ম্যানেজার ইনিশিলাইজেশন
    print("1️⃣  Initializing Swarm Manager...")
    try:
        manager = SwarmManager()
        print("✅ SwarmManager Loaded Successfully.\n")
    except Exception as e:
        print(f"❌ Failed to init manager: {e}")
        return

    # ধাপ ২: ফেইক মার্কেট ডেটা তৈরি (Mock Data)
    # আমরা এমন ডেটা দিচ্ছি যাতে টেকনিক্যাল সিগন্যাল 'Strong BUY' আসে।
    # দেখব AI নিউজ দেখে সেটাকে সাপোর্ট করে নাকি ভেটো দেয়।
    market_data = {
        "symbol": "BTC/USDT",
        "price": 95000.0,
        "volume": 1200.0,
        # features ভ্যালুগুলো টেকনিক্যাল এজেন্টের ইনপুট (RSI, MACD ইত্যাদির ডামি ভ্যালু)
        # 1.0 = Buy Signal
        "features": [1.0, 0.9, 1.0, 0.8, 1.0], 
        "portfolio_value": 10000.0,
        "orderbook_features": []
    }
    
    print(f"2️⃣  Injecting Mock Market Data: {market_data['symbol']} @ ${market_data['price']}")
    print("------------------------------------------------------------")

    # ধাপ ৩: সিদ্ধান্ত চাওয়া (The Moment of Truth)
    # এখানে SwarmManager টেকনিক্যাল ক্যালকুলেশন করবে এবং Gemini API কল করবে
    decision = await manager.get_swarm_decision(market_data)

    # ধাপ ৪: রেজাল্ট বিশ্লেষণ ও রিপোর্ট
    print("\n" + "="*60)
    print("📝 FINAL DECISION REPORT (ফলাফল)")
    print("="*60)
    
    # ফাইনাল অ্যাকশন
    action_color = "🟢" if decision['action'] == "BUY" else "🔴" if decision['action'] == "SELL" else "⚪"
    print(f"{action_color} Action:      {decision['action']}")
    print(f"🔹 Confidence:  {decision['confidence']} (Scale: 0.0 - 1.0)")
    
    print("-" * 40)
    details = decision['details']
    
    # টেকনিক্যাল স্কোর (আমাদের Mock Data অনুযায়ী এটি বেশি আসার কথা)
    print(f"🔸 Tech Score:  {details.get('tech_score'):.2f} (Weight: 60%)")
    
    # AI এর মতামত (সবচেয়ে গুরুত্বপূর্ণ অংশ)
    ai_reason = details.get('ai_reason')
    if ai_reason == "Brain Disabled" or ai_reason == "AI Error" or ai_reason == "No API Key":
        print(f"⚠️  AI Status:   ❌ {ai_reason} (API Key ঠিক আছে তো?)")
    else:
        print(f"🧠 AI Reason:   ✅ \"{ai_reason}\"")
        print(f"   (Gemini সফলভাবে মার্কেট ডেটা বিশ্লেষণ করেছে)")

    print(f"🔸 Risk Status: {details.get('risk_status')}")
    print("="*60 + "\n")

if __name__ == "__main__":
    # উইন্ডোজের জন্য ইভেন্ট লুপ ফিক্স (যদি লাগে)
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # টেস্ট রান করা
    asyncio.run(run_test())
