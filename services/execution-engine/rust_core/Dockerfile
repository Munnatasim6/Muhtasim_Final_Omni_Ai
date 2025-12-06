# Stage 1: Build
FROM rust:1.83 as builder
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# FIX: Explicitly build the binary "rust_core"
RUN cargo build --release --bin rust_core

# Stage 2: Run
FROM debian:bookworm-slim
WORKDIR /app

# Install runtime dependencies for health checks if needed
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy the binary from the specific path
COPY --from=builder /app/target/release/rust_core /usr/local/bin/rust_core

RUN chmod +x /usr/local/bin/rust_core

CMD ["rust_core"]
