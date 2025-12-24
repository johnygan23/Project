"""Sidebar UI components."""
import os
import streamlit as st
from src.ingestion import parse_file


def render_sidebar(resolver, upload_dir):
    """Render the sidebar with settings, help, and knowledge base management."""
    with st.sidebar:
        st.header("⚙️ Settings")
        
        st.divider()
        
        # Detection Settings
        with st.expander("🔍 Detection Settings", expanded=False):
            show_confidence_scores = st.toggle("Show Confidence Scores", value=True)
        
        # Resolution Settings
        with st.expander("✏️ Resolution Settings", expanded=False):
            show_explanation = st.toggle(
                "Show AI Explanation",
                value=True,
                help="Turn off to get just the rewritten text."
            )
            comparison_view = st.toggle(
                "Side-by-Side Comparison",
                value=False,
                help="Show original and rewrite side-by-side"
            )
        
        st.divider()
        
        # Help Section
        with st.expander("❓ Help & Documentation", expanded=False):
            st.markdown("""
            ### Quick Guide
            1. **Enter requirements** in the text area (one per sentence)
            2. **Click "Analyze Batch"** to process all requirements
            3. **Review results** with suggested rewrites
            4. **Export results** if needed
            
            ### Tips
            - Use clear, complete sentences
            - One requirement per sentence works best
            - Upload domain-specific documents for better results
            - Use the preview to verify sentence splitting
            
            ### Batch Processing
            - Upload SRS documents (PDF, TXT, DOCX)
            - System will extract and analyze all requirements
            - Results can be exported as a report
            
            ### Understanding Results
            - **Clear**: Requirement is unambiguous
            - **Ambiguous**: Needs clarification/rewrite
            - **Confidence**: Model's certainty (higher = more reliable)
            - **Evidence**: Knowledge base sources used for rewrite
            """)
        
        st.divider()
        
        st.header("📚 Knowledge Base")
        
        if resolver:
            total_docs = resolver.collection.count()
            st.metric("Total Chunks", total_docs)
            
            if total_docs == 0:
                st.warning("⚠️ Knowledge base is empty. Upload documents to improve results.")
        
        # File Uploader for Knowledge Base
        uploaded_files = st.file_uploader(
            "Upload Custom Documents", 
            type=["pdf", "json", "txt"], 
            accept_multiple_files=True,
            help="Upload documents to enhance the knowledge base"
        )
        
        if uploaded_files:
            if st.button("Process & Ingest"):
                try:
                    with st.spinner("Ingesting files..."):
                        new_docs_count = 0
                        errors = []
                        for uploaded_file in uploaded_files:
                            try:
                                save_path = os.path.join(upload_dir, uploaded_file.name)
                                with open(save_path, "wb") as f:
                                    f.write(uploaded_file.getbuffer())
                                
                                docs, ids, metas = parse_file(save_path)
                                if docs:
                                    resolver.add_knowledge(docs, ids, metas)
                                    new_docs_count += len(docs)
                            except Exception as e:
                                errors.append(f"{uploaded_file.name}: {str(e)}")
                        
                        if new_docs_count > 0:
                            st.success(f"✅ Successfully added {new_docs_count} chunks!")
                        if errors:
                            for error in errors:
                                st.error(f"❌ {error}")
                except Exception as e:
                    st.error(f"❌ Ingestion failed: {str(e)}")
                    st.exception(e)
        
        # Return settings
        return {
            'show_explanation': show_explanation,
            'comparison_view': comparison_view,
            'show_confidence_scores': show_confidence_scores,
        }

