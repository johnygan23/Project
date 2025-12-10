import os
import google.generativeai as genai
from sentence_transformers import SentenceTransformer, CrossEncoder
import chromadb
from rank_bm25 import BM25Okapi

class ResolutionPipeline:
    def __init__(self, vector_db_path, api_key):
        print("Initializing Resolution Pipeline...")
        
        # 1. Load Local Retrieval Models
        self.embed_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        
        # 2. Connect to Database
        self.chroma_client = chromadb.PersistentClient(path=vector_db_path)
        self.collection = self.chroma_client.get_or_create_collection(name="srs_knowledge_base")
        
        # 3. Build Memory Indices (BM25)
        data = self.collection.get()
        self.documents = data['documents'] if data['documents'] else []
        self.metadatas = data['metadatas'] if data['metadatas'] else []
        self.content_to_meta = {doc: meta for doc, meta in zip(self.documents, self.metadatas)}
        
        tokenized_corpus = [doc.lower().split() for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_corpus) if tokenized_corpus else None

        # 4. Connect to Cloud LLM
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        print("✅ Resolution Engine Ready.")

    def add_knowledge(self, documents, ids, metadatas):
        """Adds new docs to DB and updates indices immediately."""
        if not documents: return

        # 1. Add to ChromaDB
        embeddings = self.embed_model.encode(documents).tolist()
        self.collection.add(embeddings=embeddings, documents=documents, ids=ids, metadatas=metadatas)
        
        # 2. Update Local Lists (Memory)
        self.documents.extend(documents)
        self.metadatas.extend(metadatas)
        
        # 3. Update Lookup Map
        self.content_to_meta.update({doc: meta for doc, meta in zip(documents, metadatas)})
        
        # 4. Rebuild Keyword Index (BM25)
        print(f"🔄 Rebuilding BM25 Index with {len(self.documents)} documents...")
        tokenized_corpus = [doc.lower().split() for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_corpus)
        print("✅ Knowledge Base Updated.")

    def retrieve_hybrid(self, query, top_k=10):
        if not self.documents: return []
        
        # Vector Search
        query_vec = self.embed_model.encode([query]).tolist()
        chroma_res = self.collection.query(query_embeddings=query_vec, n_results=top_k)
        vector_docs = chroma_res['documents'][0] if chroma_res['documents'] else []

        # Keyword Search
        tokenized_query = query.lower().split()
        bm25_docs = self.bm25.get_top_n(tokenized_query, self.documents, n=top_k)
        
        # RRF Fusion
        scores = {}
        for rank, doc in enumerate(vector_docs):
            scores[doc] = scores.get(doc, 0) + 1 / (rank + 60)
        for rank, doc in enumerate(bm25_docs):
            scores[doc] = scores.get(doc, 0) + 1 / (rank + 60)
            
        return sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:top_k]

    def resolve_ambiguity(self, text, include_explanation):
        candidates = self.retrieve_hybrid(text)
        if not candidates: return "No relevant context found.", []

        # Re-Ranking
        pairs = [[text, doc] for doc in candidates]
        scores = self.reranker.predict(pairs)
        ranked = sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)
        best_docs = [doc for _, doc in ranked[:5]]
        
        evidence = [self.content_to_meta.get(doc, {}) for doc in best_docs]
        context_str = "\n- ".join(best_docs)

        # --- DYNAMIC PROMPT LOGIC ---
        if include_explanation:
            # Verbose Prompt (Good for learning)
            instructions =  """
                            TASK:
                            1. Explain specifically why the requirement is ambiguous.
                            2. Provide the rewritten requirement clearly.
                            """
        else:
            # Strict Prompt (Good for automation/copy-paste)
            instructions =  """
                            TASK:
                            1. Output ONLY the rewritten requirement sentence.
                            2. Do NOT provide explanations, notes, or introductory text.
                            3. Do NOT use labels like "Rewritten:".
                            """

        # Generate with Gemini
        prompt = f"""
                    You are a QA Specialist. Rewrite the ambiguous requirement to be clear using the context.
                    CONTEXT:
                    {context_str}

                    {instructions}

                    Requirement: "{text}"
                """
        try:
            response = self.model.generate_content(prompt)
            return response.text, evidence
        except Exception as e:
            return f"API Error: {e}", []