"""Sidebar configuration component."""
import streamlit as st
from utils.llm_engines import get_ollama_models
from utils.embeddings import get_default_embedding_model
from config.settings import OLLAMA_MODELS, OPENAI_MODELS, HUGGINGFACE_MODELS


def render_sidebar():
    """Render and configure sidebar, return settings dict."""
    with st.sidebar:
        st.markdown("### 🤖 Model Config")

        # LLM Provider
        llm_provider = st.selectbox(
            "LLM Provider",
            ["Ollama (Local)", "OpenAI", "Hugging Face"]
        )

        # API Key
        api_key = ""
        if llm_provider != "Ollama (Local)":
            api_key = st.text_input("API Key / Token", type="password")

        # LLM Model Selection
        if llm_provider == "Ollama (Local)":
            local_models = get_ollama_models()
            expert_model = st.selectbox(
                "LLM for KB (Expert RCA)",
                local_models if local_models else [OLLAMA_MODELS["expert_rca"]]
            )
            summary_model = st.selectbox(
                "LLM for Logs (Summary)",
                local_models if local_models else [OLLAMA_MODELS["log_summary"]]
            )
        elif llm_provider == "OpenAI":
            expert_model = st.selectbox(
                "LLM for KB",
                ["gpt-4o", "gpt-4o-mini"]
            )
            summary_model = st.selectbox(
                "LLM for Logs",
                ["gpt-4o-mini", "gpt-3.5-turbo"]
            )
        else:  # Hugging Face
            expert_model = st.text_input(
                "Expert ID",
                HUGGINGFACE_MODELS["expert_rca"]
            )
            summary_model = st.text_input(
                "Summary ID",
                HUGGINGFACE_MODELS["log_summary"]
            )

        # Temperature
        temperature = st.slider("Temperature", 0.0, 1.0, 0.0, 0.1)

        st.divider()
        st.markdown("### 🧬 Embedding Engine")

        # Embedding Provider
        embed_provider = st.selectbox(
            "Embed Provider",
            ["Ollama", "OpenAI", "Hugging Face"]
        )

        # Embedding Model
        default_embed = get_default_embedding_model(embed_provider)
        embed_model = st.text_input("Embed ID", default_embed)

        return {
            "llm_provider": llm_provider,
            "expert_model": expert_model,
            "summary_model": summary_model,
            "temperature": temperature,
            "api_key": api_key,
            "embed_provider": embed_provider,
            "embed_model": embed_model,
        }
