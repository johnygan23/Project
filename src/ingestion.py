import os
import json
import fitz  # PyMuPDF
import re

def is_low_information_page(text):
    """
    Filters out low-information pages (TOC, headers, footers, references).
    """
    text_lower = text.lower().strip()
    
    # Skip very short pages
    if len(text) < 200:
        return True
    
    # Skip pages that are mostly page numbers, headers, or footers
    lines = text.split('\n')
    non_empty_lines = [l.strip() for l in lines if l.strip()]
    if len(non_empty_lines) < 5:
        return True
    
    # Skip table of contents patterns
    toc_patterns = ['table of contents', 'contents', 'page', 'chapter', 'section']
    if any(pattern in text_lower[:200] for pattern in toc_patterns) and len(text) < 500:
        return True
    
    # Skip reference/bibliography pages
    ref_patterns = ['references', 'bibliography', 'works cited']
    if any(pattern in text_lower[:300] for pattern in ref_patterns):
        return True
    
    return False

def semantic_chunk_pdf(doc, min_chunk_size=200, max_chunk_size=1000):
    """
    Chunks PDF content semantically by paragraphs and sections.
    Attempts to keep related content together.
    """
    chunks, pages_used = [], []
    
    current_chunk = ""
    current_pages = []
    
    for i, page in enumerate(doc):
        text = page.get_text().strip()
        
        # Skip low-information pages
        if is_low_information_page(text):
            continue
        
        # Split page into paragraphs
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
        
        for para in paragraphs:
            # If adding this paragraph would exceed max size, save current chunk
            if current_chunk and len(current_chunk) + len(para) > max_chunk_size:
                if len(current_chunk) >= min_chunk_size:
                    chunks.append((current_chunk, current_pages.copy()))
                current_chunk = ""
                current_pages = []
            
            # Add paragraph to current chunk
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para
            
            if i+1 not in current_pages:
                current_pages.append(i+1)
        
        pages_used.append(i+1)
    
    # Add final chunk if it meets minimum size
    if current_chunk and len(current_chunk) >= min_chunk_size:
        chunks.append((current_chunk, current_pages))
    
    return chunks, pages_used

def parse_file(file_path):
    """
    Parses a SINGLE file and returns documents, ids, metadatas.
    Improved with semantic chunking and content filtering.
    """
    documents, metadatas, ids = [], [], []
    filename = os.path.basename(file_path)
    
    try:
        # --- PDF ---
        if filename.endswith(".pdf"):
            doc = fitz.open(file_path)
            
            # Use semantic chunking instead of page-by-page
            chunks, pages_used = semantic_chunk_pdf(doc)
            
            for idx, (chunk_text, page_nums) in enumerate(chunks):
                documents.append(chunk_text)
                
                # Enhanced metadata
                page_range = f"{min(page_nums)}-{max(page_nums)}" if len(page_nums) > 1 else str(page_nums[0])
                content_type = "standard" if "iso" in filename.lower() or "29148" in filename.lower() else "glossary" if "glossary" in filename.lower() else "document"
                
                metadatas.append({
                    "source": filename,
                    "page": page_range,
                    "type": "pdf",
                    "content_type": content_type,
                    "chunk_id": idx
                })
                ids.append(f"{filename}_chunk_{idx}")
            
            doc.close()
            print(f"  [OK] Processed {filename}: {len(chunks)} semantic chunks from {len(pages_used)} pages")

        # --- JSON (Structured Data) ---
        elif filename.endswith(".json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                items = data if isinstance(data, list) else data.get("items", [])
                
                # Determine content type from filename
                if "rule" in filename.lower():
                    content_type = "ambiguity_rule"
                elif "glossary" in filename.lower():
                    content_type = "glossary_term"
                else:
                    content_type = "structured_data"
                
                for idx, item in enumerate(items):
                    # Create structured text representation
                    if isinstance(item, dict):
                        # For ambiguity rules: create comprehensive text
                        if "rule_id" in item:
                            text_parts = [
                                f"Rule {item.get('rule_id', '')}: {item.get('category', '')}",
                                f"Description: {item.get('description', '')}",
                                f"Bad Examples: {', '.join(item.get('bad_examples', []))}",
                                f"Good Examples: {', '.join(item.get('good_examples', []))}",
                                f"Correction Strategy: {item.get('correction_strategy', '')}"
                            ]
                            text = "\n".join(text_parts)
                        # For glossary: term + definition
                        elif "term" in item and "definition" in item:
                            text = f"{item['term']}: {item['definition']}"
                        else:
                            text = json.dumps(item, ensure_ascii=False)
                    else:
                        text = str(item)
                    
                    documents.append(text)
                    metadatas.append({
                        "source": filename,
                        "item": idx,
                        "type": "json",
                        "content_type": content_type
                    })
                    ids.append(f"{filename}_item_{idx}")

        # --- TXT/MD (Templates) ---
        elif filename.endswith(".txt") or filename.endswith(".md"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
                # Improved chunking: split by template markers, then by size
                # Look for "TEMPLATE:" markers
                template_pattern = r'TEMPLATE:\s*[^\n]+'
                templates = re.split(template_pattern, content)
                
                if len(templates) > 1:
                    # Split by templates
                    template_sections = re.finditer(template_pattern, content)
                    chunk_start = 0
                    chunk_idx = 0
                    
                    for match in template_sections:
                        # Save previous chunk if exists
                        if match.start() > chunk_start:
                            prev_chunk = content[chunk_start:match.start()].strip()
                            if len(prev_chunk) >= 200:
                                documents.append(prev_chunk)
                                metadatas.append({
                                    "source": filename,
                                    "type": "template",
                                    "content_type": "template",
                                    "chunk_id": chunk_idx
                                })
                                ids.append(f"{filename}_chunk_{chunk_idx}")
                                chunk_idx += 1
                        
                        # Extract template section
                        template_end = match.end()
                        # Find next template or end of file
                        next_match = re.search(template_pattern, content[template_end:])
                        if next_match:
                            template_text = content[match.start():template_end + next_match.start()].strip()
                        else:
                            template_text = content[match.start():].strip()
                        
                        if len(template_text) >= 200:
                            documents.append(template_text)
                            metadatas.append({
                                "source": filename,
                                "type": "template",
                                "content_type": "template",
                                "chunk_id": chunk_idx
                            })
                            ids.append(f"{filename}_chunk_{chunk_idx}")
                            chunk_idx += 1
                        
                        chunk_start = template_end + (next_match.start() if next_match else len(content))
                else:
                    # Fallback: chunk by size with overlap
                    chunk_size = 800
                    overlap = 100
                    for i in range(0, len(content), chunk_size - overlap):
                        chunk = content[i:i+chunk_size].strip()
                        if len(chunk) >= 200:
                            documents.append(chunk)
                            metadatas.append({
                                "source": filename,
                                "type": "template",
                                "content_type": "template",
                                "chunk_id": i // (chunk_size - overlap)
                            })
                            ids.append(f"{filename}_chunk_{i // (chunk_size - overlap)}")

    except Exception as e:
        print(f"Error parsing {filename}: {e}")
        import traceback
        traceback.print_exc()

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