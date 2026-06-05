# Ollama Models Setup Guide

## Overview

The Docker setup now includes an automated system to pull and manage the following Ollama models on container startup:

| Model | Size | Purpose |
|-------|------|---------|
| gemma4:e2b | 7.2 GB | Large multimodal model |
| andrewmccall/gemma3-tools:latest | 3.3 GB | Tool-using Gemma3 variant |
| qwen3.5:latest | 6.6 GB | Qwen 3.5 language model |
| gemma3:4b | 3.3 GB | Lightweight Gemma3 model |
| nomic-embed-text:latest | 274 MB | Text embedding model |
| llama3.2:latest | 2.0 GB | Llama 3.2 language model |
| llama3:latest | 4.7 GB | Llama 3 language model |

**Total Storage Required:** ~27.5 GB

## How It Works

### Automatic Model Pulling

When the ollama container starts, the `entrypoint.sh` script will:

1. Start the Ollama server
2. Wait for the server to be ready
3. Check which models are already available
4. Pull only the models that don't exist
5. Display the final list of available models

**Note:** The first time you start the container, all models will be pulled (this may take 30 minutes to an hour depending on your internet speed).

### Persistent Storage

Models are stored in the `ollama_data` Docker volume, which persists between container restarts. Once pulled, models will NOT be re-downloaded on subsequent starts.

## Getting Started

### Step 1: Rebuild the Image

```bash
docker-compose build --no-cache ollama-local
```

This will:
- Include the `entrypoint.sh` script in the image
- Keep the curl health check functionality
- Update the startup behavior

### Step 2: Start the Containers

```bash
docker-compose up -d
```

The first startup will take a while as models are being pulled. Monitor the progress:

```bash
docker-compose logs -f ollama-local
```

**Expected output during first startup:**
```
✓ Ollama server is ready
Checking and pulling Ollama models...
======================================
Pulling model: gemma4:e2b
[████████████████████████] 7.2 GB
✓ Successfully pulled: gemma4:e2b

Pulling model: andrewmccall/gemma3-tools:latest
[████████████████████████] 3.3 GB
✓ Successfully pulled: andrewmccall/gemma3-tools:latest

... (more models) ...

✓ All models ready!

Available models:
NAME                            ID              SIZE      MODIFIED
gemma4:e2b                      7fbdbf8f5e45    7.2 GB    2 hours ago
andrewmccall/gemma3-tools       5cd8aa17fbf6    3.3 GB    1 hour ago
...
```

### Step 3: Verify Models Are Available

```bash
# Check via API
curl http://localhost:11434/api/tags | jq '.models[] | .name'

# Or directly in container
docker exec log-analysis-ollama ollama list
```

## Timing Considerations

### First Startup
- Model pulling: **30-60 minutes** (depends on internet speed)
- Total container startup time: **60-90 minutes**

### Subsequent Startups
- Container startup time: **10-30 seconds**
- Models are instantly available

## Disk Space Requirements

- **Ollama image:** ~1.4 GB
- **Models volume:** ~27.5 GB
- **Total:** ~29 GB

### Storage Locations

**Docker Desktop (Windows/Mac):**
- Usually stored in Docker's allocated disk space
- Increase if needed in Docker Desktop settings

**Docker on Linux:**
- Default location: `/var/lib/docker/volumes/`
- Can be customized in `/etc/docker/daemon.json`

## Managing Models

### List Available Models

```bash
docker exec log-analysis-ollama ollama list
```

### Remove a Model

```bash
docker exec log-analysis-ollama ollama rm model-name
# Example: docker exec log-analysis-ollama ollama rm "llama3:latest"
```

### Pull Additional Models

```bash
docker exec log-analysis-ollama ollama pull model-name
# Example: docker exec log-analysis-ollama ollama pull "mistral:latest"
```

### Skip Auto-Pulling

If you want to start without auto-pulling models:

```bash
# Option 1: Temporarily comment out ENTRYPOINT in Dockerfile
# Option 2: Run container with custom command
docker-compose run -it ollama-local /bin/ollama serve
```

## Customizing Models

To add or remove models, edit the `entrypoint.sh` file:

```bash
# Edit this section in docker/ollama-local/entrypoint.sh
MODELS=(
    "gemma4:e2b"
    "andrewmccall/gemma3-tools:latest"
    # Add or remove models here
    "your-new-model:latest"
)
```

