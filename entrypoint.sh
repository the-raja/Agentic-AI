#!/bin/bash
set -e

echo "=========================================="
echo "🚀 Starting OmniAgent Docker Container"
echo "=========================================="

# Start Ollama service in background
echo "📦 Starting Ollama engine in background..."
ollama serve > /tmp/ollama.log 2>&1 &

# Wait for Ollama service to become responsive
echo "⏳ Waiting for Ollama engine to initialize..."
until curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
    sleep 2
done

echo "✅ Ollama engine is online!"

# Verify or pull default vision model (llava)
echo "🧠 Checking Ollama vision model (llava)..."
ollama pull llava

echo "✅ Vision model 'llava' ready!"

# Launch Flask Web Interface
echo "🌐 Launching OmniAgent Web Dashboard on port ${PORT:-5000}..."
exec python web_interface.py
