"""Log Analysis tab component."""
import re
import streamlit as st
from dateutil import parser as date_parser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import (
    DB_LOGS_PATH, LOGS_COLLECTION, SIMILARITY_THRESHOLD, MAX_SEARCH_RESULTS
)
from utils.database import get_vector_store, get_inventory, get_file_list
from utils.pdf_generator import create_pdf_report
from utils.search import web_search


def extract_timestamp(line):
    """Extract unix timestamp from log line."""
    ts_value = 0
    match = re.search(r'(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})', line)
    if match:
        try:
            ts_value = int(date_parser.parse(match.group(0)).timestamp())
        except Exception:
            ts_value = 0
    return ts_value


def ingest_logs(uploaded_files, embed_engine, existing_files):
    """Process and ingest uploaded log files."""
    new_files = [f for f in uploaded_files if f.name not in existing_files]
    if not new_files:
        return

    with st.status("Ingesting logs...") as status:
        db = get_vector_store(DB_LOGS_PATH, embed_engine, LOGS_COLLECTION)

        for file in new_files:
            status.write(f"Processing {file.name}...")
            content = file.read().decode('utf-8', errors='ignore').splitlines()

            batch_texts, batch_metadatas = [], []
            for line in content:
                if not line.strip():
                    continue
                ts = extract_timestamp(line)
                batch_texts.append(line)
                batch_metadatas.append({
                    "source": file.name,
                    "unix_ts": int(ts)
                })

            if batch_texts:
                db.add_texts(batch_texts, metadatas=batch_metadatas)

        status.update(label="Logs ingested!", state="complete")
    st.rerun()


def render_pattern_analysis(log_file, embed_engine, llm_fn):
    """Render pattern analysis section."""
    st.markdown("#### 📊 Pattern Analysis")
    pattern_query = st.text_input(
        "Pattern (e.g. ERROR):",
        key="pattern_input"
    )

    if pattern_query and log_file:
        db = get_vector_store(DB_LOGS_PATH, embed_engine, LOGS_COLLECTION)
        results = db._collection.get(
            where={"source": log_file},
            where_document={"$contains": pattern_query}
        )
        hits = results.get('documents', [])

        st.metric("Total Hits", len(hits))

        if hits and st.button("High level Analysis 🤖", use_container_width=True):
            with st.status("Analyzing pattern hits..."):
                summary = llm_fn(
                    f"Expert summary of log hits in {log_file}: {hits[:20]}"
                ).content
                st.info(summary)


def render_context_explorer(log_file, embed_engine):
    """Render context explorer section."""
    st.markdown("#### 🔍 Context Explorer")
    col1, col2 = st.columns([3, 1])

    with col1:
        context_query = st.text_input("Query details:", key="context_input")
    with col2:
        record_limit = st.number_input("Records", 1, 10, 1)

    if context_query and log_file:
        db = get_vector_store(DB_LOGS_PATH, embed_engine, LOGS_COLLECTION)

        # Try exact match first
        exact = db._collection.get(
            where={"source": log_file},
            where_document={"$contains": context_query},
            limit=record_limit
        )

        if exact.get('documents'):
            for doc in exact['documents']:
                st.markdown(
                    f'<div style="background:#1e1e1e; color:#4caf50; padding:6px; '
                    f'border-radius:4px; font-size:11px; margin-bottom:4px; '
                    f'border-left:3px solid #4caf50;">{doc}</div>',
                    unsafe_allow_html=True
                )
        else:
            # Fall back to semantic search
            semantic = db.similarity_search_with_relevance_scores(
                context_query,
                k=record_limit,
                filter={"source": log_file}
            )
            for doc, score in semantic:
                if score > SIMILARITY_THRESHOLD:
                    st.markdown(
                        f'<div style="background:#1e1e1e; color:#d4d4d4; padding:6px; '
                        f'border-radius:4px; font-size:11px; margin-bottom:4px; '
                        f'border-left:3px solid #007bff;">{doc.page_content}</div>',
                        unsafe_allow_html=True
                    )


def render_rca_section(embed_engine, expert_llm_fn):
    """Render Root Cause Analysis section."""
    with st.expander("🧠 Expert Root Cause Analysis", expanded=True):
        incident_query = st.text_input(
            "Describe the incident for Hybrid correlation:"
        )

        if st.button("🚀 Run Comprehensive RCA") and incident_query:
            with st.status("🔍 Orchestrating Hybrid RCA...") as status:
                # Search logs
                status.write("Searching log history...")
                db_logs = get_vector_store(
                    DB_LOGS_PATH,
                    embed_engine,
                    LOGS_COLLECTION
                )
                log_context = "\n".join([
                    f"[{h.metadata.get('source')}] {h.page_content}"
                    for h in db_logs.similarity_search(incident_query, k=MAX_SEARCH_RESULTS)
                ])

                # Search knowledge base
                status.write("Consulting Knowledge Base...")
                from config.settings import DB_KB_PATH, KB_COLLECTION
                db_kb = get_vector_store(
                    DB_KB_PATH,
                    embed_engine,
                    KB_COLLECTION
                )
                kb_context = "\n".join([
                    h.page_content
                    for h in db_kb.similarity_search(incident_query, k=3)
                ])

                # Web search
                status.write("Searching Web (DuckDuckGo) for external context...")
                web_context = web_search(incident_query)

                # Generate RCA
                status.write("Generating Expert Insights...")
                prompt = (
                    f"RCA Query: {incident_query}\n\n"
                    f"Logs:\n{log_context}\n\n"
                    f"Internal KB:\n{kb_context}\n\n"
                    f"External Web Search:\n{web_context}"
                )
                st.session_state.last_rca = expert_llm_fn(prompt).content
                status.update(label="Hybrid RCA Complete!", state="complete")

        # Display and export RCA
        if st.session_state.get('last_rca'):
            st.markdown(st.session_state.last_rca)
            pdf_data = create_pdf_report(st.session_state.last_rca, incident_query)
            st.download_button(
                "📥 PDF Export",
                data=pdf_data,
                file_name="RCA_Report.pdf"
            )


def render_log_analysis_tab(embed_engine, expert_llm_fn, summary_llm_fn):
    """Render main log analysis tab."""
    st.markdown("### 📄 Log Analysis")

    # Get existing logs
    logs_inventory = get_inventory(DB_LOGS_PATH, LOGS_COLLECTION)
    log_files = get_file_list(logs_inventory)

    # File uploader
    uploaded_logs = st.file_uploader(
        "Upload Logs",
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_logs:
        ingest_logs(uploaded_logs, embed_engine, log_files)

    # Analysis sections
    if log_files:
        selected_file = st.selectbox("📂 Investigation File", log_files)

        col1, col2 = st.columns([1, 2])

        with col1:
            render_pattern_analysis(selected_file, embed_engine, summary_llm_fn)

        with col2:
            render_context_explorer(selected_file, embed_engine)

        st.divider()

    render_rca_section(embed_engine, expert_llm_fn)
