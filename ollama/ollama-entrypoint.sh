#!/bin/bash
set -e

ollama serve &
SERVER_PID=$!

echo "Waiting for Ollama to start..."
until curl -s http://localhost:11434/api/tags >/dev/null; do
  sleep 1
done

echo "Pulling llama3.2 model..."
ollama pull llama3.2 || true

wait $SERVER_PID