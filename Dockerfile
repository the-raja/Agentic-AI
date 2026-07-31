FROM python:3.11-slim

# 1. Install build tools for TA-Lib C Library & system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. Download and install official Ollama binary
RUN curl -fsSL https://github.com/ollama/ollama/releases/latest/download/ollama-linux-amd64.tgz -o ollama.tgz && \
    mkdir -p /usr/local && \
    tar -C /usr/local -xzf ollama.tgz && \
    rm -f ollama.tgz

# 3. Download and compile TA-Lib C library (using GitHub releases mirror)
RUN curl -fsSL https://github.com/ta-lib/ta-lib/releases/download/v0.4.0/ta-lib-0.4.0-src.tar.gz -o ta-lib.tar.gz && \
    tar -xzf ta-lib.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    ldconfig && \
    cd .. && \
    rm -rf ta-lib ta-lib.tar.gz

WORKDIR /app

# 4. Install Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy Project Files & Configure Entrypoint
COPY . .
RUN chmod +x entrypoint.sh

# Expose ports for Web UI (8080) and Ollama Engine (11434)
EXPOSE 8080 11434

ENV HOST=0.0.0.0
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["./entrypoint.sh"]
