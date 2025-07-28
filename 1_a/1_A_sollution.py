import fitz
import json
import os
import re
import numpy as np

def extract_headings(pdf_path):
    doc = fitz.open(pdf_path)
    title_candidates = []
    heading_candidates = []
    
    # Extract text blocks with metadata
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text_blocks = page.get_text("dict", sort=True)["blocks"]
        page_width = page.rect.width
        
        for block in text_blocks:
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if not text:
                        continue
                    
                    block_data = {
                        "text": text,
                        "size": span["size"],
                        "page": page_num + 1,
                        "bbox": span["bbox"],
                        "flags": span["flags"],
                        "is_bold": bool(span["flags"] & 2**4)
                    }
                    
                    # Title candidates (first page only)
                    if page_num == 0 and span["bbox"][1] < 100:
                        title_candidates.append(block_data)
                    
                    # Heading candidates (all pages)
                    x_center = (span["bbox"][0] + span["bbox"][2]) / 2
                    is_centered = abs(x_center - page_width/2) < 50
                    is_heading = (
                        len(text.split()) < 15 and 
                        not text.endswith(('.', ':', ';', ',')) and
                        not text.isdigit()
                    )
                    
                    if is_heading and (block_data["is_bold"] or is_centered):
                        heading_candidates.append(block_data)
    
    # Determine title - concatenate top candidates
    title = " ".join([c["text"] for c in sorted(
        title_candidates,
        key=lambda x: (x["bbox"][1], x["bbox"][0])
    )[:3]]).strip()
    
    if not title:
        title = "Untitled"
    
    # Cluster heading font sizes
    if heading_candidates:
        sizes = np.array([c["size"] for c in heading_candidates])
        size_bins = np.histogram_bin_edges(sizes, bins=5)
        size_levels = np.digitize(sizes, size_bins)
        max_level = size_levels.max()
        
        # Create hierarchy map
        level_map = {
            max_level: "H1",
            max_level-1: "H2",
            max_level-2: "H3",
            max_level-3: "H4",
            max_level-4: "H5"
        }
    else:
        level_map = {}
    
    # Process headings with hierarchy
    headings = []
    seen_texts = set()
    
    for i, candidate in enumerate(heading_candidates):
        level = level_map.get(size_levels[i], "H3")
        text = re.sub(r'\s+', ' ', candidate["text"])  # Normalize whitespace
        
        # Skip duplicates and non-headings
        if (text.lower() in seen_texts or 
            len(text) < 2 or 
            text.isdigit() or
            text.lower() in ["page", "continued", "•"]):
            continue
            
        headings.append({
            "level": level,
            "text": text,
            "page": candidate["page"]
        })
        seen_texts.add(text.lower())
    
    # Sort by page and vertical position
    headings.sort(key=lambda x: (x["page"], x["bbox"][1]))
    
    return {
        "title": title[:200],  # Truncate long titles
        "outline": headings
    }

# Process all PDFs in input directory
if __name__ == "__main__":
    input_dir = "/app/input"
    output_dir = "/app/output"
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            result = extract_headings(pdf_path)
            
            output_path = os.path.join(
                output_dir,
                f"{os.path.splitext(filename)[0]}.json"
            )
            
            with open(output_path, "w") as f:
                json.dump(result, f, indent=2)