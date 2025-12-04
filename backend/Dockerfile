# Stage 1: Build the Rust extension
FROM python:3.13.9-slim as builder

WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install maturin
RUN pip install maturin

# Copy rust_core source
COPY rust_core/ ./rust_core/

# Build the wheel
WORKDIR /app/rust_core
# We use --features python-backend to enable pyo3
RUN maturin build --release --features python-backend --out dist

# Stage 2: Run the application
FROM python:3.13.9-slim

WORKDIR /app

# Install system dependencies (runtime)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy and install the generated wheel from builder stage
COPY --from=builder /app/rust_core/dist/*.whl .
RUN pip install *.whl && rm *.whl

# Copy requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project structure
COPY backend/ /app/backend/
COPY core/ /app/core/
COPY db/ /app/db/
COPY config/ /app/config/

# Set PYTHONPATH to include /app so imports like 'from db.timescale' work
ENV PYTHONPATH=/app

# Run from backend directory
WORKDIR /app/backend

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
