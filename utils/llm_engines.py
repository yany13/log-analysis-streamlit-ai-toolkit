"""LLM engine initialization."""
import requests
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
import streamlit as st
from config.settings import OLLAMA_URL


@st.cache_data(ttl=30)
def get_ollama_models():
    """Fetch available models from Ollama."""
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        if resp.status_code == 200:
            return [m['name'] for m in resp.json().get('models', [])]
    except Exception:
        pass
    return []


def get_llm(provider, model_id, temperature=0.0, api_key=None):
    """
    Get LLM instance based on provider.

    Args:
        provider: "Ollama (Local)" or "OpenAI"
        model_id: Model identifier
        temperature: Temperature parameter
        api_key: API key for OpenAI

    Returns:
        LLM instance
    """
    if provider == "Ollama (Local)":
        return ChatOllama(
            model=model_id,
            base_url=OLLAMA_URL,
            temperature=temperature
        )
    elif provider == "OpenAI":
        return ChatOpenAI(
            model=model_id,
            api_key=api_key,
            temperature=temperature
        )
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
