# Models Deployment Status

## Current Setup

The Ollama container is now configured to automatically pull and manage 7 language models on startup.

### Models Configuration

| Model | Size | Status | Notes |
|-------|------|--------|-------|
| gemma4:e2b | 7.2 GB | ⚠️ Requires Ollama 0.4+ | Will skip on current version |
| andrewmccall/gemma3-tools | 3.3 GB | ✅ Compatible | Pulling now |
| qwen3.5:latest | 6.6 GB | ✅ Compatible | Queued |
| gemma3:4b | 3.3 GB | ✅ Compatible | Queued |
| nomic-embed-text:latest | 274 MB | ✅ Compatible | Queued |
| llama3.2:latest | 2.0 GB | ✅ Compatible | Queued |
| llama3:latest | 4.7 GB | ✅ Compatible | Queued |

**Total Size (Compatible Models):** ~20.2 GB

## How to Monitor Progress

### Watch Live Logs

```bash
docker-compose logs -f ollama-local
```

**Expected output:**
```
✓ Ollama server is ready

Checking and pulling Ollama models...
======================================
Pulling model: andrewmccall/gemma3-tools:latest
pulling aeda25e63ebd... 15% ▕███▏                ▏  512 MB/3.3 GB  6.7 MB/s  8m15s
```

### Check Model Availability

```bash
# Once pulling is complete, check available models
docker exec log-analysis-ollama ollama list
```

## Estimated Timeline

### First Startup
- **Time required:** 2-4 hours (depending on internet speed)
- **Network speed:** Assumes 6-10 MB/s download
- **gemma4:e2b:** Will be skipped (requires Ollama 0.4+)

**Download breakdown:**
- andrewmccall/gemma3-tools: ~30 minutes (3.3 GB)
- qwen3.5:latest: ~60 minutes (6.6 GB)
- gemma3:4b: ~30 minutes (3.3 GB)
- llama3:latest: ~45 minutes (4.7 GB)
- llama3.2:latest: ~20 minutes (2.0 GB)
- nomic-embed-text:latest: ~3 minutes (274 MB)

### Subsequent Startups
- **Time required:** 10-30 seconds
- Models are already cached and won't be re-downloaded

## Current System Status

### Services Running

```bash
$ docker-compose ps

NAME                  IMAGE                                  STATUS
log-analysis-ollama   ...ollama-local:latest                 Up (healthy) ✓
log-analysis-streamlit ...streamlit-app:latest               Up (healthy) ✓
```

### Available APIs

- **Ollama API:** http://localhost:11434
- **Streamlit UI:** http://localhost:8501

## What Happens on Startup

1. ✓ Ollama server starts and listens on port 11434
2. ✓ Health check passes after server is ready
3. ✓ Entrypoint script checks for each model
4. ✓ Missing models are automatically pulled
5. ✓ Streamlit container waits for Ollama health check
6. ✓ Streamlit starts once Ollama is healthy

## Model Pulling Details

### Automatic Pulling

The `entrypoint.sh` script in the Ollama container:

```bash
# For each model, check if it exists
if ollama list | grep -q "^${model}"; then
    echo "✓ Model already exists: $model"
else
    echo "Pulling model: $model"
    ollama pull "$model"
fi
```

**Benefits:**
- ✅ One-time setup (pulls only missing models)
- ✅ Persistent storage (survives container restarts)
- ✅ No manual intervention needed
- ✅ Automatic resume if interrupted

### Storage Location

Models are stored in Docker volume: `ollama_data`

**Path inside container:** `/root/.ollama/models`

**Disk usage:** ~20-27 GB (depending on which models are pulled)

## Managing Models

### List Available Models

```bash
docker exec log-analysis-ollama ollama list
```

**Example output:**
```
NAME                            ID              SIZE      MODIFIED
andrewmccall/gemma3-tools       5cd8aa17fbf6    3.3 GB    15 minutes ago
qwen3.5:latest                  6488c96fa5fa    6.6 GB    30 minutes ago
gemma3:4b                       a2af6cc3eb7f    3.3 GB    45 minutes ago
nomic-embed-text:latest         0a109f422b47    274 MB    1 hour ago
llama3.2:latest                 a80c4f17acd5    2.0 GB    1 hour ago
llama3:latest                   365c0bd3c000    4.7 GB    1 hour ago
```

### Remove a Model (to free space)

