# PDF Heading Extractor

This project processes PDF files to extract the **document title** and **headings** based on font size, boldness, and position. It uses PyMuPDF to parse PDF contents and generates a JSON outline for each file.

---

## Features

- Detects the **title** from the top region of the first page.
- Extracts **headings** using:
  - Font size clustering
  - Boldness or horizontal centering
- Outputs a structured **JSON outline** with heading levels (`H1` to `H5`) and page numbers.

---

## Directory Structure

```
/app
 ├── input/     # Place PDF files here
 ├── output/    # Extracted JSON files will be saved here
 └── 1_A_sollution.py
```

---

## Requirements

- Python 3.7+
- PyMuPDF (`fitz`)
- NumPy

Install dependencies:

```bash
pip install -r Requirements.txt
```

If you're using the file you uploaded:

```bash
pip install -r Requirements.txt.txt
```

---

## Usage

### Standalone Script

Place your PDF files in the `input/` directory, then run:

```bash
python 1_A_sollution.py
```

The script will generate corresponding `.json` files in the `output/` directory.

---

### Docker Setup

To build and run using Docker:

#### Build the Docker image

```bash
docker build -f Dockerfile.dockerfile -t pdf-heading-extractor .
```

#### Run the container

```bash
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output pdf-heading-extractor
```

---

## Output Format

Each output JSON file has the following structure:

```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Introduction",
      "page": 1
    },
    ...
  ]
}
```

---
## Contributors

- Sarthak Kumar
- Anoop Mishra

---

## License
This project is for educational and internal use. Adapt freely as needed.