# Two Service Docker Architecture - Final Setup ✅

## Complete Structure

```
log-analysis-streamlit-ai-toolkit/
│
├── docker-compose.yml                 ✅ ROOT LEVEL - Main orchestration
│
├── docker/
│   ├── ollama-local/                 ✅ SERVICE 1: Ollama LLM Server
│   │   ├── Dockerfile                   (FROM ollama/ollama:latest)
│   │   └── .dockerignore
│   │
│   └── streamlit-app/                ✅ SERVICE 2: Streamlit Application
│       ├── Dockerfile                   (FROM python:3.11-slim)
│       └── .dockerignore
│
├── app.py
├── requirements.txt
├── config/
├── utils/
├── components/
├── .streamlit/
├── data/
└── [Documentation files]
```

## Two Services

### Service 1: ollama-local
```
Dockerfile: docker/ollama-local/Dockerfile
Base Image: ollama/ollama:latest
Container: log-analysis-ollama
Port: 11434
Purpose: LLM Inference Server
Volume: ollama_data:/root/.ollama
```

**Dockerfile:**
```dockerfile
FROM ollama/ollama:latest
EXPOSE 11434
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s \
    CMD curl -f http://localhost:11434/api/tags || exit 1
CMD ["ollama", "serve"]
```

### Service 2: streamlit-app
```
Dockerfile: docker/streamlit-app/Dockerfile
Base Image: python:3.11-slim
Container: log-analysis-streamlit
Port: 8501
Purpose: Web Application UI
Volumes: db_logs, db_kb, logs
```

**Dockerfile:**
```dockerfile
FROM python:3.11-slim
# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
# Copy application code
COPY app.py .
COPY config/ ./config/
COPY utils/ ./utils/
COPY components/ ./components/
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.headless=true"]
```

## Docker Compose (Root Level)

**File:** `docker-compose.yml`

```yaml
version: '3.8'

services:

  ollama-local:
    build:
      context: .
      dockerfile: ./docker/ollama-local/Dockerfile
    container_name: log-analysis-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped
    networks:
      - log-analysis-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3

  streamlit-app:
    build:
      context: .
      dockerfile: ./docker/streamlit-app/Dockerfile
    container_name: log-analysis-streamlit
    ports:
      - "8501:8501"
    volumes:
      - ./db_logs:/app/db_logs
      - ./db_kb:/app/db_kb
      - ./logs:/app/logs
    environment:
      - OLLAMA_URL=http://ollama-local:11434
      - PYTHONUNBUFFERED=1
    depends_on:
      ollama-local:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - log-analysis-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  ollama_data:

networks:
  log-analysis-network:
    driver: bridge
```

## Key Features

### ✅ Two Separate Services
- Independent containers
- Proper separation of concerns
- Easy to scale or update individually

### ✅ Clean Folder Organization
```
docker/
├── ollama-local/     (Ollama service)
└── streamlit-app/    (Streamlit service)
```

### ✅ Single Orchestration
- One `docker-compose.yml` at root
- Manages both services
- Defines networking, volumes, dependencies

### ✅ Automatic Health Checks
- Both services monitored
- Auto-restart on failure
- Dependency management (Streamlit waits for Ollama)

### ✅ Docker Network
- Bridge network for inter-service communication
- Services communicate via service names
- Isolated from host network

## Quick Start

### 1. Build Both Services
```bash
cd log-analysis-streamlit-ai-toolkit
docker-compose build
```

### 2. Start Both Services
```bash
docker-compose up
```

Or background:
```bash
docker-compose up -d
```

### 3. Verify Both Running
```bash
docker-compose ps
```

Expected:
```
NAME                      STATUS
log-analysis-ollama       Up (healthy)
log-analysis-streamlit    Up (healthy)
```

### 4. Access Services
```
Streamlit:  http://localhost:8501
Ollama API: http://localhost:11434/api/tags
```

### 5. Pull LLM Models
```bash
docker exec log-analysis-ollama ollama pull gemma3:4b
docker exec log-analysis-ollama ollama pull llama3.2
docker exec log-analysis-ollama ollama pull nomic-embed-text
```

## Service Management

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ollama-local
docker-compose logs -f streamlit-app
```

### Restart Services
```bash
# Specific
docker-compose restart ollama-local
docker-compose restart streamlit-app

# All
docker-compose restart
```

### Stop Services
```bash
# All
docker-compose stop

# Specific
docker-compose stop streamlit-app
docker-compose stop ollama-local
```

### Start Services
```bash
# All
docker-compose start