```bash
docker exec log-analysis-ollama ollama rm "model-name"
# Example: docker exec log-analysis-ollama ollama rm "llama3:latest"
```

### Manually Pull Additional Models

```bash
docker exec log-analysis-ollama ollama pull "model-name"
# Example: docker exec log-analysis-ollama ollama pull "mistral:latest"
```

### Stop Auto-Pulling (Emergency)

If you need to stop the process and just run the server:

```bash
# Stop current containers
docker-compose down

# Run container without auto-pulling
docker-compose run -it ollama-local /bin/ollama serve
```

## Troubleshooting

### Model Won't Pull

**Error:** `Error: pull model manifest: 412`

This means the model requires a newer version of Ollama.

**Solution:** 
- Model will be skipped automatically
- The script will continue with other models
- This is normal for `gemma4:e2b` with Ollama 0.3.6

### Pulling Stuck at 0%

**Cause:** Network issue or registry timeout

**Solution:**
```bash
# Check container logs
docker-compose logs ollama-local

# Restart container (will resume pulling)
docker-compose restart ollama-local

# Or fully clean and restart
docker-compose down -v
docker-compose up -d
```

### Disk Space Full

**Error:** Model pulling stops suddenly

**Solution:**
1. Check disk space: `df -h`
2. Clean up other Docker resources: `docker system prune -a`
3. Remove unnecessary models: `docker exec log-analysis-ollama ollama rm model-name`
4. Increase Docker's allocated disk space

### Network Connection Issues

**Error:** Models not downloading

**Solution:**
```bash
# Check internet connection
ping google.com

# Test registry access
curl https://registry.ollama.ai/

# Try using a different DNS
# Or use a VPN if your region blocks the registry
```

## Performance Tips

### Optimize Download Speed

1. **Use wired connection** if possible (faster and more stable than WiFi)
2. **Close bandwidth-heavy applications** during pulling
3. **Use a local network mirror** if your organization has one
4. **Run during off-peak hours** for better registry speeds

### Monitor During Pulling

```bash
# Watch real-time download speed
docker-compose logs -f ollama-local | grep "MB/s"

# Check disk usage
docker exec log-analysis-ollama du -sh /root/.ollama/models
```

## Files Modified

- ✅ `docker/ollama-local/entrypoint.sh` - Automated model pulling script
- ✅ `docker/ollama-local/Dockerfile` - Updated with entrypoint
- ✅ `MODELS_SETUP.md` - Complete model management guide
- ✅ `MODELS_DEPLOYMENT.md` - This file

## Next Steps

### 1. Monitor the Pulling Process

```bash
docker-compose logs -f ollama-local
```

Watch for:
- "✓ Ollama server is ready" - Server is up
- "pulling aeda25e63ebd..." - Model download in progress
- "✓ Successfully pulled: model-name" - Model completed
- "✓ All models ready!" - All pulling finished

### 2. Wait for Completion

Time required: 2-4 hours for first startup

You can interrupt and resume later - the script will pick up where it left off.

### 3. Verify Models Are Available

```bash
docker exec log-analysis-ollama ollama list
```

Should show all successfully pulled models.

### 4. Use the Application

Once models are ready:
- Access Streamlit: http://localhost:8501
- Use any available model in your application

## Using Models in Your Application

### With Ollama SDK

```python
import ollama

# List available models
response = ollama.list()

# Generate with a specific model
response = ollama.generate(
    model="llama3.2:latest",
    prompt="Tell me about docker"
)
```

### With API

```bash
# Generate using REST API
curl http://localhost:11434/api/generate \
  -d '{
    "model": "llama3.2:latest",
    "prompt": "Tell me about docker"
  }'

# For embeddings
curl http://localhost:11434/api/embeddings \
  -d '{
    "model": "nomic-embed-text:latest",
    "prompt": "Hello world"
  }'
```

## Rollback to Minimal Setup

If you want only essential models:

Edit `docker/ollama-local/entrypoint.sh` and change:

```bash
MODELS=(
    "nomic-embed-text:latest"    # Essential for embeddings
    "gemma3:4b"                  # Fast, lightweight
)
```

Then rebuild:
```bash
docker-compose build --no-cache ollama-local
```

---

**Setup Date:** 2026-06-05
**Version:** Ollama 0.3.6
**Models:** 6 compatible + 1 requiring upgrade
**Storage Required:** ~20-27 GB
**Status:** Auto-pulling in progress
