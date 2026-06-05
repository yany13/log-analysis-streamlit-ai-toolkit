"""Database operations with ChromaDB."""
import os
import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
import streamlit as st


def get_chroma_client(path):
    """Get ChromaDB persistent client."""
    return chromadb.PersistentClient(
        path=path,
        settings=Settings(allow_reset=True, anonymized_telemetry=False)
    )


@st.cache_data(ttl=30)
def get_vector_store(path, embed_fn, col_name):
    """Get or create a vector store (Chroma + LangChain)."""
    client = get_chroma_client(path)
    return Chroma(
        client=client,
        collection_name=col_name,
        embedding_function=embed_fn
    )


def get_inventory(path, col_name):
    """Get full inventory from a collection."""
    if not os.path.exists(path):
        return {}
    try:
        client = get_chroma_client(path)
        col = client.get_collection(col_name)
        return col.get(include=['metadatas', 'documents'])
    except Exception:
        return {}


def get_file_list(inventory, source_key='source'):
    """Extract unique filenames from inventory metadatas."""
    if not inventory or not inventory.get('metadatas'):
        return []
    return sorted(list(set([m.get(source_key) for m in inventory['metadatas']])))


def delete_collection(path, col_name):
    """Delete entire collection."""
    try:
        client = get_chroma_client(path)
        client.delete_collection(col_name)
        return True
    except Exception:
        return False


def delete_from_collection(path, col_name, where_filter):
    """Delete records matching filter."""
    try:
        client = get_chroma_client(path)
        col = client.get_collection(col_name)
        col.delete(**where_filter)
        return True
    except Exception:
        return False
