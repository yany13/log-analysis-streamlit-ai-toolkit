FROM ollama/ollama:0.3.6

# Install curl for health checks and bash for entrypoint script
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Copy entrypoint script
COPY docker/ollama-local/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \
    CMD curl -f http://localhost:11434/api/tags || exit 1

# Use custom entrypoint to pull models on startup
ENTRYPOINT ["/entrypoint.sh"]
