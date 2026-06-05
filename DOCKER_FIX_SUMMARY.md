# Docker Setup Fix Summary

## Problem
The Docker Compose setup was failing with the error:
```
Error: unknown command "ollama" for "ollama"
Container log-analysis-ollama exited with code 1
```

## Root Cause
The Dockerfile for the ollama service was incorrectly overriding the CMD instruction. The `ollama/ollama:latest` base image has its own entrypoint and command setup, which was being broken by the explicit `CMD ["ollama", "serve"]` override.

## Changes Made

### 1. Fixed `docker/ollama-local/Dockerfile`
**Before:**
```dockerfile
FROM ollama/ollama:latest

WORKDIR /app

# Expose Ollama port
EXPOSE 11434

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s \
    CMD curl -f http://localhost:11434/api/tags || exit 1

# Run Ollama server
CMD ["ollama", "serve"]
```

**After:**
```dockerfile
FROM ollama/ollama:0.3.6

# Install curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s \
    CMD curl -f http://localhost:11434/api/tags || exit 1
```

**Why:**
- Changed from `latest` to a pinned stable version `0.3.6` to avoid unpredictable behavior
- **Added curl installation** - the health check requires curl, which wasn't available in the base image
- Removed the problematic `CMD` override - the base image already handles this correctly
- Removed unnecessary `WORKDIR` and `EXPOSE` statements (already in base image)
- Kept the HEALTHCHECK which is essential for Docker Compose service dependency management

### 2. Fixed `docker-compose.yml`
**Before:**
```yaml
version: '3.8'

services:
  ...
```

**After:**
```yaml
services:
  ...
```

**Why:**
- Removed the obsolete `version` attribute (Docker Compose v2+ ignores it)
- Eliminates deprecation warnings

## Testing

To verify the fix works:

```bash
# Clean rebuild
docker-compose build --no-cache

# Start containers
docker-compose up -d

# Check status
docker-compose ps

# Test Ollama API
curl http://localhost:11434/api/tags

# View logs if needed
docker-compose logs -f ollama-local
docker-compose logs -f streamlit-app
```

## Expected Behavior

1. **Ollama Container** should:
   - Start without errors
   - Pass health checks within 30-60 seconds
   - Be accessible at `http://localhost:11434`
   - Store models in the `ollama_data` volume

2. **Streamlit Container** should:
   - Wait for Ollama to be healthy (via `depends_on`)
   - Start within 60-120 seconds after Ollama is ready
   - Be accessible at `http://localhost:8501`
   - Mount volumes for data persistence

## Next Steps

1. **Pull LLM Models** (first time setup):
   ```bash
   docker exec log-analysis-ollama ollama pull gemma3:4b
   docker exec log-analysis-ollama ollama pull llama3.2
   docker exec log-analysis-ollama ollama pull nomic-embed-text
   ```

2. **Access the Application**:
   - Streamlit UI: http://localhost:8501
   - Ollama API: http://localhost:11434/api/tags

3. **Monitor Container Health**:
   ```bash
   docker stats
   docker-compose logs -f
   ```

## Troubleshooting

If you still encounter issues:

1. **Check Docker resources**: Allocate at least 4GB RAM to Docker
2. **Clean rebuild**: `docker-compose down -v && docker-compose build --no-cache`
3. **Check logs**: `docker-compose logs`
4. **Verify curl is available**: The health check requires curl in both containers
5. **Port conflicts**: Ensure ports 11434 and 8501 are not in use

## Architecture

The setup uses two services in a Docker network:

```
┌─────────────────────────────────────────┐
│     Docker Network (bridge)             │
│    log-analysis-network                 │
│                                         │
│  ┌──────────────────┐ ┌──────────────┐ │
│  │  ollama-local    │ │  streamlit   │ │
│  │  Port 11434      │ │  Port 8501   │ │
│  └──────────────────┘ └──────────────┘ │
│         ▲                     │         │
│         └─────────────────────┘         │
│     (Streamlit depends on Ollama)       │
└─────────────────────────────────────────┘
         ▼              ▼
    localhost:11434   localhost:8501
```

**Persisted Volumes:**
- `ollama_data`: LLM models
- `db_logs`: Log embeddings
- `db_kb`: Knowledge base embeddings
- `logs`: Application logs
