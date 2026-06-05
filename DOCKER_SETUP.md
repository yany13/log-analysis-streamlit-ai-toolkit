# Docker Setup Guide

This guide walks you through running the Log Analysis AI Toolkit using Docker.

## Prerequisites

### Windows
1. **Docker Desktop for Windows**
   - Download: https://www.docker.com/products/docker-desktop
   - Install with WSL 2 backend (recommended)
   - Allocate at least 4GB RAM to Docker

### macOS
1. **Docker Desktop for Mac**
   - Download: https://www.docker.com/products/docker-desktop
   - Allocate at least 4GB RAM to Docker

### Linux
1. **Docker Engine**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   ```

2. **Docker Compose**
   ```bash
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

## Quick Start

### Windows (Easiest)
Simply double-click:
```
run-docker.bat
```

### macOS / Linux
```bash
chmod +x run-docker.sh
./run-docker.sh
```

### Or manually
```bash
docker-compose up --build
```

## What Gets Started

The `docker-compose.yml` starts 2 services:

### 1. Ollama (Port 11434)
- **Image**: `ollama/ollama:latest`
- **Purpose**: Local LLM inference server
- **Volumes**: `ollama_data` (persists models)
- **Health Check**: Checks `/api/tags` endpoint

### 2. Streamlit (Port 8501)
- **Image**: Built from `./docker/Dockerfile`
- **Purpose**: Web UI for log analysis
- **Volumes**: 
  - `db_logs` - Vector database for logs
  - `db_kb` - Vector database for knowledge base
  - `./logs` - Application logs
- **Dependencies**: Waits for Ollama to be healthy
- **Environment**: `OLLAMA_URL=http://ollama:11434`

## How to Use

1. **Start containers** (see Quick Start above)

2. **Wait for services to start**
   ```
   Ollama: 10-30 seconds
   Streamlit: 30-60 seconds
   ```

3. **Open in browser**
   - Streamlit UI: http://localhost:8501
   - Ollama API: http://localhost:11434/api/tags

4. **Pull models in Ollama** (first time only)
   ```bash
   # Access Ollama container
   docker exec -it log-analyzer-ollama ollama pull gemma3:4b
   docker exec -it log-analyzer-ollama ollama pull llama3.2
   docker exec -it log-analyzer-ollama ollama pull nomic-embed-text
   ```

5. **Use the application**
   - Upload logs
   - Index knowledge base
   - Run RCA analysis

## Useful Docker Commands

### View running containers
```bash
docker ps
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f streamlit
docker-compose logs -f ollama
```

### Stop services
```bash
docker-compose down
```

### Stop and remove volumes (WARNING: deletes data)
```bash
docker-compose down -v
```

### Rebuild images
```bash
docker-compose build --no-cache
```

### Access container shell
```bash
docker exec -it log-analyzer-app /bin/bash
docker exec -it log-analyzer-ollama /bin/sh
```

### Check container resource usage
```bash
docker stats
```

## Troubleshooting

### "Docker daemon is not running"
**Windows**: Open Docker Desktop application

**Linux**: Start Docker service
```bash
sudo systemctl start docker
```

### Port already in use
If ports 8501 or 11434 are already used, modify `docker-compose.yml`:
```yaml
ports:
  - "8502:8501"  # Change 8502 to desired port
  - "11435:11434"  # Change 11435 to desired port
```

### Out of disk space
Clean up Docker resources:
```bash
docker system prune -a
```

### Ollama models not loading
Models are stored in the `ollama_data` volume. To reset:
```bash
docker-compose down -v
docker-compose up  # Will be clean, need to re-pull models
```

### Streamlit slow or unresponsive
Check resource allocation in Docker Desktop:
- Settings → Resources
- Allocate more CPU and Memory

### Requirements not installing
Check Docker build logs:
```bash
docker-compose build --no-cache streamlit
docker-compose logs streamlit
```

## Performance Tips

1. **Allocate Resources**
   - Minimum: 4GB RAM, 2 CPU cores
   - Recommended: 8GB RAM, 4 CPU cores

2. **Model Selection**
   - Smaller models run faster: `nomic-embed-text`, `gemma3:4b`
   - Larger models more accurate: `llama3.2`, `mistral`

3. **Database Optimization**
   - Use named volumes (faster than bind mounts)
   - Clear old data periodically

4. **Network**
   - Use internal Docker network (automatic)
   - No need for external network access

## File Structure in Container

```
/app/
├── app.py
├── requirements.txt
├── config/
├── utils/
├── components/
├── db_logs/      (volume mount)
├── db_kb/        (volume mount)
└── logs/         (volume mount)
```

## Persistence

Your data persists in Docker volumes:
- **db_logs**: Log embeddings
- **db_kb**: Knowledge base embeddings
- **ollama_data**: Downloaded models

These survive container restarts but are removed with `docker-compose down -v`.

## Next Steps

After starting, see [README.md](README.md) for usage instructions.

Happy log analyzing! 🕵️
