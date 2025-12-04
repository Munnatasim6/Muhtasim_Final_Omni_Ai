FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc g++ libpq-dev build-essential curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Fix: Path update for requirements
COPY legacy_backup/backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy Service Code
COPY libs /app/libs
COPY services/ai-brain /app/brain

# Fix: Legacy Core Support
COPY legacy_backup/core /app/core
COPY legacy_backup/backend /app/backend

RUN mkdir -p /app/data/models

# Fix: PYTHONPATH inclusion
ENV PYTHONPATH=/app:/app/libs:/app/core:/app/backend

CMD ["tail", "-f", "/dev/null"]
