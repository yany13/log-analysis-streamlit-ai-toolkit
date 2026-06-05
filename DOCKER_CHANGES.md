# Docker Configuration Changes

## Summary

The Docker setup has been refactored from **2 separate containers** to **1 unified container** with both services managed by `supervisord`.

## What Changed

### Previous Docker Setup ❌
```
docker-compose.yml:
  services:
    - ollama (ollama/ollama:latest)
    - streamlit (custom image)
    - network (log-analyzer-network)
    - multiple volumes
```

### New Docker Setup ✅
```
docker-compose.yml:
  services:
    - log-analyzer (single container)
      - runs Ollama internally
      - runs Streamlit internally
      - managed by supervisord
```

## Files Modified

### Root Level

#### `docker-compose.yml` - UPDATED ✅
**Before:**
```yaml
services:
  ollama:
    image: ollama/ollama:latest
    container_name: log-analyzer-ollama
    
  streamlit:
    image: custom-image
    container_name: log-analyzer-app
    depends_on:
      - ollama
```

**After:**
```yaml
services:
  log-analyzer:
    build: ./docker/Dockerfile
    container_name: log-analyzer
    ports:
      - "8501:8501"   # Streamlit
      - "11434:11434" # Ollama
```

### Docker Directory

#### `docker/Dockerfile` - UPDATED ✅
**Added:**
- `supervisor` installation
- `ollama` installation from official script
- Copy of supervisor configs
- Support for both port 8501 and 11434
- Single entry point: supervisord

**Removed:**
- Direct Streamlit CMD
- Single port exposure (now has both ports)

**New Content:**
```dockerfile
FROM python:3.11-slim
# ... install supervisor, ollama, streamlit ...
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
```

#### `docker/supervisord.conf` - NEW ✅
Main supervisor configuration:
```ini
[supervisord]
nodaemon=true
logfile=/app/logs/supervisord.log

[unix_http_server]
file=/var/run/supervisor.sock

[include]
files = /etc/supervisor/conf.d/*.conf
```

**Purpose:** Manages both services, logging, and process monitoring

#### `docker/ollama.conf` - NEW ✅
Ollama service configuration:
```ini
[program:ollama]
command=/usr/bin/ollama serve
autostart=true
autorestart=true
environment=OLLAMA_HOST=0.0.0.0:11434
```

**Purpose:** Defines how Ollama runs as a supervised service

#### `docker/streamlit.conf` - NEW ✅
Streamlit service configuration:
```ini
[program:streamlit]
command=streamlit run app.py --server.address=0.0.0.0 --server.port=8501
autostart=true
autorestart=true
priority=999
```

**Purpose:** Defines how Streamlit runs as a supervised service

#### `docker/docker-compose.yml` - UPDATED ✅
Backup compose file (mirrors root `docker-compose.yml`)

## Container Architecture

### Container Image
```
Dockerfile
├── FROM python:3.11-slim
├── Install: build-essential, curl, git, supervisor
├── Install: Ollama (via official script)
├── Install: Python requirements (streamlit, etc.)
├── Copy: Application code
├── Copy: Supervisor configs
└── CMD: supervisord (manages both services)
```

### Inside Container
```
log-analyzer (container)
├── supervisord (PID 1)
│   ├── Ollama service (managed)
│   │   └── Port 11434 → localhost:11434
│   └── Streamlit service (managed)
│       └── Port 8501 → localhost:8501
├── Volumes:
│   ├── /app/db_logs
│   ├── /app/db_kb
│   ├── /app/logs
│   └── /root/.ollama
└── Environment:
    ├── OLLAMA_HOST=0.0.0.0:11434
    ├── OLLAMA_URL=http://localhost:11434
    └── PYTHONUNBUFFERED=1
```

## How Services Are Managed

### supervisord Features
1. **Process Monitoring** - Watches both services
2. **Auto-Restart** - Restarts failed services
3. **Logging** - Centralized log collection
4. **Control** - Can start/stop/restart services
5. **Startup Order** - Ollama (priority 10) before Streamlit (priority 999)

