"""Requirement processing logic."""
import time
import streamlit as st
from src.utils.text import split_sentences


def process_requirements(detector, resolver, text_input, settings):
    """
    Process requirements from text input.
    
    Args:
        detector: AmbiguityDetector instance
        resolver: ResolutionPipeline instance
        text_input: Input text string
        settings: Dictionary with processing settings
    
    Returns:
        tuple: (success: bool, message: str)
    """
    if not text_input:
        return False, "⚠️ Please enter text or upload a document."
    
    st.session_state.processing_stopped = False
    st.session_state.analysis_results = []
    
    # Split Input
    sentences = split_sentences(text_input)
    
    if len(sentences) == 0:
        return False, "⚠️ No sentences detected. Please check your input format."
    
    # Progress tracking
    status_container = st.empty()
    progress_bar = st.progress(0)
    
    start_time = time.time()
    
    # Process Loop
    for idx, sentence in enumerate(sentences):
        # Check for stop
        if st.session_state.processing_stopped:
            st.warning("⏹️ Processing stopped by user.")
            break
        
        # Update Progress
        progress = (idx + 1) / len(sentences)
        progress_bar.progress(progress)
        status_container.info(f"Processing {idx+1}/{len(sentences)}: {sentence[:50]}...")
        
        try:
            # Detection
            label, score = detector.predict(sentence)
            
            result = {
                'sentence': sentence,
                'label': label,
                'score': score,
                'rewrite': None,
                'evidence': []
            }
            
            # Logic Branch
            if label in ["Clear", "Clean", "LABEL_0"]:
                result['status'] = 'clear'
            else:
                result['status'] = 'ambiguous'
                
                # Resolution (Only if Ambiguous)
                if resolver:
                    try:
                        rewrite, evidence = resolver.resolve_ambiguity(
                            sentence,
                            include_explanation=settings['show_explanation']
                        )
                        result['rewrite'] = rewrite
                        # Use a fixed number of evidence items to display
                        max_evidence_items = 5
                        result['evidence'] = evidence[:max_evidence_items] if evidence else []
                    except Exception as e:
                        st.error(f"❌ Resolution failed for requirement {idx+1}: {str(e)}")
                        result['rewrite'] = f"Error: {str(e)}"
            
            st.session_state.analysis_results.append(result)
            
        except Exception as e:
            st.error(f"❌ Error processing requirement {idx+1}: {str(e)}")
            st.exception(e)
            result = {
                'sentence': sentence,
                'label': 'Error',
                'score': 0.0,
                'rewrite': None,
                'evidence': [],
                'error': str(e)
            }
            st.session_state.analysis_results.append(result)
    
    # Clear progress indicators
    progress_bar.empty()
    status_container.empty()
    
    elapsed_time = time.time() - start_time
    return True, f"✅ Analysis complete! Processed {len(st.session_state.analysis_results)} requirements in {elapsed_time:.2f} seconds."

