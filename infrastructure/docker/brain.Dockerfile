# AI এর জন্য পাইথন ৩.১০ ভালো
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# AI লাইব্রেরি (NumPy, Pandas, PyTorch) কম্পাইল করার জন্য প্রয়োজনীয় টুলস
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ডিপেন্ডেন্সি ইনস্টল
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# AI ব্রেইন সার্ভিসের কোড কপি করা
COPY libs /app/libs
COPY core /app/core
COPY services/ai-brain /app/brain

# মডেল রাখার ফোল্ডার তৈরি করা
RUN mkdir -p /app/data/models

# পাথ সেট করা
ENV PYTHONPATH=/app:/app/libs:/app/core

# ডিফল্ট কমান্ড (এটি পরবর্তীতে আপনার দরকার মতো পরিবর্তন করা যাবে)
# আপাতত এটি ইনফিনিটি লুপে চলবে যাতে কন্টেইনার বন্ধ না হয়ে যায়
CMD ["tail", "-f", "/dev/null"]
