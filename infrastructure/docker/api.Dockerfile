# বেস ইমেজ হিসেবে আমরা স্লিম ভার্সন ব্যবহার করছি যাতে সাইজ কম হয়
FROM python:3.10-slim

# পাইথনের আউটপুট বাফারিং বন্ধ রাখা (লগ দেখার সুবিধার জন্য)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ওয়ার্কিং ডিরেক্টরি সেট করা
WORKDIR /app

# সিস্টেম ডিপেন্ডেন্সি ইনস্টল করা (PostgreSQL/TimeScaleDB এর জন্য libpq-dev জরুরি)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# রিকোয়ারমেন্টস ফাইল কপি করা এবং ইনস্টল করা
# নোট: আমরা ধরে নিচ্ছি আপনার মূল requirements.txt টি backend ফোল্ডারে আছে
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# আমাদের নতুন স্ট্রাকচার অনুযায়ী ফোল্ডারগুলো কন্টেইনারে কপি করা
# ১. শেয়ারড লাইব্রেরি (Libs)
COPY libs /app/libs

# ২. লিগ্যাসি কোড সাপোর্ট (পুরানো ইম্পোর্ট ঠিক রাখার জন্য)
COPY backend /app/backend

# ৩. মেইন অ্যাপ (API Gateway)
COPY apps/api-gateway /app/api

# এনভায়রনমেন্ট ভেরিয়েবল সেট করা যাতে পাইথন মডিউলগুলো খুঁজে পায়
ENV PYTHONPATH=/app:/app/libs:/app/backend

# কন্টেইনারের পোর্ট এক্সপোজ করা
EXPOSE 8000

# সার্ভার রান করা
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
