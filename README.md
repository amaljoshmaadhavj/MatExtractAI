# MatExtractAI

> **AI-powered Extraction & Validation of Materials Science Research Papers**

[![Python Version](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)](https://github.com)
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
├── 📁 src/                     
│   ├── agents/                  # LLM extraction agents (composition, mechanics, etc.)
│   ├── evaluation/              # Validation & confidence scoring logic
│   ├── ingest/                  # PDF ingestion & preprocessing
│   ├── config.py                # Configuration & path settings
│   ├── main.py                  # Pipeline A entrypoint
│   ├── run_agent_step5.py       # Mechanical properties extraction
│   ├── run_agent_step6.py       # Processing agent
│   ├── run_agent_step7.py       # Microstructure agent
│   ├── run_agent_step8.py       # Composition agent
│   └── run_pipeline_b.py        # Pipeline B validation runner
│
├── 📁 data/
│   └── raw_pdfs/                # Input: Place your research papers here (PDF format)
│
├── 📁 output/                   
│   └── <paper_name>/            # Output folder per paper
│       ├── *_sections.json      # Extracted text sections
│       ├── *_tables.json        # Extracted tables
│       ├── *_mech_agent.json    # Mechanical properties
│       ├── *_processing_agent.json  # Processing routes
│       ├── *_microstructure_agent.json  # Microstructure data
│       ├── *_composition_agent.json     # Composition data
│       └── *_evaluated.json    # Final validated output
│
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── .gitignore                   # Git ignores
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
- Python 3.13+
- Virtual environment (recommended)
- Ollama installed with LLM models loaded locally
- Ghostscript (required by Camelot for table extraction)

### Installation

```bash
# Clone or navigate to the project
cd MatExtractAI

# Create virtual environment
python -m venv .venv

# Activate it (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Usage

#### 1. Prepare Input PDFs
Place your research papers in **`data/raw_pdfs/`**:
```
data/raw_pdfs/
├── paper1.pdf
├── paper2.pdf
└── paper3.pdf
```

#### 2. Run Pipeline A - Extraction & Text Processing
```bash
python src/main.py
```

**Example output:**
```
Processing PDFs:   0%|                                                      | 0/1 [00:00<?, ?it/s]
📄 Processing applsci-14-10986-v2
✅ Saved outputs to C:\Users\admin\MatExtractAI\output\applsci-14-10986-v2
Processing PDFs: 100%|███████████████████████████████| 1/1 [00:08<00:00,  8.03s/it]
```

This generates:
- `*_sections.json` — Extracted text sections (Abstract, Introduction, Methods, Results, etc.)
- `*_tables.json` — Extracted tables

#### 3. Run Extraction Agents (Pipeline A - Domain Extraction)
```bash
python src/run_agent_step5.py  # Mechanical properties
python src/run_agent_step6.py  # Processing routes
python src/run_agent_step7.py  # Microstructure
python src/run_agent_step8.py  # Composition
```

This generates agent-specific JSON files:
- `*_mech_agent.json` — Mechanical properties extracted
- `*_processing_agent.json` — Processing routes extracted
- `*_microstructure_agent.json` — Microstructure data extracted
- `*_composition_agent.json` — Composition data extracted

#### 4. Run Pipeline B - Validation & Confidence Scoring
```bash
python src/run_pipeline_b.py
```

**Example output:**
```
✅ Pipeline B done: applsci-14-10986-v2
```

This generates:
- `*_evaluated.json` — Final validated output with confidence scores and cross-agent verification

### Output Files Location
All results are saved in **`output/<paper_name>/`**

- `*_sections.json` — Text sections
- `*_tables.json` — Extracted tables
- `*_mech_agent.json` — Mechanical properties
- `*_processing_agent.json` — Processing routes
- `*_microstructure_agent.json` — Microstructure analysis
- `*_composition_agent.json` — Composition data
- `*_evaluated.json` — Final validated results with confidence metrics

### Complete Example Workflow
```bash
# Clear previous outputs
rm -r output\*  # Windows
# rm -r output/*  # macOS/Linux

# Add your PDFs to data/raw_pdfs/

# Run the complete pipeline
python src/main.py
python src/run_agent_step5.py
python src/run_agent_step6.py
python src/run_agent_step7.py
python src/run_agent_step8.py
python src/run_pipeline_b.py

# Check results
# output/paper1/
# output/paper2/
# etc...
```

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