# Specific
docker-compose start ollama-local
docker-compose start streamlit-app
```

### Remove Everything
```bash
docker-compose down          # Remove containers
docker-compose down -v       # Remove containers and volumes
docker-compose down --rmi all # Remove containers, volumes, images
```

## Networking

**Network Name:** `log-analysis-network`

**Service Discovery:**
```
Streamlit → Ollama
http://ollama-local:11434
```

**Port Mapping:**
```
External          Container
8501 → 8501 (Streamlit)
11434 → 11434 (Ollama)
```

## Volumes

```
./db_logs            (Log embeddings)
./db_kb              (KB embeddings)
./logs               (Application logs)
ollama_data          (LLM models)
```

## Dependencies

**Startup Order:**
```
1. ollama-local starts
2. ollama-local health checks pass
3. streamlit-app starts
4. Both services running and monitored
```

**Configuration in docker-compose.yml:**
```yaml
streamlit-app:
  depends_on:
    ollama-local:
      condition: service_healthy  # Wait for health
```

## Health Checks

### Ollama Health
```bash
curl http://localhost:11434/api/tags
```

### Streamlit Health
```bash
curl http://localhost:8501/_stcore/health
```

## Troubleshooting

### Service won't start
```bash
docker-compose logs ollama-local
docker-compose logs streamlit-app
```

### Port already in use
Edit `docker-compose.yml`:
```yaml
services:
  ollama-local:
    ports:
      - "11435:11434"  # Change 11435 if needed

  streamlit-app:
    ports:
      - "8502:8501"    # Change 8502 if needed
```

### Services can't communicate
```bash
# Check network
docker network ls
docker network inspect log-analysis-network

# Verify service names
docker-compose ps
```

### Rebuild from scratch
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

## Files Reference

### Main Orchestration
- **Root:** `docker-compose.yml` - Defines both services

### Service 1: Ollama
- **Dockerfile:** `docker/ollama-local/Dockerfile`
- **Build Context:** Root directory
- **Base:** `ollama/ollama:latest`

### Service 2: Streamlit
- **Dockerfile:** `docker/streamlit-app/Dockerfile`
- **Build Context:** Root directory
- **Base:** `python:3.11-slim`
- **Dependencies:** Requirements.txt, app code, config

### Documentation
- **[TWO_SERVICE_SETUP.md](TWO_SERVICE_SETUP.md)** - Detailed guide
- **[README.md](README.md)** - Project overview
- **[DOCKER_SETUP.md](DOCKER_SETUP.md)** - General Docker info

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Docker Compose Network: log-analysis-network       │
│                                                     │
│  ┌──────────────────────┐  ┌────────────────────┐  │
│  │  ollama-local        │  │  streamlit-app     │  │
│  │                      │  │                    │  │
│  │ ┌────────────────┐   │  │ ┌────────────────┐ │  │
│  │ │  Ollama        │   │  │ │ Streamlit      │ │  │
│  │ │  Port 11434    │◄──┼──┼─│ Port 8501      │ │  │
│  │ │                │   │  │ │                │ │  │
│  │ └────────────────┘   │  │ └────────────────┘ │  │
│  │                      │  │                    │  │
│  │ Volume:              │  │ Volumes:           │  │
│  │ ollama_data          │  │ db_logs            │  │
│  │                      │  │ db_kb              │  │
│  │                      │  │ logs               │  │
│  └──────────────────────┘  └────────────────────┘  │
│         ▲                              │            │
│         └──────────────────────────────┘            │
│        (Service Dependency & Communication)        │
└─────────────────────────────────────────────────────┘
         ▼                           ▼
    Port 11434                   Port 8501
   (localhost)                  (localhost)
```

## Summary

| Aspect | Details |
|--------|---------|
| **Services** | 2 (ollama-local, streamlit-app) |
| **Containers** | 2 |
| **Orchestration** | 1 docker-compose.yml (root) |
| **Dockerfiles** | 2 (in docker/ subfolders) |
| **Networking** | Bridge network (log-analysis-network) |
| **Health Checks** | Both services have health checks |
| **Dependencies** | Streamlit depends on Ollama |
| **Ports** | 8501 (Streamlit), 11434 (Ollama) |
| **Volumes** | 4 (db_logs, db_kb, logs, ollama_data) |

## Next Steps

1. **Build:**
   ```bash
   docker-compose build
   ```

2. **Start:**
   ```bash
   docker-compose up
   ```

3. **Verify:**
   ```bash
   docker-compose ps
   ```

4. **Use:**
   ```
   http://localhost:8501
   ```

---

**Two separate services. Clean organization. Professional setup.** ✅ 🐳

