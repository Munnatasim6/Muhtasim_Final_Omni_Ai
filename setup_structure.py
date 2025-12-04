import os
import shutil
from pathlib import Path

def move_files():
    # ১. আমরা নতুন ফোল্ডারগুলো তৈরি করছি
    new_dirs = [
        "apps/dashboard",
        "apps/api-gateway",
        "services/execution-engine",
        "services/ai-brain",
        "services/data-nexus",
        "services/blockchain-watcher",
        "libs/database",
        "libs/strategies",
        "libs/shared-utils",
        "infrastructure/docker",
        "infrastructure/k8s"
    ]

    print("🚀 প্রজেক্ট রি-অর্গানাইজেশন শুরু হচ্ছে...")

    for d in new_dirs:
        os.makedirs(d, exist_ok=True)
        print(f"✅ ফোল্ডার তৈরি হয়েছে: {d}")

    # ২. ফাইল মুভ করার লজিক (Source -> Destination)
    moves = {
        # Frontend (React) চলে যাবে apps/dashboard এ
        "frontend": "apps/dashboard/frontend",
        "dashboard": "apps/dashboard/legacy_dashboard",
        
        # Rust Core চলে যাবে services/execution-engine এ
        "rust_core": "services/execution-engine/rust_core",
        
        # Web3 Modules চলে যাবে services/blockchain-watcher এ
        "web3_modules": "services/blockchain-watcher/src",
        
        # Strategies চলে যাবে libs/strategies এ
        "strategies": "libs/strategies/src",
        
        # DB ফাইলগুলো libs/database এ
        "db": "libs/database/src",
        
        # Kubernetes ফাইলগুলো infrastructure এ
        "k8s": "infrastructure/k8s/config",
    }

    # ৩. মুভ করা হচ্ছে
    for src, dst in moves.items():
        if os.path.exists(src):
            # গন্তব্য ফোল্ডার নিশ্চিত করা
            dst_dir = os.path.dirname(dst)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            
            # মুভ করা
            try:
                shutil.move(src, dst)
                print(f"📦 সরানো হয়েছে: {src} -> {dst}")
            except Exception as e:
                print(f"❌ সমস্যা হয়েছে {src} সরাতে: {e}")
        else:
            print(f"⚠️ পাওয়া যায়নি: {src} (হয়তো আগেই সরানো হয়েছে)")

    # ৪. Core এবং Backend এর ফাইলগুলো আমরা আপাতত 'libs' বা 'services' এ নিচ্ছি না
    # কারণ ওগুলো refactor করা দরকার। তবে আমরা একটা 'legacy' ফোল্ডারে রেখে দিতে পারি
    # যাতে মেইন ফোল্ডার ক্লিন থাকে।
    
    print("\n🎉 অভিনন্দন! আপনার প্রজেক্ট এখন 'Google-Ready' স্ট্রাকচারে আছে।")
    print("এখন আপনি apps/ এবং services/ ফোল্ডারগুলো দেখতে পাবেন।")

if __name__ == "__main__":
    move_files()
