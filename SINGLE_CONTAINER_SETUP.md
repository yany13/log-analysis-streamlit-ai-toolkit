# Single Container Setup Guide

## Overview

The Docker setup has been refactored to run **Ollama** and **Streamlit** as sub-services within a **single container**, managed by `supervisord`.

### Previous Architecture (2 Containers)
```
Container 1: Ollama (ollama/ollama:latest)
Container 2: Streamlit App (custom image)
```

### New Architecture (1 Container)
```
Container: log-analyzer
├── Service 1: Ollama (port 11434)
└── Service 2: Streamlit (port 8501)
Both managed by supervisord
```

## How It Works

### Single Container Benefits
- ✅ Simpler deployment and management
- ✅ Shared storage and networking (no cross-container communication)
- ✅ Single health check for both services
- ✅ Easier resource allocation
- ✅ Unified logging
- ✅ Faster inter-service communication

### Service Management

**supervisord** manages both services:
- Monitors service health
- Auto-restarts failed services
- Logs all output
- Handles startup order

## File Structure

```
docker/
├── Dockerfile              # Single multi-service container
├── supervisord.conf        # Supervisor main config
├── ollama.conf            # Ollama service config
├── streamlit.conf         # Streamlit service config
└── docker-compose.yml     # Orchestration (runs one container)

root/
└── docker-compose.yml     # Primary orchestration file
```

## Service Configurations

### Ollama Service
- **Command**: `/usr/bin/ollama serve`
- **Port**: 11434 (internal & exposed)
- **Logs**: `/app/logs/ollama.out.log`, `/app/logs/ollama.err.log`
- **Restart**: Auto-restart on failure
- **User**: root (required for Ollama)

### Streamlit Service
- **Command**: `streamlit run app.py --server.headless=true`
- **Port**: 8501 (internal & exposed)
- **Logs**: `/app/logs/streamlit.out.log`, `/app/logs/streamlit.err.log`
- **Restart**: Auto-restart on failure
- **Priority**: 999 (starts after Ollama)
- **User**: root

## Quick Start

### Windows
```bash
cd log-analysis-streamlit-ai-toolkit
run-docker.bat
```

### macOS/Linux
```bash
cd log-analysis-streamlit-ai-toolkit
chmod +x run-docker.sh
./run-docker.sh
```

### Manual
```bash
cd log-analysis-streamlit-ai-toolkit
docker-compose up --build
```

## Accessing Services

Both services run in the same container:

| Service | URL | Port |
|---------|-----|------|
| Streamlit UI | http://localhost:8501 | 8501 |
| Ollama API | http://localhost:11434 | 11434 |

## Monitoring

### View Container Status
```bash
docker ps
```

Shows single container: `log-analyzer`

### View Service Logs

#### All logs
```bash
docker logs -f log-analyzer
```

#### Follow Streamlit service
```bash
docker logs -f log-analyzer | grep streamlit
```

#### Follow Ollama service
```bash
docker logs -f log-analyzer | grep ollama
```

#### Access inside container
```bash
docker exec -it log-analyzer /bin/bash
supervisorctl status     # View all services
supervisorctl tail ollama
supervisorctl tail streamlit
```

## Service Management Inside Container

### Connect to running container
```bash
docker exec -it log-analyzer /bin/bash
```

### Check supervisor status
```bash
supervisorctl status
```

Output example:
```
ollama                   RUNNING   pid 15, uptime 0:10:24
streamlit                RUNNING   pid 18, uptime 0:10:22
```

### Restart a service
```bash
supervisorctl restart ollama
supervisorctl restart streamlit
```

### Stop/Start services
```bash
supervisorctl stop ollama
supervisorctl start ollama
supervisorctl restart all
```

## Environment Variables

Set in container environment:
- `OLLAMA_URL=http://localhost:11434` - For Streamlit to connect to Ollama
- `OLLAMA_HOST=0.0.0.0:11434` - Ollama bind address
- `PYTHONUNBUFFERED=1` - Real-time Python output

## Storage & Volumes

All data persists via volumes:

```
Volumes:
├── db_logs:/app/db_logs          # Log embeddings
├── db_kb:/app/db_kb              # KB embeddings
├── logs:/app/logs                # Application logs
└── ollama_data:/root/.ollama     # Ollama models
```

