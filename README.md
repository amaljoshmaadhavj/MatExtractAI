# MatExtractAI

> **AI-powered Extraction & Validation of Materials Science Research Papers**

[![Python Version](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)](https://github.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Last Updated](https://img.shields.io/badge/Updated-2026-blue.svg)]()

## Overview

MatExtractAI is an **end-to-end intelligent system** that transforms unstructured **materials science research PDFs** into **structured, evidence-backed JSON** using a combination of deterministic parsing and local LLM-based agents.

With a focus on **scientific rigor, traceability, and reproducibility**, MatExtractAI is purpose-built for:
- Research data repositories
- Automated research pipelines  
- Materials informatics platforms
- Cross-paper meta-analysis



## Key Features

| Feature | Description |
|---------|-------------|
| **Intelligent PDF Processing** | Page-wise extraction with automatic section segmentation (Intro, Methods, Results, etc.) |
| **Table Intelligence** | Reliable extraction, cleaning, and validation of research tables |
| **Domain-Specific Agents** | 4 specialized LLM agents for mechanical properties, composition, processing, & microstructure |
| **Evidence Validation** | All extracted claims linked to exact textual evidence with confidence scoring |
| **100% Offline** | Uses local LLMs via Ollama - no cloud dependencies, complete data privacy |
| **Cross-Agent Verification** | Consistency checks between multiple agents for enhanced accuracy |
| **Scientific Rigor** | Deterministic parsing + semantic validation for reproducible results |


## System Architecture

MatExtractAI employs a **dual-pipeline approach** for extraction and validation:

### Pipeline A — Extraction & Structuring
A deterministic multi-stage pipeline that converts PDFs into structured JSON:

```
Research PDF 
    ↓
[1] PDF Ingestion & Page Extraction
    ↓
[2] Text Normalization & Page-wise Processing
    ↓
[3] Automatic Section Segmentation
    ↓
[4] Table Detection & Extraction
    ↓
[5] Domain-Specific Agent Processing
    ├─→ Mechanical Properties Agent
    ├─→ Alloy Composition Agent
    ├─→ Processing Routes Agent
    └─→ Microstructure Agent
    ↓
[6] Structured JSON Output
```

### Pipeline B — Validation & Trust Scoring
Applies rigorous validation logic to ensure scientific accuracy:

```
Extracted JSON
    ↓
[7] Evidence Extraction & Linking
    ↓
[8] Numeric Range Validation
    ↓
[9] Semantic Consistency Analysis
    ↓
[10] Cross-Agent Agreement Scoring
    ↓
Final Output with Confidence Metrics
```  


## 📂 Project Structure

```
MatExtractAI/
│
├── 📁 src/                      # Core source code
│   ├── agents/                  # 🧠 LLM extraction agents (composition, mechanics, etc.)
│   ├── evaluation/              # ✅ Validation & confidence scoring logic
│   ├── ingest/                  # 📥 PDF ingestion & preprocessing
│   ├── utils/                   # 🔧 Shared utilities & helpers
│   ├── main.py                  # ⚡ Pipeline A entrypoint
│   └── run_pipeline_b.py        # 🔍 Pipeline B validation runner
│
├── 📁 data/
│   └── raw_pdfs/                # 📄 Input research papers (PDF format)
│
├── 📁 output/                   # 📊 Generated structured outputs
│   ├── *_page_text.json         # Raw text extraction
│   ├── *_sections.json          # Section segmentation
│   ├── *_tables.json            # Table extraction
│   ├── *_*_agent.json           # Agent-specific extractions
│   ├── *_evaluated.json         # Pipeline B validation results
│   └── *.csv                    # Cleaned table exports
│
├── requirements.txt             # 📦 Python dependencies
├── README.md                    # 📖 This file
└── .gitignore                   # 🚫 Git ignores
```


## Example Output

**Input:** Research PDF on magnesium alloy processing  
**Output:** Structured, validated material property data

```json
{
  "alloy_name": "AZ31",
  "composition": {
    "Al": "3%",
    "Zn": "1%",
    "evidence": "Table 1, page 2"
  },
  "avg_grain_size_um": 15,
  "grain_size_evidence": "SEM analysis, Section 3.2",
  "texture": "strong basal texture",
  "processing_route": "hot rolling followed by annealing",
  "mechanical_properties": {
    "yield_strength_MPa": 85,
    "ultimate_tensile_strength_MPa": 235
  },
  "final_confidence": "high",
  "agent_agreements": {
    "composition_agent": "confirmed",
    "microstructure_agent": "confirmed",
    "mechanics_agent": "confirmed"
  }
}
```

**Key insight:** Every extracted value is **linked to evidence** with transparency scores from multiple validation agents.

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Language** | Python 3.13+ | Core implementation |
| **PDF Processing** | PyMuPDF (fitz) | Fast, reliable text extraction |
| **Table Extraction** | Camelot-py | Intelligent table detection & parsing |
| **Pattern Matching** | regex | Deterministic section/entity parsing |
| **LLM Inference** | Ollama | Local, private LLM execution |
| **Data Processing** | pandas, numpy | Validation & numerical analysis |
| **Orchestration** | Python asyncio | Parallel agent execution |

> **System Requirements:**
> - Python 3.13+
> - ⚠️ Ghostscript (required by Camelot for advanced table extraction)
> - Ollama installed with LLM models loaded locally

## ▶️ Quick Start Guide

### Prerequisites
- Python 3.13 installed
- Ollama running locally with LLM models loaded
- Ghostscript installed (for table extraction)

### Installation & Execution

#### 1️. Clone & Setup Virtual Environment
```bash
git clone https://github.com/your-org/MatExtractAI.git
cd MatExtractAI

# Create virtual environment
python -m venv .venv

# Activate it
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

#### 2️. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3️. Prepare Input Data
Place your PDF files in the `data/raw_pdfs/` directory:
```bash
cp your_research_paper.pdf data/raw_pdfs/
```

#### 4. Run Pipeline A (Extraction)
```bash
python src/main.py
```
This generates structured JSON files in `output/`

#### 5️. Run Pipeline B (Validation)
```bash
python src/run_pipeline_b.py
```
This adds confidence scores and validation metrics to your extracted data

### Output Files
- `*_page_text.json` — Raw extracted text by page
- `*_sections.json` — Auto-segmented document sections
- `*_tables.json` — Extracted table data
- `*_agent.json` — Agent-specific extractions
- `*_evaluated.json` — Final validated output with confidence scores
- `*.csv` — Cleaned table exports

## Why MatExtractAI?

| Challenge | Traditional LLMs | MatExtractAI |
|-----------|------------------|--------------|
| **Accuracy** | ❌ Prone to hallucination | ✅ Evidence-backed, validated |
| **Traceability** | ❌ Black-box outputs | ✅ All claims linked to source |
| **Privacy** | ❌ Cloud-dependent | ✅ 100% local & offline |
| **Reproducibility** | ❌ Non-deterministic | ✅ Deterministic parsing + validation |
| **Domain Knowledge** | ❌ Generic LLMs | ✅ Materials science specialists |
| **Cost** | ❌ API/subscription fees | ✅ One-time setup, zero runtime costs |
| **Confidence Scoring** | ❌ Not available | ✅ Detailed metrics from cross-validation |  


## Documentation

- [Architecture Details](docs/ARCHITECTURE.md) — Deep dive into pipeline design
- [Agent Guide](docs/AGENTS.md) — How to customize extraction agents
- [API Reference](docs/API.md) — Integration guide
- [Examples](examples/) — Sample workflows and use cases

## Future Work

- **Multi-paper Aggregation** — Consolidate data across multiple papers
- **Knowledge Graph Export** — RDF/OWL format for semantic integration
- **Dataset-Level Validation** — Cross-dataset consistency analysis
- **Web Dashboard** — Interactive visualization & export interface
- **Chemistry & Physics Support** — Extend beyond materials science
- **REST API** — Scalable inference service
- **Collaborative Curation** — Community feedback loop for model improvement


## Author & Contact

**Amaljosh Maadhav J**

- Email: [amal018josephmathi@gmail.com]
- LinkedIn: [https://www.linkedin.com/in/amaljoshmaadhavj/]
- GitHub: [https://github.com/amaljoshmaadhavj]