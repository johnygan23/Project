import os
import json
import fitz  # PyMuPDF
import pandas as pd

def parse_file(file_path):
    """
    Parses a SINGLE file and returns documents, ids, metadatas.
    """
    documents, metadatas, ids = [], [], []
    filename = os.path.basename(file_path)
    
    try:
        # --- PDF ---
        if filename.endswith(".pdf"):
            doc = fitz.open(file_path)
            for i, page in enumerate(doc):
                text = page.get_text()
                if len(text) > 50:
                    documents.append(text)
                    metadatas.append({"source": filename, "page": i+1, "type": "pdf"})
                    ids.append(f"{filename}_pg{i+1}")

        # --- JSON (Glossary) ---
        elif filename.endswith(".json"):
            with open(file_path, "r") as f:
                data = json.load(f)
                items = data if isinstance(data, list) else data.get("items", [])
                for idx, item in enumerate(items):
                    text = str(item)
                    documents.append(text)
                    metadatas.append({"source": filename, "item": idx, "type": "glossary"})
                    ids.append(f"{filename}_item_{idx}")

        # --- TXT/MD (Templates) ---
        elif filename.endswith(".txt") or filename.endswith(".md"):
            with open(file_path, "r") as f:
                content = f.read()
                # Simple chunking by 1000 chars
                for i in range(0, len(content), 1000):
                    documents.append(content[i:i+1000])
                    metadatas.append({"source": filename, "type": "template"})
                    ids.append(f"{filename}_chunk_{i}")

    except Exception as e:
        print(f"Error parsing {filename}: {e}")

    return documents, ids, metadatas

def load_initial_knowledge(folder_path):
    """Scans a folder and returns all data (Used for Static Knowledge)."""
    all_docs, all_ids, all_metas = [], [], []
    
    if not os.path.exists(folder_path):
        return [], [], []

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            docs, ids, metas = parse_file(file_path)
            all_docs.extend(docs)
            all_ids.extend(ids)
            all_metas.extend(metas)
            
    return all_docs, all_ids, all_metas