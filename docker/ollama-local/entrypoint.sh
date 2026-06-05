#!/bin/bash

# Start ollama server in the background
ollama serve &
OLLAMA_PID=$!

# Wait for ollama to be ready
echo "Waiting for Ollama server to start..."
until curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
    sleep 2
done
echo "✓ Ollama server is ready"

# Array of models to pull
# Note: Some models may require newer Ollama versions
MODELS=(
    "gemma4:e2b"                          # Requires Ollama 0.4+
    "andrewmccall/gemma3-tools:latest"
    "qwen3.5:latest"
    "gemma3:4b"
    "nomic-embed-text:latest"
    "llama3.2:latest"
    "llama3:latest"
)

# Pull models if they don't already exist
echo ""
echo "Checking and pulling Ollama models..."
echo "======================================"

for model in "${MODELS[@]}"; do
    # Check if model already exists
    if ollama list | grep -q "^${model}"; then
        echo "✓ Model already exists: $model"
    else
        echo "Pulling model: $model"
        ollama pull "$model"
        if [ $? -eq 0 ]; then
            echo "✓ Successfully pulled: $model"
        else
            echo "✗ Failed to pull: $model"
        fi
    fi
    echo ""
done

echo "======================================"
echo "✓ All models ready!"
echo ""
echo "Available models:"
ollama list
echo ""

# Keep the server running in foreground
wait $OLLAMA_PID
