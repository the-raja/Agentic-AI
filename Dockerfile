# Use an official lightweight Python runtime
FROM python:3.11-slim

# Install system dependencies needed for Ollama (procps, zstd) and TA-Lib build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    procps \
    zstd \
    build-essential \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install official Ollama binary
RUN curl -fsSL https://ollama.com/install.sh | sh

# Download and compile TA-Lib C library
RUN curl -L https://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz -o ta-lib.tar.gz && \
    tar -xzf ta-lib.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    ldconfig && \
    cd .. && \
    rm -rf ta-lib ta-lib.tar.gz

# Set working directory inside container
WORKDIR /app

# Prevent Python from writing .pyc files and buffer logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8080

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Ensure entrypoint script is executable
RUN chmod +x entrypoint.sh

# Expose ports: 8080 (OmniAgent Web UI) and 11434 (Ollama)
EXPOSE 8080 11434

# Set entrypoint to run Ollama + OmniAgent all-in-one
ENTRYPOINT ["/app/entrypoint.sh"]