Then rebuild the image:

```bash
docker-compose build --no-cache ollama-local
```

## Troubleshooting

### Models Not Pulling

**Issue:** Container starts but models aren't being pulled

**Solution:**
```bash
# Check container logs
docker-compose logs ollama-local

# Verify server is running
curl http://localhost:11434/api/tags

# Manually pull models
docker exec log-analysis-ollama ollama pull gemma3:4b
```

### Out of Disk Space

**Issue:** Disk space insufficient for all models

**Solution:**
1. Choose essential models only (reduce list in entrypoint.sh)
2. Increase Docker's disk allocation
3. Clean up other Docker images:
   ```bash
   docker system prune -a
   ```

### Models Stuck on Pulling

**Issue:** A model seems to be stuck downloading

**Solution:**
```bash
# Stop the container
docker-compose down

# Remove the partial model
docker volume rm log-analysis-streamlit-ai-toolkit_ollama_data

# Or selectively clean:
docker exec log-analysis-ollama ollama rm stuck-model-name

# Restart
docker-compose up -d
```

### Network Issues

**Issue:** Models fail to pull due to network errors

**Solutions:**
1. Check your internet connection
2. Verify Ollama registry is accessible: `curl https://registry.ollama.ai/`
3. Use a VPN if your region has access restrictions
4. Retry: `docker-compose restart ollama-local`

## Performance Tips

### Optimize Startup Time

**Option 1: Selective Models**
Only include models you actually need:
```bash
MODELS=(
    "nomic-embed-text:latest"  # Essential for embeddings
    "gemma3:4b"                # Lightweight, good performance
    "llama3.2:latest"          # Strong all-around model
)
```

**Option 2: Parallel Pulling**
Modify the entrypoint script to pull models in parallel (advanced):
```bash
for model in "${MODELS[@]}"; do
    ollama pull "$model" &  # Add & for background execution
done
wait  # Wait for all to complete
```

### Monitor Resource Usage

```bash
# Watch CPU/Memory during model pulling
docker stats

# Check disk usage
docker exec log-analysis-ollama du -sh /root/.ollama/models
```

### Keep Models Updated

Models may receive updates. To update:

```bash
# Remove old version
docker exec log-analysis-ollama ollama rm model-name

# Pull latest
docker exec log-analysis-ollama ollama pull model-name:latest

# Or rebuild container
docker-compose build --no-cache ollama-local
```

## Architecture

### Model Storage Flow

```
┌─────────────────────────────────────────┐
│         Docker Container                │
│    (log-analysis-ollama)                │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │    Ollama Server (port 11434)   │   │
│  │                                 │   │
│  │  1. Receives pull request       │   │
│  │  2. Checks local cache          │   │
│  │  3. Downloads if needed         │   │
│  │  4. Stores in volume            │   │
│  └─────────────────────────────────┘   │
│            │                            │
│            ↓ (Mount)                    │
│  ┌─────────────────────────────────┐   │
│  │  /root/.ollama/models           │   │
│  │  (Volume: ollama_data)          │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
            │
            ↓ (Persists)
  Docker Volume (Host Disk)
  ~27.5 GB
```

## Files Modified

- ✅ `docker/ollama-local/entrypoint.sh` - New script for auto-pulling models
- ✅ `docker/ollama-local/Dockerfile` - Updated to use entrypoint script
- ✅ `MODELS_SETUP.md` - This guide

## Next Steps

1. **Build the updated image:**
   ```bash
   docker-compose build --no-cache ollama-local
   ```

2. **Start the containers:**
   ```bash
   docker-compose up -d
   ```

3. **Monitor the startup:**
   ```bash
   docker-compose logs -f ollama-local
   ```

4. **Wait for models to complete:**
   - Watch the logs until you see "✓ All models ready!"
   - This may take 30-60 minutes for the first run

5. **Verify everything is running:**
   ```bash
   docker-compose ps
   curl http://localhost:11434/api/tags
   ```

6. **Access your application:**
   - Streamlit UI: http://localhost:8501
   - Ollama API: http://localhost:11434

## Support

If you encounter issues:

1. Check the logs: `docker-compose logs ollama-local`
2. Verify disk space: `df -h`
3. Check network: `curl https://registry.ollama.ai/`
4. See the Troubleshooting section above

---

**Setup Date:** 2026-06-05
**Models Updated:** 7 models
**Total Size:** ~27.5 GB
