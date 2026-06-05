@echo off
REM Log Analysis AI Toolkit - Docker Runner for Windows

echo.
echo 🚀 Starting Log Analysis AI Toolkit with Docker...
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop for Windows first.
    echo Visit: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Desktop (includes Docker Compose).
    pause
    exit /b 1
)

echo 📋 Configuration:
echo   - Ollama API: http://localhost:11434
echo   - Streamlit UI: http://localhost:8501
echo   - Database volumes: db_logs, db_kb
echo.

REM Build and start containers
echo 🔨 Building and starting containers...
echo.
docker-compose up --build

echo.
echo ✅ Done! Access the application at http://localhost:8501
pause
