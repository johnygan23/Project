"""Main panel UI components."""
import streamlit as st
from src.utils.text import split_sentences


def render_main_panel():
    """Render the main input panel with batch processing and text input."""
    st.title("🛡️ SRS Ambiguity Guard (Bulk Mode)")
    st.markdown("Enter multiple requirements below. The system will analyze them **sentence-by-sentence**.")
    
    # File Upload for Batch Processing
    st.subheader("📄 Batch Processing")
    batch_file = st.file_uploader(
        "Upload SRS Document for Batch Analysis",
        type=["txt", "pdf"],
        help="Upload a document containing multiple requirements"
    )
    
    # Main Input Area
    text_input = st.text_area(
        "Input Requirements (Paragraph):", 
        height=150, 
        placeholder="The system should be fast. The login screen must display a welcome message.",
        help="Enter requirements separated by periods. Each sentence will be analyzed separately."
    )
    
    # Load text from batch file if uploaded
    if batch_file:
        try:
            if batch_file.type == "text/plain":
                content = batch_file.read().decode("utf-8")
                text_input = content
                st.success(f"✅ Loaded {len(content)} characters from {batch_file.name}")
            elif batch_file.type == "application/pdf":
                # For PDF, we'd need to extract text
                st.info("PDF extraction will be added. Please use TXT files for now.")
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
    
    # Input Validation and Preview
    if text_input:
        sentences = split_sentences(text_input)
        with st.expander("📋 Preview Sentences", expanded=False):
            st.info(f"Found {len(sentences)} sentence(s) to analyze:")
            for i, sent in enumerate(sentences, 1):
                st.text(f"{i}. {sent}")
    
    return text_input


def render_action_buttons():
    """Render action buttons for analysis, clear, export, and stop."""
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        analyze_btn = st.button("🔍 Analyze Batch", type="primary", use_container_width=True)
    with col2:
        clear_btn = st.button("🗑️ Clear Results", use_container_width=True)
    with col3:
        export_btn = st.button("📥 Export Results", use_container_width=True, 
                               disabled=len(st.session_state.analysis_results) == 0)
    with col4:
        stop_btn_clicked = st.button("⏹️ Stop Processing", use_container_width=True)
        if stop_btn_clicked:
            st.session_state.processing_stopped = True
            st.warning("⏹️ Stop requested. Processing will stop after current requirement.")
    
    return analyze_btn, clear_btn, export_btn


def render_summary_statistics():
    """Render summary statistics if results exist."""
    if not st.session_state.analysis_results:
        return
    
    st.divider()
    st.subheader("📊 Summary Statistics")
    
    total = len(st.session_state.analysis_results)
    clear_count = sum(1 for r in st.session_state.analysis_results 
                     if r.get('label') in ['Clear', 'Clean', 'LABEL_0'])
    ambiguous_count = total - clear_count
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Requirements", total)
    with col2:
        st.metric("✅ Clear", clear_count, delta=None)
    with col3:
        st.metric("⚠️ Ambiguous", ambiguous_count, delta=None)
    with col4:
        ambiguity_rate = (ambiguous_count / total * 100) if total > 0 else 0
        st.metric("Ambiguity Rate", f"{ambiguity_rate:.1f}%")
    
    st.divider()

