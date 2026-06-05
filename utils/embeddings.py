"""Embedding engine initialization."""
from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from config.settings import OLLAMA_URL, EMBEDDING_DEFAULTS


def get_embeddings(provider, model_id, api_key=None):
    """
    Get embedding engine based on provider.

    Args:
        provider: "Ollama", "OpenAI", or "Hugging Face"
        model_id: Model identifier
        api_key: API key for OpenAI

    Returns:
        Embedding function instance
    """
    if provider == "Ollama":
        return OllamaEmbeddings(model=model_id, base_url=OLLAMA_URL)
    elif provider == "OpenAI":
        return OpenAIEmbeddings(model=model_id, openai_api_key=api_key)
    elif provider == "Hugging Face":
        return HuggingFaceEmbeddings(model_name=model_id)
    else:
        raise ValueError(f"Unknown embedding provider: {provider}")


def get_default_embedding_model(provider):
    """Get default embedding model for provider."""
    provider_key = provider.lower().replace(" ", "").replace("huggingface", "huggingface")
    return EMBEDDING_DEFAULTS.get(provider_key, EMBEDDING_DEFAULTS.get("ollama"))