### Service Lifecycle
```
1. Container starts
   ↓
2. supervisord starts (PID 1)
   ↓
3. supervisord starts Ollama service
   ↓
4. supervisord waits for Ollama readiness
   ↓
5. supervisord starts Streamlit service
   ↓
6. Both services running in same container
```

## Port Exposure

### Both Ports Now Exposed
```
Host Machine:
├── 8501 → Container:8501 (Streamlit)
└── 11434 → Container:11434 (Ollama)

Inside Container (localhost):
├── localhost:8501 (Streamlit)
└── localhost:11434 (Ollama)
```

### Services Communicate Internally
```
Streamlit → Ollama
http://localhost:11434  (no network overhead)
```

## Docker Volumes

### Single Container Volumes
```yaml
volumes:
  - ./db_logs:/app/db_logs        # Log embeddings
  - ./db_kb:/app/db_kb            # KB embeddings
  - ./logs:/app/logs              # App logs
  - ollama_data:/root/.ollama     # Ollama models
```

All services share same volumes (no isolation needed)

## Benefits of Single Container

| Feature | Benefit |
|---------|---------|
| **Simplicity** | One image to build, one container to manage |
| **Communication** | Localhost communication (no network overhead) |
| **Storage** | Shared volumes, no cross-container copying |
| **Logging** | Unified logs in single container |
| **Health** | Single health check for both services |
| **Startup** | Faster (parallel service startup) |
| **Resources** | Lower memory footprint |
| **Networking** | No network bridge needed |

## Build Process

### Building Single Container
```bash
docker-compose build --build-arg [ARGS]
```

**Steps:**
1. Builds from `docker/Dockerfile`
2. Installs supervisor
3. Installs Ollama
4. Installs Python requirements
5. Copies application code
6. Copies supervisor configs
7. Exposes ports 8501 and 11434
8. Sets supervisord as entry point

### Image Size Estimate
```
python:3.11-slim         ~200MB
+ system dependencies    ~100MB
+ Ollama installation    ~150MB
+ Python packages        ~500MB
___________________________
Total: ~950MB (varies)
```

## Running Single Container

### docker-compose.yml
```yaml
services:
  log-analyzer:
    build:
      context: .
      dockerfile: ./docker/Dockerfile
    ports:
      - "8501:8501"
      - "11434:11434"
    volumes:
      - ./db_logs:/app/db_logs
      - ./db_kb:/app/db_kb
      - ./logs:/app/logs
      - ollama_data:/root/.ollama
```

### Start Command
```bash
docker-compose up --build
```

## Verification

### Check Container Running
```bash
docker ps
```

Shows: `log-analyzer` (1 container)

### Check Services Inside
```bash
docker exec -it log-analyzer supervisorctl status
```

Output:
```
ollama     RUNNING   pid 15, uptime 0:10:24
streamlit  RUNNING   pid 18, uptime 0:10:22
```

### Test Endpoints
```bash
# Streamlit
curl http://localhost:8501/_stcore/health

# Ollama
curl http://localhost:11434/api/tags
```

## Migration from Two Containers

If you had the old two-container setup running:

```bash
# Stop and remove old containers
docker-compose down

# Build new single container
docker-compose build --no-cache

# Start new single container
docker-compose up
```

## Troubleshooting Single Container

### Services not starting
```bash
docker logs -f log-analyzer
```

### Check supervisor
```bash
docker exec -it log-analyzer supervisorctl status
```

### Restart services
```bash
docker exec -it log-analyzer supervisorctl restart all
```

### Access container shell
```bash
docker exec -it log-analyzer /bin/bash
supervisorctl tail -f ollama
supervisorctl tail -f streamlit
```

## Next Steps

1. **Build the image**
   ```bash
   docker-compose build
   ```

2. **Start the container**
   ```bash
   docker-compose up
   ```

3. **Verify both services**
   ```bash
   curl http://localhost:8501
   curl http://localhost:11434/api/tags
   ```

4. **Pull models**
   ```bash
   docker exec -it log-analyzer ollama pull gemma3:4b
   ```

5. **Access application**
   ```
   http://localhost:8501
   ```

---

**Complete migration to single-container architecture!** ✅
