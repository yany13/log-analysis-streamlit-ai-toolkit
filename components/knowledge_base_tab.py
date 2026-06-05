"""Knowledge Base tab component."""
import time
import streamlit as st
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import (
    DB_KB_PATH, KB_COLLECTION, CHUNK_SIZE, CHUNK_OVERLAP
)
from utils.database import get_vector_store, get_inventory, get_file_list


def ingest_kb_files(uploaded_files, embed_engine, existing_files):
    """Process and ingest uploaded knowledge base files."""
    new_files = [f for f in uploaded_files if f.name not in existing_files]
    if not new_files:
        return

    with st.status("Indexing KB...") as status:
        db = get_vector_store(DB_KB_PATH, embed_engine, KB_COLLECTION)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )

        for file in new_files:
            status.write(f"Processing {file.name}...")
            content = file.read().decode('utf-8', errors='ignore')
            chunks = splitter.split_text(content)
            db.add_texts(
                chunks,
                metadatas=[{"source": file.name} for _ in chunks]
            )

        status.update(label="Indexing Complete!", state="complete")
        time.sleep(0.5)

    st.rerun()


def render_knowledge_base_tab(embed_engine):
    """Render knowledge base indexing tab."""
    st.markdown("### 📚 Knowledge Base Indexing")

    # Get existing KB files
    kb_inventory = get_inventory(DB_KB_PATH, KB_COLLECTION)
    kb_files = get_file_list(kb_inventory)

    # File uploader for runbooks/docs
    uploaded_kb = st.file_uploader(
        "Upload Runbooks",
        accept_multiple_files=True,
        key="kb_uploader"
    )

    if uploaded_kb:
        ingest_kb_files(uploaded_kb, embed_engine, kb_files)

    # Display stats
    if kb_files:
        st.markdown("#### 📊 Indexed Documents")
        for filename in kb_files:
            st.caption(f"✓ {filename}")
