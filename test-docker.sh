#!/bin/bash

echo "Testing Docker Compose Setup..."
echo "================================"

echo ""
echo "1. Stopping any existing containers..."
docker-compose down -v 2>/dev/null || true

echo ""
echo "2. Starting containers..."
docker-compose up -d

echo ""
echo "3. Waiting for ollama to be healthy..."
for i in {1..30}; do
  if docker-compose ps | grep -q "log-analysis-ollama.*healthy"; then
    echo "✓ Ollama is healthy!"
    break
  fi
  echo "  Attempt $i/30..."
  sleep 2
done

echo ""
echo "4. Checking container status..."
docker-compose ps

echo ""
echo "5. Testing Ollama API..."
curl -s http://localhost:11434/api/tags | head -20

echo ""
echo "6. Checking Streamlit health..."
curl -s http://localhost:8501/_stcore/health 2>/dev/null && echo "✓ Streamlit is healthy" || echo "! Streamlit not yet ready"

echo ""
echo "================================"
echo "Setup complete!"
echo "Ollama API: http://localhost:11434"
echo "Streamlit UI: http://localhost:8501"
