# MatExtractAI 🧠📄  
**AI-powered Extraction & Validation of Materials Science Research Papers**

MatExtractAI is an end-to-end system that converts unstructured **materials science research PDFs** into **structured, evidence-backed JSON** using deterministic parsing and local LLM-based agents.

The project focuses on **accuracy, traceability, and validation**, making it suitable for scientific data repositories, research automation, and materials informatics.



## Key Features

- Page-wise PDF text extraction
- Automatic section segmentation (Introduction, Methods, Results, etc.)
- Reliable table extraction and cleaning
- Domain-specific LLM agents:
  - Mechanical Properties
  - Alloy Composition
  - Processing Routes
  - Microstructure
- Evidence-backed validation (Pipeline B)
- Confidence scoring and cross-agent consistency checks
- Fully offline (local LLMs)


## System Architecture

MatExtractAI is built using **two complementary pipelines**.

### 🔹 Pipeline A — Extraction & Structuring
1. PDF ingestion  
2. Page-wise text extraction  
3. Section splitting  
4. Table extraction  
5. Agent-based information extraction  
6. Structured JSON generation  

### 🔹 Pipeline B — Validation & Trust Scoring
7. Evidence matching  
8. Numeric and semantic verification  
9. Cross-agent consistency analysis  
10. Final confidence scoring  


## 📂 Project Structure

```
MatExtractAI/
│
├── src/
│   ├── agents/                 # LLM-based extraction agents
│   ├── evaluation/             # Validation & confidence logic
│   ├── utils/                  # Shared utilities
│   ├── main.py                 # Pipeline A runner
│   └── run_pipeline_b.py       # Pipeline B runner
│
├── data/
│   └── raw_pdfs/               # Input research papers
│
├── output/                     # JSON outputs (extraction + validation)
│
├── requirements.txt
├── README.md
└── .gitignore
```


## Example Output

```json
{
  "alloy": "AZ31",
  "avg_grain_size_um": 15,
  "texture": "strong basal texture",
  "final_confidence": "high"
}
```

Each extracted value is linked to **textual evidence** from the paper.

## Tech Stack

- **Python 3.13**
- **PyMuPDF** — PDF text extraction
- **Camelot** — Table extraction
- **regex** — Section parsing
- **Ollama** — Local LLM inference
- **pandas / numpy** — Data handling

> ⚠️ Ghostscript is required for Camelot (system dependency).

## ▶️ How to Run

### 1️. Create virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2️. Install dependencies
```bash
pip install -r requirements.txt
```

### 3️. Run Pipeline A
```bash
python src/main.py
```

### 4️. Run Pipeline B
```bash
python src/run_pipeline_b.py
```

## Why MatExtractAI?

✔ Avoids blind LLM hallucination  
✔ Evidence-aware extraction  
✔ Scientific rigor and validation  
✔ Fully reproducible and offline  


## Future Work

- Multi-paper aggregation
- Knowledge graph export
- Dataset-level validation
- UI dashboard
- Support for other scientific fields