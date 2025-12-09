import streamlit as st
import os
from dotenv import load_dotenv
from src.detection import AmbiguityDetector
from src.resolution import ResolutionPipeline
from ingest import load_initial_knowledge, parse_file

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
    Cached to prevent reloading on every interaction.
    """
    # 1. Load Detection (DeBERTa)
    # Ensure you have the model folder at ./models/deberta_classifier
    detector = AmbiguityDetector(model_path=DETECTION_MODEL_PATH)
    
    # 2. Load Resolution (Gemini + ChromaDB)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ Missing GEMINI_API_KEY in .env file")
        return detector, None
        
    resolver = ResolutionPipeline(vector_db_path=DB_PATH, api_key=api_key)
    
    # 3. Check/Load Static Knowledge (First Run)
    if resolver.collection.count() == 0:
        print("⚡ DB is empty. Loading Static Knowledge...")
        docs, ids, metas = load_initial_knowledge(STATIC_KNOWLEDGE_PATH)
        if docs:
            resolver.add_knowledge(docs, ids, metas)
            print(f"✅ Loaded {len(docs)} static documents.")
            
    return detector, resolver

# Initialize Everything
with st.spinner("🚀 Starting AI Engines..."):
    detector, resolver = load_models()

# --- SIDEBAR: KNOWLEDGE MANAGEMENT ---
with st.sidebar:
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
                    # Save locally
                    save_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Parse & Add
                    docs, ids, metas = parse_file(save_path)
                    if docs:
                        resolver.add_knowledge(docs, ids, metas)
                        new_docs_count += len(docs)
                
                if new_docs_count > 0:
                    st.success(f"Successfully added {new_docs_count} chunks!")
                else:
                    st.warning("No valid text found in files.")

    st.divider()
    if resolver:
        st.caption(f"Total Documents in DB: {resolver.collection.count()}")

# --- MAIN UI ---
st.title("🛡️ SRS Ambiguity Guard")
st.markdown("Enter a software requirement below. The system will first **check for ambiguity**, and if found, use **RAG** to suggest a fix.")

text_input = st.text_area("Requirement to Analyze:", height=100)

if st.button("Analyze & Resolve", type="primary"):
    if not text_input:
        st.warning("Please enter a requirement.")
    else:
        # --- STAGE A: DETECTION ---
        with st.spinner("🔍 Scanning for ambiguity..."):
            # Call the Detector Class
            label, score = detector.predict(text_input)
        
        # --- LOGIC BRANCH ---
        # Note: Check your specific model labels. 
        # Sometimes DeBERTa outputs "LABEL_0" (Clear) and "LABEL_1" (Ambiguous)
        if label in ["Clear", "Clean", "LABEL_0"]:
            st.success(f"✅ **Requirement is Clear** (Confidence: {score:.2%})")
            st.balloons()
            
        else:
            st.error(f"⚠️ **Ambiguity Detected** (Confidence: {score:.2%})")
            
            # --- STAGE B: RESOLUTION ---
            if resolver:
                with st.spinner("🧠 Consulting Knowledge Base & Rewriting..."):
                    rewrite, evidence = resolver.resolve_ambiguity(text_input)
                
                # Display Results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("💡 Suggested Rewrite")
                    st.info(rewrite)
                    
                with col2:
                    st.subheader("📚 Evidence Used")
                    for item in evidence:
                        source = item.get('source', 'Unknown')
                        type_ = item.get('type', 'General').upper()
                        # Handle location logic
                        if 'page' in item: loc = f"Page {item['page']}"
                        elif 'row' in item: loc = f"Row {item['row']}"
                        elif 'item' in item: loc = f"Item {item['item']}"
                        elif 'chunk' in item: loc = f"Chunk {item['chunk']}"
                        else: loc = "Full Doc"
                            
                        with st.expander(f"{source} ({type_})"):
                            st.caption(f"Location: {loc}")
            else:
                st.error("Resolution engine is not loaded. Check API Key.")