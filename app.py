"""
SRS Ambiguity Guard - Main Application
A Streamlit application for detecting and resolving ambiguity in software requirements.
"""
import os
import streamlit as st
from dotenv import load_dotenv
from src.core.models import load_models
from src.core.processing import process_requirements
from src.ui.sidebar import render_sidebar
from src.ui.main_panel import render_main_panel, render_action_buttons, render_summary_statistics
from src.ui.results import render_results, render_export_button

# --- CONFIGURATION ---
STATIC_KNOWLEDGE_PATH = "./data/raw"
UPLOAD_DIR = "./data/user_uploads"
DB_PATH = "./data/rag_db"
DETECTION_MODEL_PATH = "./models/deberta_classifier"

# Ensure upload dir exists
os.makedirs(UPLOAD_DIR, exist_ok=True)
load_dotenv()  # Load API Key

# --- INITIALIZATION ---
st.set_page_config(page_title="SRS Guard", layout="wide", initial_sidebar_state="expanded")

# Initialize session state
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = []
if 'processing_stopped' not in st.session_state:
    st.session_state.processing_stopped = False

# Initialize Models
with st.spinner("🚀 Starting AI Engines..."):
    detector, resolver = load_models(
        STATIC_KNOWLEDGE_PATH,
        DB_PATH,
        DETECTION_MODEL_PATH
    )

# --- SIDEBAR ---
settings = render_sidebar(resolver, UPLOAD_DIR)

# --- MAIN UI ---
text_input = render_main_panel()

# Action Buttons
analyze_btn, clear_btn, export_btn = render_action_buttons()

# Clear Results
if clear_btn:
    st.session_state.analysis_results = []
    st.session_state.processing_stopped = False
    st.rerun()

# Export Results
if export_btn and st.session_state.analysis_results:
    render_export_button()

# Summary Statistics
render_summary_statistics()

# Processing
if analyze_btn:
    success, message = process_requirements(detector, resolver, text_input, settings)
    if success:
        st.success(message)
        st.rerun()
    else:
        st.warning(message)

# Display Results
render_results(settings)
