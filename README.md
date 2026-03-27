# MatExtractAI

> **AI-powered Extraction & Validation of Materials Science Research Papers**

[![Python Version](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)](https://github.com)
[![Last Updated](https://img.shields.io/badge/Updated-2026-blue.svg)]()

## Overview

MatExtractAI is a **full-stack intelligent system** that transforms unstructured **materials science research PDFs** into **structured, evidence-backed JSON** using a combination of deterministic parsing and local LLM-based agents. The system features a **modern web interface** (Next.js/React frontend) connected to a **robust FastAPI backend** with MongoDB persistence.

With a focus on **scientific rigor, traceability, and reproducibility**, MatExtractAI is purpose-built for:
- Research data repositories
- Automated research pipelines  
- Materials informatics platforms
- Cross-paper meta-analysis
- Enterprise knowledge extraction

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
├── 📁 backend/                  
│   ├── app/                     # FastAPI application
│   │   ├── core/                # Business logic (workers, utils, exceptions)
│   │   ├── models/              # Pydantic models & schemas
│   │   ├── routes/              # API endpoints
│   │   ├── services/            # Service layer (extraction, validation)
│   │   ├── storage/             # File & database operations
│   │   ├── config.py            # Settings & configuration
│   │   └── main.py              # FastAPI app initialization
│   ├── uploads/                 # Uploaded PDF files
│   ├── results/                 # Processing results & outputs
│   ├── logs/                    # Application logs
│   ├── requirements.txt         # Python dependencies
│   ├── main.py                  # Server entrypoint
│   └── OLLAMA_SETUP.txt         # Ollama configuration guide
│
├── 📁 frontend/                 
│   ├── app/                     # Next.js pages & components
│   │   ├── upload/              # File upload interface
│   │   ├── progress/            # Job progress tracking
│   │   └── results/             # Results display
│   ├── components/              # Reusable React components
│   ├── lib/                     # Utilities & API client
│   ├── public/                  # Static assets
│   ├── package.json             # Node dependencies
│   └── tsconfig.json            # TypeScript configuration
│
├── 📁 data/                     # Additional data files
│
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
| **Backend** | Python 3.13+, FastAPI | REST API, request handling, orchestration |
| **Frontend** | TypeScript, Next.js 14+, React 18+ | Modern UI with server-side rendering |
| **Styling** | Tailwind CSS | Responsive, utility-first CSS |
| **Database** | MongoDB Atlas / Local MongoDB | Document storage for results & metadata |
| **LLM Inference** | Ollama | Local, private LLM execution (no cloud) |
| **PDF Processing** | PyMuPDF (fitz) | Fast, reliable text extraction |
| **Table Extraction** | Camelot-py | Intelligent table detection & parsing |
| **Pattern Matching** | regex | Deterministic section/entity parsing |
| **Data Processing** | pandas, numpy | Validation & numerical analysis |
| **Task Queue** | Python asyncio | Parallel job execution & background tasks |

> **System Requirements:**
> - Python 3.13+
> - Node.js 18+ (for frontend)
> - MongoDB instance (local or cloud)
> - Ollama with LLM models loaded locally
> - ⚠️ Ghostscript (required by Camelot for advanced table extraction)

## ▶️ Quick Start Guide

### Prerequisites
- Python 3.13+
- Node.js 18+
- Virtual environment (recommended)
- MongoDB instance (local or Atlas)
- Ollama installed with LLM models loaded locally
- Ghostscript (required by Camelot for table extraction)

### Installation

#### Backend Setup
```bash
# Navigate to backend
cd backend

# Create Python virtual environment
python -m venv .venv

# Activate it (Windows)
.venv\Scripts\activate
# Or (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install Node dependencies
pnpm install
# or: npm install
```

### Configuration

#### Backend Configuration
Create a `.env` file in the `backend/` directory:
```env
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://localhost:3000

# MongoDB Connection
MONGODB_URL=mongodb://localhost:27017
# Or MongoDB Atlas: mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=mat_extract_ai
USE_MONGODB=True

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b

# File Storage
UPLOAD_DIR=./uploads
RESULTS_DIR=./results
LOGS_DIR=./logs
MAX_FILE_SIZE=52428800

# Processing
JOB_TIMEOUT=1800
CLEANUP_DAYS=7
```

**📖 Detailed Ollama setup:** See [backend/OLLAMA_SETUP.txt](backend/OLLAMA_SETUP.txt)

### Running the Application

#### 1. Start MongoDB
```bash
# Local MongoDB
mongod

# Or use MongoDB Atlas - configure connection string in .env
```

#### 2. Start Ollama
```bash
ollama serve
```

#### 3. Start Backend Server
```bash
cd backend
python main.py
```


#### 4. Start Frontend (in new terminal)
```bash
cd frontend
pnpm dev
# or: npm run dev
```

#### 5. Access Application
Open browser and navigate to: **`http://localhost:3000`**

### Usage Workflow

1. **Upload PDF** → Upload research paper via web interface
2. **Processing** → Real-time progress monitoring
3. **Results Display** → View extracted data, tables, and metrics
4. **Export** → Download results in JSON format


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
- **Web Dashboard** — Enhanced visualization & analytics
- **Chemistry & Physics Support** — Extend beyond materials science
- **REST API Documentation** — OpenAPI/Swagger interface
- **Collaborative Curation** — Community feedback loop for model improvement
- **Deployment** — Docker containers & cloud deployment guides



## Security & Privacy

✅ **Environment Variables** — Never commit `.env` files (add to `.gitignore`)
✅ **MongoDB Credentials** — Store securely, use strong passwords
✅ **Local Processing** — All data stays on-premises, no cloud dependencies
✅ **Secret Scanning** — GitHub Actions monitor for exposed credentials


## Author & Contact

**Amaljosh Maadhav J**

- Email: [amal018josephmathi@gmail.com]
- LinkedIn: [https://www.linkedin.com/in/amaljoshmaadhavj/]
- GitHub: [https://github.com/amaljoshmaadhavj]