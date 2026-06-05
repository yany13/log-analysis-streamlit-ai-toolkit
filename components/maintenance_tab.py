"""Maintenance tab component."""
import os
import shutil
import streamlit as st
from config.settings import DB_LOGS_PATH, DB_KB_PATH, LOGS_COLLECTION, KB_COLLECTION
from utils.database import (
    get_chroma_client, get_inventory, delete_collection, delete_from_collection
)


def render_clear_database_section():
    """Render database clearing controls."""
    st.markdown("#### 🗑️ Clear Databases")

    col1, col2 = st.columns(2)

    with col1:
        if st.checkbox("Enable Wipe Logs"):
            if st.button("🗑️ CLEAR LOG DB", use_container_width=True):
                if os.path.exists(DB_LOGS_PATH):
                    shutil.rmtree(DB_LOGS_PATH)
                st.success("Log database cleared!")
                st.rerun()

    with col2:
        if st.checkbox("Enable Wipe KB"):
            if st.button("🗑️ CLEAR KB DB", use_container_width=True):
                if os.path.exists(DB_KB_PATH):
                    shutil.rmtree(DB_KB_PATH)
                st.success("KB database cleared!")
                st.rerun()


def render_inventory_section(db_path, col_name, label):
    """Render inventory display with delete options."""
    st.markdown(f"#### {label} Inventory")

    inventory = get_inventory(db_path, col_name)

    if inventory and inventory.get('metadatas'):
        # Aggregate by source
        inv_dict = {}
        for metadata in inventory['metadatas']:
            source = metadata.get('source', 'unknown')
            inv_dict[source] = inv_dict.get(source, 0) + 1

        # Display with delete buttons
        for filename, count in inv_dict.items():
            col1, col2, col3 = st.columns([6, 2, 2])

            with col1:
                st.markdown(f"**📁 {filename}**")
            with col2:
                st.write(f"{count} recs")
            with col3:
                if st.button("🗑️ Delete", key=f"del_{col_name}_{filename}"):
                    delete_from_collection(
                        db_path,
                        col_name,
                        {"where": {"source": filename}}
                    )
                    st.rerun()
    else:
        st.info(f"No {label.lower()} indexed yet")


def render_maintenance_tab():
    """Render maintenance and database management tab."""
    st.markdown("### 🛠️ Maintenance")

    render_clear_database_section()

    st.divider()

    # Logs inventory
    render_inventory_section(DB_LOGS_PATH, LOGS_COLLECTION, "📄 LOGS")

    st.divider()

    # KB inventory
    render_inventory_section(DB_KB_PATH, KB_COLLECTION, "📚 KB")
