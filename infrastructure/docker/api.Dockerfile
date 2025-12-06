# Base Image
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Fix: requirements.txt এখন legacy_backup এর ভেতরে আছে
COPY legacy_backup/backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy folders (New Structure)
COPY libs /app/libs
COPY apps/api_gateway /app/api

# Fix: Legacy code support (পুরনো কোড যেন কাজ করে)
COPY legacy_backup/backend /app/backend
COPY legacy_backup/core /app/core

# PYTHONPATH আপডেট করা যাতে সব ফোল্ডার থেকে ইম্পোর্ট করা যায়
ENV PYTHONPATH=/app:/app/libs:/app/backend:/app/core

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
