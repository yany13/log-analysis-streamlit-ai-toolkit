#!/bin/bash

# Log Analysis AI Toolkit - Docker Runner
set -e

echo "🚀 Starting Log Analysis AI Toolkit with Docker..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Display information
echo "📋 Configuration:"
echo "  - Ollama API: http://localhost:11434"
echo "  - Streamlit UI: http://localhost:8501"
echo "  - Database volumes: db_logs, db_kb"
echo ""

# Build and start containers
echo "🔨 Building and starting containers..."
docker-compose up --build

echo ""
echo "✅ Done! Access the application at http://localhost:8501"
