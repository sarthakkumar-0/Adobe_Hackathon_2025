# PDF Section Relevance Extractor

This project extracts **relevant sections and paragraphs** from PDF documents based on a user's persona and job-to-be-done context. It uses Sentence-BERT embeddings to rank sections and paragraphs by semantic similarity.

---

## Features

- Parses PDFs into logical **sections** and **paragraphs**.
- Uses **sentence-transformers** to compute semantic relevance.
- Ranks:
  - Top 5 relevant **sections**.
  - Top 5 **subsections/paragraphs**.
- Outputs results as structured **JSON**.

---

## Directory Structure

```
/app
 ├── input/
 │   ├── *.pdf           # Input PDF files
 │   └── config.json     # Configuration with persona/job/documents
 ├── output/
 │   └── output.json     # Extracted relevant sections and paragraphs
 └── 1_B_sollution.py
```

---

## Requirements

- Python 3.7+
- PyMuPDF
- NumPy
- scikit-learn
- sentence-transformers

Install with:

```bash
pip install -r requirement_1_b.txt.txt
```

---

## Usage

### Standalone Script

Place PDFs and `config.json` in the `input/` directory. Then run:

```bash
python 1_B_sollution.py
```

The output will be generated in `output/output.json`.

---

### Docker Setup

#### Build the Docker image

```bash
docker build -f Dockerfile.dockerfile -t pdf-section-extractor .
```

#### Run the container

```bash
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output pdf-section-extractor
```

---

## Output Format

```json
{
  "metadata": {
    "input_documents": ["file1.pdf", "file2.pdf"],
    "persona": "Product Manager",
    "job_to_be_done": "Understand market trends",
    "processing_timestamp": "2025-07-28T14:30:00"
  },
  "extracted_sections": [
    {
      "document": "file1.pdf",
      "section_title": "Introduction",
      "importance_rank": 1,
      "page_number": 2
    }
  ],
  "subsection_analysis": [
    {
      "document": "file1.pdf",
      "refined_text": "This report focuses on...",
      "page_number": 2
    }
  ]
}
```

---

## Contributors

- Sarthak Kumar
- Anoop Mishra

---

## License

This project is intended for internal and educational purposes.