## Health Checks

The container includes health check:
```
Status: Checks every 30s
Success: When Streamlit health endpoint responds
Failure: After 3 consecutive failures
Start period: 60s (warm-up time)
```

## Configuration Files

### supervisord.conf
- Main supervisor daemon configuration
- Sets logging, PID file, socket
- Includes service configs from `/etc/supervisor/conf.d/`

### ollama.conf
- Ollama service configuration
- Auto-start and auto-restart settings
- Output redirection to log files
- Environment variables

### streamlit.conf
- Streamlit service configuration
- Higher priority (starts after Ollama)
- Passes command-line arguments
- Output logging

## Building the Image

### Fresh build (no cache)
```bash
docker-compose build --no-cache
```

### View build output
```bash
docker-compose build --verbose
```

## Troubleshooting

### Container won't start
```bash
docker-compose logs log-analyzer
```

### Service not running
```bash
docker exec -it log-analyzer supervisorctl status
```

### Restart stuck service
```bash
docker exec -it log-analyzer supervisorctl restart ollama
docker exec -it log-analyzer supervisorctl restart streamlit
```

### Check service logs
```bash
# Ollama logs
docker exec -it log-analyzer tail -f /app/logs/ollama.out.log

# Streamlit logs
docker exec -it log-analyzer tail -f /app/logs/streamlit.out.log
```

### Models not loading
The container includes Ollama installation, but models must be pulled:
```bash
docker exec -it log-analyzer ollama pull gemma3:4b
docker exec -it log-analyzer ollama pull llama3.2
docker exec -it log-analyzer ollama pull nomic-embed-text
```

### Port conflicts
If ports 8501 or 11434 are in use:
```bash
# Find what's using the ports
lsof -i :8501
lsof -i :11434

# Or modify docker-compose.yml:
ports:
  - "8502:8501"     # Change 8502 if needed
  - "11435:11434"   # Change 11435 if needed
```

## Performance Tips

### Resource Allocation
In Docker Desktop (Windows/macOS):
- Settings → Resources
- Allocate at least 8GB RAM
- Allocate 4+ CPU cores

### Model Selection
- Smaller models: `gemma3:4b`, `nomic-embed-text`
- Larger models: `llama3.2`, `mistral`

### Database Cleanup
```bash
# Inside container
docker exec -it log-analyzer bash
rm -rf /app/db_logs/*
rm -rf /app/db_kb/*
```

## Comparison: Two Containers vs. One Container

| Aspect | Two Containers | One Container |
|--------|---|---|
| Startup Time | Slower (sequential) | Faster (parallel) |
| Communication | Network bridge | Localhost (faster) |
| Resource Usage | Higher (2 images) | Lower (1 image) |
| Complexity | Higher | Lower |
| Networking | Network needed | None needed |
| Logging | Separate | Unified |
| Health Checks | Independent | Unified |
| Scaling | Easier | Not applicable |

## Next Steps

1. **Start the container**
   ```bash
   docker-compose up --build
   ```

2. **Verify both services**
   ```bash
   curl http://localhost:8501/_stcore/health
   curl http://localhost:11434/api/tags
   ```

3. **Pull LLM models**
   ```bash
   docker exec -it log-analyzer ollama pull gemma3:4b
   ```

4. **Access the UI**
   ```
   http://localhost:8501
   ```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│          Docker Container: log-analyzer             │
│  (Python 3.11-slim + Ollama + Streamlit)           │
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │      supervisord (Process Manager)          │  │
│  │                                             │  │
│  │  ┌──────────────────┐  ┌────────────────┐  │  │
│  │  │     Ollama       │  │   Streamlit    │  │  │
│  │  │   Port 11434     │  │  Port 8501     │  │  │
│  │  └──────────────────┘  └────────────────┘  │  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
│  Shared Volumes:                                   │
│  - db_logs (log embeddings)                        │
│  - db_kb (KB embeddings)                           │
│  - logs (application logs)                         │
│  - ollama_data (LLM models)                        │
└─────────────────────────────────────────────────────┘
```

---

**One container. Two services. Simplified management.** 🚀
