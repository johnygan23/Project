import streamlit as st
import os
import re
import time
from dotenv import load_dotenv
from src.detection import AmbiguityDetector
from src.resolution import ResolutionPipeline
from src.ingestion import load_initial_knowledge, parse_file

# --- CONFIGURATION ---
STATIC_KNOWLEDGE_PATH = "./data/static_knowledge"
UPLOAD_DIR = "./data/user_uploads"
DB_PATH = "./data/rag_db"
DETECTION_MODEL_PATH = "./models/deberta_classifier"

# Ensure upload dir exists
os.makedirs(UPLOAD_DIR, exist_ok=True)
load_dotenv() # Load API Key

# --- INITIALIZATION ---
st.set_page_config(page_title="SRS Guard", layout="wide")

@st.cache_resource
def load_models():
    """
    Loads both the Detection Model (CPU) and Resolution Pipeline (API).
    """
    # 1. Load Detection (DeBERTa)
    detector = AmbiguityDetector(model_path=DETECTION_MODEL_PATH)
    
    # 2. Load Resolution (Gemini + ChromaDB)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ Missing GEMINI_API_KEY in .env file")
        return detector, None
        
    resolver = ResolutionPipeline(vector_db_path=DB_PATH, api_key=api_key)
    
    # 3. Check/Load Static Knowledge (First Run)
    if resolver.collection.count() == 0:
        docs, ids, metas = load_initial_knowledge(STATIC_KNOWLEDGE_PATH)
        if docs:
            resolver.add_knowledge(docs, ids, metas)
            
    return detector, resolver

def split_sentences(text):
    """
    Splits text into sentences using regex.
    Matches periods/questions/exclamations followed by space or end of line.
    """
    # This regex looks for sentence terminators (.?!) followed by a space or end-of-string
    sentences = re.split(r'(?<=[.?!])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

# Initialize Everything
with st.spinner("🚀 Starting AI Engines..."):
    detector, resolver = load_models()

# --- SIDEBAR: KNOWLEDGE MANAGEMENT ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Toggle for Explanation
    show_explanation = st.toggle("Show AI Explanation", value=True, 
                                 help="Turn off to get just the rewritten text.")

    st.divider()
    
    st.header("📚 Knowledge Base")
    
    # File Uploader
    uploaded_files = st.file_uploader(
        "Upload Custom Documents", 
        type=["pdf", "json", "txt"], 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button("Process & Ingest"):
            with st.spinner("Ingesting files..."):
                new_docs_count = 0
                for uploaded_file in uploaded_files:
                    save_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    docs, ids, metas = parse_file(save_path)
                    if docs:
                        resolver.add_knowledge(docs, ids, metas)
                        new_docs_count += len(docs)
                
                if new_docs_count > 0:
                    st.success(f"Successfully added {new_docs_count} chunks!")

    st.divider()
    if resolver:
        st.caption(f"Total Documents in DB: {resolver.collection.count()}")

# --- MAIN UI ---
st.title("🛡️ SRS Ambiguity Guard (Bulk Mode)")
st.markdown("Enter multiple requirements below. The system will analyze them **sentence-by-sentence**.")

text_input = st.text_area("Input Requirements (Paragraph):", height=150, placeholder="The system should be fast. The login screen must display a welcome message.")

if st.button("Analyze Batch", type="primary"):
    if not text_input:
        st.warning("Please enter text.")
    else:
        # 1. Split Input
        sentences = split_sentences(text_input)
        st.info(f"Processing {len(sentences)} sentence(s)...")
        
        progress_bar = st.progress(0)
        
        # 2. Process Loop
        for idx, sentence in enumerate(sentences):
            # Update Progress
            progress_bar.progress((idx + 1) / len(sentences))
            
            # Create a container for each sentence
            with st.container():
                st.markdown(f"### Requirement {idx+1}")
                st.text(sentence)
                
                # A. Detection
                label, score = detector.predict(sentence)
                
                # B. Logic Branch
                if label in ["Clear", "Clean", "LABEL_0"]:
                    st.success(f"✅ **Clear** (Confidence: {score:.2%})")
                else:
                    st.error(f"⚠️ **Ambiguity Detected** (Confidence: {score:.2%})")
                    
                    # C. Resolution (Only if Ambiguous)
                    if resolver:
                        with st.spinner(f"Resolving req {idx+1}..."):
                            rewrite, evidence = resolver.resolve_ambiguity(sentence, include_explanation=show_explanation)
                        
                        # Display Rewrite
                        st.markdown("**💡 Suggested Rewrite:**")
                        st.info(rewrite)
                        
                        # Display Evidence
                        with st.expander("🔍 View Retrieved Context"):
                            for item in evidence:
                                source = item.get('source', 'Unknown')
                                type_ = item.get('type', 'General').upper()
                                if 'page' in item: loc = f"Page {item['page']}"
                                elif 'row' in item: loc = f"Row {item['row']}"
                                else: loc = "N/A"
                                    
                                st.markdown(f"**{source}** ({type_}) - `{loc}`")
                                
            st.divider() # Visual separation between sentences