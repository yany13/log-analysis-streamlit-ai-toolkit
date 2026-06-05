# Two Service Docker Setup

## Overview

The Log Analysis AI Toolkit is organized as **two independent Docker services** under a single orchestration:

1. **ollama-local** - Ollama LLM server (port 11434)
2. **streamlit-app** - Streamlit web application (port 8501)

Both services are managed by Docker Compose with automatic health checks and service dependencies.

## Folder Structure

```
log-analysis-streamlit-ai-toolkit/
├── docker-compose.yml                 ← Main orchestration (root level)
│
├── docker/
│   ├── ollama-local/
│   │   ├── Dockerfile                ← Ollama service image
│   │   └── .dockerignore
│   │
│   └── streamlit-app/
│       ├── Dockerfile                ← Streamlit service image
│       └── .dockerignore
│
├── app.py
├── requirements.txt
├── config/
├── utils/
├── components/
├── .streamlit/
└── data/
```

## Services

### Service 1: ollama-local

**Purpose:** LLM inference server

```yaml
Service Name: ollama-local
Container Name: log-analysis-ollama
Base Image: ollama/ollama:latest
Port: 11434
Volumes: ollama_data:/root/.ollama
Health Check: curl http://localhost:11434/api/tags
```

**Dockerfile Location:** `docker/ollama-local/Dockerfile`

```dockerfile
FROM ollama/ollama:latest
EXPOSE 11434
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s \
    CMD curl -f http://localhost:11434/api/tags || exit 1
CMD ["ollama", "serve"]
```

### Service 2: streamlit-app

**Purpose:** Web UI for log analysis

```yaml
Service Name: streamlit-app
Container Name: log-analysis-streamlit
Base Image: python:3.11-slim
Port: 8501
Volumes: db_logs, db_kb, logs
Health Check: curl http://localhost:8501/_stcore/health
Dependencies: ollama-local (must be healthy first)
```

**Dockerfile Location:** `docker/streamlit-app/Dockerfile`

```dockerfile
FROM python:3.11-slim
# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
# Copy application
COPY app.py .
COPY config/ ./config/
COPY utils/ ./utils/
COPY components/ ./components/
EXPOSE 8501
CMD ["streamlit", "run", "app.py", ...]
```

## Docker Compose Configuration

**Main File:** `docker-compose.yml` (root level)

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
    networks:
      - log-analysis-network

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
    depends_on:
      ollama-local:
        condition: service_healthy
    networks:
      - log-analysis-network

volumes:
  ollama_data:

networks:
  log-analysis-network:
    driver: bridge
```

## Quick Start

### Build Both Services
```bash
cd log-analysis-streamlit-ai-toolkit
docker-compose build
```

### Start Both Services
```bash
docker-compose up
```

Or in background:
```bash
docker-compose up -d
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ollama-local
docker-compose logs -f streamlit-app
```

### Stop Services
```bash
docker-compose down
```

## Accessing Services

| Service | URL | Purpose |
|---------|-----|---------|
| Streamlit | http://localhost:8501 | Log analysis web UI |
| Ollama API | http://localhost:11434 | LLM inference API |

## Service Communication

**Streamlit → Ollama:**
```
Streamlit container connects to Ollama using:
http://ollama-local:11434

