FROM python:3.11-slim

# 1. Install build tools for TA-Lib C Library & dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Ollama CLI inside container
RUN curl -fsSL https://ollama.com/install.sh | sh

# 3. Download and compile TA-Lib C library
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

WORKDIR /app

# 4. Install Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy Project Files & Configure Entrypoint
COPY . .
RUN chmod +x entrypoint.sh

# Expose ports for Web UI (5000) and Ollama Engine (11434)
EXPOSE 5000 11434

ENV HOST=0.0.0.0
ENV PORT=5000
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["./entrypoint.sh"]
