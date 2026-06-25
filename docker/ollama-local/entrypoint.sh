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
# Using stable models known to work with Ollama 0.30.10
MODELS=(
    "llama3.2:latest"                     # Stable, widely-used
    "nomic-embed-text:latest"             # Stable embedding model
    "llama3:latest"                       # Fallback option
    "qwen3.5:latest"                      # Qwen 3 (14B variant)
    "gemma4:latest"                       # Gemma 4 early version
    "qwen2.5:32b"                         # RAG in-depth (better reasoning for RCA)
    "mistral:7b"                          # Quick analysis (faster summaries)
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
