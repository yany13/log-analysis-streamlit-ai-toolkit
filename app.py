"""Log Analysis AI Tool - Main Application."""
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import streamlit as st
from components.sidebar import render_sidebar
from components.log_analysis_tab import render_log_analysis_tab
from components.knowledge_base_tab import render_knowledge_base_tab
from components.maintenance_tab import render_maintenance_tab
from utils.embeddings import get_embeddings
from utils.llm_engines import get_llm


def initialize_session_state():
    """Initialize session state variables."""
    if 'last_rca' not in st.session_state:
        st.session_state.last_rca = ""


def configure_page():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="Log Analysis Tool",
        layout="wide",
        page_icon="🕵️"
    )


def main():
    """Main application entry point."""
    configure_page()
    initialize_session_state()

    # Render sidebar and get configuration
    config = render_sidebar()

    # Initialize engines based on config
    embed_engine = get_embeddings(
        config["embed_provider"],
        config["embed_model"],
        api_key=config["api_key"]
    )

    expert_llm = lambda prompt: get_llm(
        config["llm_provider"],
        config["expert_model"],
        temperature=config["temperature"],
        api_key=config["api_key"]
    ).invoke(prompt)

    summary_llm = lambda prompt: get_llm(
        config["llm_provider"],
        config["summary_model"],
        temperature=config["temperature"],
        api_key=config["api_key"]
    ).invoke(prompt)

    # Main UI
    st.markdown(
        '<p style="font-size:24px; font-weight:800; color:#007bff;">🕵️ Log Analysis Tool</p>',
        unsafe_allow_html=True
    )

    # Create tabs
    tab1, tab2, tab3 = st.tabs([
        "📄 Log Analysis",
        "📚 Knowledge Base",
        "🛠️ Maintenance"
    ])

    with tab1:
        render_log_analysis_tab(embed_engine, expert_llm, summary_llm)

    with tab2:
        render_knowledge_base_tab(embed_engine)

    with tab3:
        render_maintenance_tab()


if __name__ == "__main__":
    main()
