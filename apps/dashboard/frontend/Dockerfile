# Stage 1: Build the Rust WASM module
FROM rust:1.83-slim as rust-builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install wasm-pack via binary
RUN curl https://rustwasm.github.io/wasm-pack/installer/init.sh -sSf | sh

# Copy rust_core source
COPY rust_core/ ./rust_core/

# Build WASM module
WORKDIR /app/rust_core
RUN wasm-pack build --target web --no-default-features

# Stage 2: Build the React application
FROM node:24-alpine as build

WORKDIR /app

# Copy package.json and package-lock.json from frontend directory
COPY frontend/package*.json ./frontend/

# Set working directory to frontend
WORKDIR /app/frontend

# Install dependencies
RUN npm install

# Copy the rest of the frontend application code
COPY frontend/ .

# Copy rust_core/pkg from the rust-builder stage
# Frontend expects ../../../rust_core/pkg/rust_core
# So we need to put it in /app/rust_core/pkg
COPY --from=rust-builder /app/rust_core/pkg /app/rust_core/pkg

# Build the application
RUN npm run build

# Stage 3: Serve the application with Nginx
FROM nginx:alpine

# Copy the build output from the previous stage to the Nginx html directory
COPY --from=build /app/frontend/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
