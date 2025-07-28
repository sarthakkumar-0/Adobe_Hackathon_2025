import json
import os
import re
import time
import fitz
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Configuration
MODEL_NAME = "all-MiniLM-L6-v2"
MAX_SECTIONS = 5
MAX_SUBSECTIONS = 5
MAX_TEXT_LENGTH = 500

def extract_sections(pdf_path):
    """Extract meaningful sections from PDF with context awareness"""
    doc = fitz.open(pdf_path)
    sections = []
    current_section = {"title": "", "content": "", "page": 1}
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text", sort=True)
        
        # Split into logical sections
        chunks = re.split(r'\n\s*(?=[A-Z][A-Za-z\s]{10,}[:]?$)', text)
        
        for chunk in chunks:
            if not chunk.strip():
                continue
                
            # Identify section titles (capitalized phrases at start)
            title_match = re.match(r'^([A-Z][A-Za-z\s\-]{10,}[:]?)\s*', chunk)
            title = title_match.group(1).strip() if title_match else "Untitled Section"
            
            content = chunk[len(title):].strip() if title_match else chunk.strip()
            
            # Handle multi-line titles
            if '\n' in title:
                title_lines = title.split('\n')
                title = title_lines[0]
                content = '\n'.join(title_lines[1:]) + '\n' + content
            
            sections.append({
                "title": title,
                "content": content,
                "page": page_num + 1
            })
    
    return sections

def process_documents(input_dir, config):
    """Process documents and rank sections by relevance"""
    persona_job = f"{config['persona']}: {config['job']}"
    model = SentenceTransformer(MODEL_NAME)
    persona_embedding = model.encode([persona_job])
    
    all_sections = []
    all_paragraphs = []
    
    # Process each document
    for doc_info in config["documents"]:
        doc_path = os.path.join(input_dir, doc_info["filename"])
        if not os.path.exists(doc_path):
            continue
            
        sections = extract_sections(doc_path)
        for section in sections:
            # Encode section title + content
            section_text = f"{section['title']}: {section['content']}"
            embedding = model.encode([section_text])
            similarity = cosine_similarity(embedding, persona_embedding)[0][0]
            
            all_sections.append({
                "document": doc_info["filename"],
                "title": section["title"],
                "content": section["content"],
                "page": section["page"],
                "similarity": similarity
            })
            
            # Extract paragraphs for subsection analysis
            paragraphs = re.split(r'\n\s*\n', section["content"])
            for para in paragraphs:
                if para.strip() and len(para) > 20:  # Filter short paragraphs
                    para_embedding = model.encode([para])
                    para_similarity = cosine_similarity(para_embedding, persona_embedding)[0][0]
                    
                    all_paragraphs.append({
                        "document": doc_info["filename"],
                        "text": para,
                        "page": section["page"],
                        "similarity": para_similarity
                    })
    
    # Rank sections and paragraphs
    all_sections.sort(key=lambda x: x["similarity"], reverse=True)
    all_paragraphs.sort(key=lambda x: x["similarity"], reverse=True)
    
    # Prepare final outputs
    extracted_sections = []
    for i, sec in enumerate(all_sections[:MAX_SECTIONS], 1):
        extracted_sections.append({
            "document": sec["document"],
            "section_title": sec["title"],
            "importance_rank": i,
            "page_number": sec["page"]
        })
    
    subsection_analysis = []
    for para in all_paragraphs[:MAX_SUBSECTIONS]:
        refined_text = para["text"][:MAX_TEXT_LENGTH]
        if len(para["text"]) > MAX_TEXT_LENGTH:
            refined_text += "..."
            
        subsection_analysis.append({
            "document": para["document"],
            "refined_text": refined_text,
            "page_number": para["page"]
        })
    
    return extracted_sections, subsection_analysis

if __name__ == "__main__":
    # Load configuration
    input_dir = "/app/input"
    config_path = os.path.join(input_dir, "config.json")
    
    with open(config_path) as f:
        config_data = json.load(f)
    
    config = {
        "persona": config_data["persona"]["role"],
        "job": config_data["job_to_be_done"]["task"],
        "documents": config_data["documents"]
    }
    
    # Process documents
    start_time = time.time()
    extracted_sections, subsection_analysis = process_documents(input_dir, config)
    processing_time = time.time() - start_time
    
    # Prepare output
    output = {
        "metadata": {
            "input_documents": [doc["filename"] for doc in config["documents"]],
            "persona": config["persona"],
            "job_to_be_done": config["job"],
            "processing_timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }
    
    # Save output
    with open("/app/output/output.json", "w") as f:
        json.dump(output, f, indent=2)