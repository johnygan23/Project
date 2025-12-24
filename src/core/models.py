"""Model loading and initialization."""
import os
import streamlit as st
from dotenv import load_dotenv
from src.detection import AmbiguityDetector
from src.resolution import ResolutionPipeline
from src.ingestion import load_initial_knowledge


@st.cache_resource
def load_models(static_knowledge_path, db_path, model_path):
    """
    Loads both the Detection Model (CPU) and Resolution Pipeline (API).
    """
    # 1. Load Detection (DeBERTa)
    detector = AmbiguityDetector(model_path=model_path)
    
    # 2. Load Resolution (Gemini + ChromaDB)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ Missing GEMINI_API_KEY in .env file")
        return detector, None
        
    resolver = ResolutionPipeline(vector_db_path=db_path, api_key=api_key)
    
    # 3. Check/Load Static Knowledge (First Run)
    if resolver.collection.count() == 0:
        docs, ids, metas = load_initial_knowledge(static_knowledge_path)
        if docs:
            resolver.add_knowledge(docs, ids, metas)
            
    return detector, resolver