(Service name 'ollama-local' resolves via Docker's internal DNS)
```

## Health Checks

Both services include health checks:

### Ollama Health Check
```
Test: curl -f http://localhost:11434/api/tags
Interval: Every 30 seconds
Timeout: 10 seconds
Start Period: 30 seconds
```

### Streamlit Health Check
```
Test: curl -f http://localhost:8501/_stcore/health
Interval: Every 30 seconds
Timeout: 10 seconds
Start Period: 60 seconds
```

## Service Dependencies

**Startup Order:**
```
1. Docker Compose starts both services in parallel
2. Ollama-local service starts and begins health checks
3. Streamlit-app service waits for ollama-local health check to pass
4. Once Ollama is healthy, Streamlit-app starts
5. Both services running and monitored
```

**Configuration:**
```yaml
streamlit-app:
  depends_on:
    ollama-local:
      condition: service_healthy  # Wait for health check
```

## Managing Services

### View Status
```bash
docker-compose ps
```

Output:
```
NAME                      STATUS              PORTS
log-analysis-ollama       Up (healthy)       0.0.0.0:11434->11434/tcp
log-analysis-streamlit    Up (healthy)       0.0.0.0:8501->8501/tcp
```

### Restart Service
```bash
# Restart specific service
docker-compose restart ollama-local
docker-compose restart streamlit-app

# Restart all
docker-compose restart
```

### Stop Specific Service
```bash
docker-compose stop streamlit-app
docker-compose stop ollama-local
```

### Start Specific Service
```bash
docker-compose start ollama-local
docker-compose start streamlit-app
```

## Volumes

### Shared Between Services

| Volume | Mount Point | Purpose |
|--------|-------------|---------|
| `./db_logs` | `/app/db_logs` | Log embeddings (Streamlit) |
| `./db_kb` | `/app/db_kb` | KB embeddings (Streamlit) |
| `./logs` | `/app/logs` | Application logs (Streamlit) |

### Ollama-Specific

| Volume | Mount Point | Purpose |
|--------|-------------|---------|
| `ollama_data` | `/root/.ollama` | Downloaded LLM models |

## Networking

**Network Name:** `log-analysis-network`

**Type:** Bridge network

**Services Connected:**
- ollama-local
- streamlit-app

**Benefits:**
- Automatic DNS resolution (service name → IP)
- Isolated from host network
- Services can communicate by name
- Clean isolation from other containers

**Service Discovery:**
```
Streamlit can reach Ollama using:
http://ollama-local:11434
```

## Environment Variables

**Set in Streamlit Service:**
```yaml
environment:
  - OLLAMA_URL=http://ollama-local:11434
  - PYTHONUNBUFFERED=1
```

**Ollama Defaults:**
- `OLLAMA_HOST=0.0.0.0:11434` (listens on all interfaces)

## Building Images

### Build Ollama Service Only
```bash
docker-compose build ollama-local
```

### Build Streamlit Service Only
```bash
docker-compose build streamlit-app
```

### Build Without Cache
```bash
docker-compose build --no-cache
```

### View Build Output
```bash
docker-compose build --verbose
```

## Troubleshooting

### Service won't start
```bash
docker-compose logs streamlit-app
docker-compose logs ollama-local
```

### Health check failing
```bash
# Check if service is responsive
curl http://localhost:11434/api/tags
curl http://localhost:8501/_stcore/health
```

### Can't connect between services
```bash
# Verify network
docker network ls
docker network inspect log-analysis-network

# Check service names
docker-compose ps
```

### Rebuild services
```bash
# Clean rebuild
docker-compose build --no-cache
docker-compose down -v
docker-compose up
```

## Port Mapping

```
Host Machine          Docker Network
8501:8501     ←→     streamlit-app:8501
11434:11434   ←→     ollama-local:11434
```

**External Access:**
- Streamlit: http://localhost:8501
- Ollama: http://localhost:11434

**Internal Service Access:**
- Streamlit → Ollama: http://ollama-local:11434

## Resource Management

### View Resource Usage
```bash
docker stats log-analysis-ollama
docker stats log-analysis-streamlit
```

### Limit Resources
Edit `docker-compose.yml`:
```yaml
services:
  ollama-local:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

## Scaling

### Run Multiple Streamlit Instances
```yaml
streamlit-app:
  deploy:
    replicas: 2  # Only works with 'docker stack'
```

Note: For true scaling, use Docker Swarm or Kubernetes

## Networking Modes

Current setup uses **bridge network** (recommended):
- Services isolated from host
- Internal DNS resolution
- Clean separation
- Easy communication between services

## Next Steps

1. **Build Images**
   ```bash
   docker-compose build
   ```

2. **Start Services**
   ```bash
   docker-compose up
   ```

3. **Verify Both Running**
   ```bash
   docker-compose ps
   ```

4. **Pull LLM Models**
   ```bash
   docker exec log-analysis-ollama ollama pull gemma3:4b
   docker exec log-analysis-ollama ollama pull llama3.2
   ```

5. **Access Application**
   ```
   http://localhost:8501
   ```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│               Docker Network (bridge)                   │
│              log-analysis-network                       │
│                                                         │
│  ┌──────────────────────┐  ┌──────────────────────┐   │
│  │  ollama-local        │  │  streamlit-app       │   │
│  │  ┌────────────────┐  │  │  ┌────────────────┐  │   │
│  │  │ Ollama Server  │  │  │  │ Streamlit App  │  │   │
│  │  │ Port 11434     │  │  │  │ Port 8501      │  │   │
│  │  └────────────────┘  │  │  └────────────────┘  │   │
│  │  Health: Checking    │  │  Health: Checking    │   │
│  └──────────────────────┘  └──────────────────────┘   │
│         ▲                              │               │
│         │                              │               │
│         └──────────────────────────────┘               │
│              (Service Dependency)                      │
└─────────────────────────────────────────────────────────┘
         ▼                         ▼
    Port 11434                 Port 8501
   (localhost)               (localhost)
```

---

**Two services. Clean organization. Full Docker Compose management.** 🐳

