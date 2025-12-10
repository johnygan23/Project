import os
from dotenv import load_dotenv
from src.resolution import ResolutionPipeline
# IMPORT THE LOGIC FROM SRC
from src.ingestion import load_initial_knowledge 

# 1. Setup
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
DB_PATH = "./data/rag_db"
STATIC_PATH = "./data/raw" 

# 2. Initialize Pipeline
print("🚀 Starting Ingestion...")
resolver = ResolutionPipeline(vector_db_path=DB_PATH, api_key=API_KEY)

# 3. Load & Ingest
print(f"📂 Scanning {STATIC_PATH}...")
docs, ids, metas = load_initial_knowledge(STATIC_PATH)

if docs:
    resolver.add_knowledge(docs, ids, metas)
    print(f"🎉 Successfully ingested {len(docs)} documents into {DB_PATH}")
else:
    print("⚠️ No documents found to ingest.")