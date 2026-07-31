#!/bin/bash
set -e

echo "=== Starting OmniAgent All-in-One Container ==="

export OLLAMA_HOST="127.0.0.1:11434"

echo "[1/3] Starting Ollama background daemon..."
ollama serve &

echo "[2/3] Waiting for Ollama API..."
until curl -s http://127.0.0.1:11434/api/tags > /dev/null; do
    sleep 1
done

echo "Ollama API is online!"

if ! curl -s http://127.0.0.1:11434/api/tags | grep -q "llava"; then
    echo "Pulling vision model (llava)..."
    ollama pull llava
fi

echo "[3/3] AI Models ready! Launching OmniAgent Server on http://localhost:8080..."
exec python web_interface.py
