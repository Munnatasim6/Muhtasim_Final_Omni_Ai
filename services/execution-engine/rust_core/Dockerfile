# Stage 1: Build
FROM rust:1.75 as builder
WORKDIR /app
COPY . .
# রিলিজ মোডে বিল্ড করা হচ্ছে
RUN cargo build --release

# Stage 2: Run
FROM debian:bookworm-slim
WORKDIR /app
# বিল্ডার স্টেজ থেকে বাইনারি কপি করা হচ্ছে
COPY --from=builder /app/target/release/rust_core /usr/local/bin/rust_core

# এক্সিকিউটেবল পারমিশন দেওয়া
RUN chmod +x /usr/local/bin/rust_core

CMD ["rust_core"]
