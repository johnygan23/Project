"""Results display UI components."""
import streamlit as st
from datetime import datetime
from src.utils.report import generate_report


def render_results(settings):
    """Render the results display with tabs and detailed views."""
    if not st.session_state.analysis_results:
        return
    
    st.divider()
    st.subheader("📝 Detailed Results")
    
    # Tabs for different views
    tab1, tab2 = st.tabs(["📋 All Results", "🔍 Evidence Summary"])
    
    with tab1:
        _render_all_results(settings)
    
    with tab2:
        _render_evidence_summary()


def _render_all_results(settings):
    """Render all results with detailed information."""
    for idx, result in enumerate(st.session_state.analysis_results, 1):
        with st.container():
            # Header with columns
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### Requirement {idx}")
                st.text(result['sentence'])
            
            with col2:
                if result.get('status') == 'clear':
                    st.success("✅ **Clear**")
                    if settings['show_confidence_scores']:
                        st.caption(f"Confidence: {result['score']:.2%}")
                else:
                    st.error("⚠️ **Ambiguous**")
                    if settings['show_confidence_scores']:
                        st.caption(f"Confidence: {result['score']:.2%}")
            
            # Rewrite Section
            if result.get('rewrite'):
                if settings['comparison_view']:
                    # Side-by-Side Comparison
                    col_orig, col_rewrite = st.columns(2)
                    with col_orig:
                        st.markdown("**Original (Ambiguous)**")
                        st.warning(result['sentence'])
                    with col_rewrite:
                        st.markdown("**Suggested (Clear)**")
                        st.success(result['rewrite'])
                else:
                    st.markdown("**💡 Suggested Rewrite:**")
                    st.info(result['rewrite'])
                
                # Enhanced Evidence Display
                if result.get('evidence'):
                    _render_evidence(result['evidence'])
            
            st.divider()


def _render_evidence(evidence):
    """Render evidence display for a requirement."""
    with st.expander(f"🔍 View Retrieved Context ({len(evidence)} sources)", expanded=False):
        for i, item in enumerate(evidence, 1):
            with st.container():
                col_source, col_type = st.columns([3, 1])
                
                source = item.get('source', 'Unknown')
                content_type = item.get('content_type', item.get('type', 'General'))
                
                with col_source:
                    st.markdown(f"**{i}. {source}**")
                
                with col_type:
                    st.caption(f"Type: {content_type}")
                
                # Location information - handle both page (PDF) and item (JSON) fields
                location_info = []
                if 'page' in item and item.get('page') != 'N/A':
                    location_info.append(f"Page: {item['page']}")
                if 'item' in item:
                    location_info.append(f"Item: {item['item']}")
                if 'chunk_id' in item and item.get('chunk_id') != '':
                    location_info.append(f"Chunk: {item['chunk_id']}")
                
                if location_info:
                    st.caption(" | ".join(location_info))
                
                st.divider()


def _render_evidence_summary():
    """Render evidence summary grouped by source."""
    st.subheader("📚 Evidence Summary")
    all_evidence = []
    for result in st.session_state.analysis_results:
        if result.get('evidence'):
            all_evidence.extend(result['evidence'])
    
    if all_evidence:
        # Group by source
        sources = {}
        for item in all_evidence:
            source = item.get('source', 'Unknown')
            if source not in sources:
                sources[source] = []
            sources[source].append(item)
        
        for source, items in sources.items():
            with st.expander(f"📄 {source} ({len(items)} references)"):
                for item in items:
                    # Get content type
                    content_type = item.get('content_type', item.get('type', 'N/A'))
                    
                    # Get location - handle both page (PDF) and item (JSON) fields
                    location_parts = []
                    if 'page' in item and item.get('page') != 'N/A':
                        location_parts.append(f"Page: {item['page']}")
                    if 'item' in item:
                        location_parts.append(f"Item: {item['item']}")
                    if 'chunk_id' in item and item.get('chunk_id') != '':
                        location_parts.append(f"Chunk: {item['chunk_id']}")
                    
                    location_str = " | ".join(location_parts) if location_parts else "N/A"
                    
                    st.caption(f"Type: {content_type} | {location_str}")
    else:
        st.info("No evidence retrieved for ambiguous requirements.")


def render_export_button():
    """Render export download button if results exist."""
    if st.session_state.analysis_results:
        report = generate_report(st.session_state.analysis_results)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="📥 Download Report",
            data=report,
            file_name=f"srs_analysis_{timestamp}.txt",
            mime="text/plain"
        )

