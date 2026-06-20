"""Application configuration and constants."""
import os
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Database paths
DB_LOGS_PATH = str(PROJECT_ROOT / "db_logs")
DB_KB_PATH = str(PROJECT_ROOT / "db_kb")

# Collection names
LOGS_COLLECTION = "log_collection"
KB_COLLECTION = "kb_collection"

# Ollama
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

# Default models
OLLAMA_MODELS = {
    "expert_rca": "llama3:latest",
    "log_summary": "llama3.2:latest",
}

OPENAI_MODELS = {
    "expert_rca": "gpt-4o",
    "log_summary": "gpt-4o-mini",
}

HUGGINGFACE_MODELS = {
    "expert_rca": "meta-llama/Llama-3.1-8B-Instruct",
    "log_summary": "meta-llama/Llama-3.2-1B-Instruct",
}

# Embeddings
EMBEDDING_DEFAULTS = {
    "ollama": "nomic-embed-text",
    "openai": "text-embedding-3-small",
    "huggingface": "sentence-transformers/all-MiniLM-L6-v2",
}

# Text splitting
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100

# Search
SIMILARITY_THRESHOLD = 0.15
MAX_SEARCH_RESULTS = 10

# Temperature
DEFAULT_TEMPERATURE = 0.0
