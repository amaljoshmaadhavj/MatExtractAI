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
| **Advanced Table Parsing** | Multi-strategy table extraction: tabulated, CSV, pipe-delimited, structured pairs with type inference |
| **Domain-Specific Agents** | 4 specialized LLM agents + 1 master consolidation agent for mechanical properties, composition, processing, & microstructure |
| **Conflict Resolution** | Automatic detection & resolution of contradictory values across agents with tolerance-based reconciliation |
| **Data Normalization** | Unit conversion (15+ types), material name standardization, element symbols, semantic validation |
| **Evidence Validation** | All extracted claims linked to exact textual evidence with confidence scoring |
| **100% Offline** | Uses local LLMs via Ollama - no cloud dependencies, complete data privacy |
| **Scientific Rigor** | Deterministic parsing + semantic validation for reproducible results |


## System Architecture

MatExtractAI employs a **comprehensive pipeline** with extraction, consolidation, conflict resolution, and normalization:

### Complete Processing Pipeline

```
Research PDF 
    ↓
[1] PDF Ingestion & Page Extraction (PyMuPDF)
    ↓
[2] Text Normalization & Page-wise Processing
    ↓
[3] Automatic Section Segmentation (regex-based)
    ↓
[4] Advanced Table Detection & Extraction (5 strategies)
    ├─ Tabulated (space-aligned)
    ├─ CSV/Delimited (comma, semicolon)
    ├─ Pipe-delimited (Markdown style)
    ├─ Structured pairs (key:value)
    └─ Column type inference
    ↓
[5] Domain-Specific Agent Processing (4 agents in parallel)
    ├─→ Mechanical Properties Agent
    ├─→ Alloy Composition Agent
    ├─→ Processing Routes Agent
    └─→ Microstructure Agent
    ↓
[6] Master Consolidation Agent (Phase 1)
    ├─ Identify materials across agents
    ├─ Merge multi-agent outputs
    ├─ Detect & resolve conflicts
    ├─ Build evidence chains
    └─ Calculate confidence scores
    ↓
[7] Data Normalization (Phase 2)
    ├─ Unit conversion (MPa, μm, °C, etc.)
    ├─ Material name standardization (AZ31B, Ti-6Al-4V)
    ├─ Element symbol normalization (Al, Mg, Zn)
    ├─ Semantic validation (grain_size < material_size)
    └─ Value precision control
    ↓
[8] Structured MaterialRecord Output
    ├─ record_id (UUID)
    ├─ material_name (normalized)
    ├─ composition (standardized elements)
    ├─ processing (normalized values/units)
    ├─ microstructure (validated data)
    ├─ properties (standardized units)
    ├─ evidence_chain (source attribution)
    └─ extraction_confidence (0-1.0)
```

### Conflict Resolution Strategy

When agent outputs contradict each other:
- **Tolerance-based matching**: Property-specific ranges (YS ±5%, elongation ±10%, grain_size ±15%)
- **Automatic resolution**: Weighted average of conflicting values
- **Confidence weighting**: 60% extraction confidence + 20% data richness + 20% diversity
- **Human-readable report**: Detailed conflict documentation for review


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
**Output:** Normalized material record with evidence chain

```json
{
  "record_id": "a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6",
  "material_name": "AZ31B",
  "material_variants": ["AZ31B"],
  "composition": {
    "primary_elements": [
      {"element": "Mg", "percent": 96.0, "unit": "wt%"},
      {"element": "Al", "percent": 3.0, "unit": "wt%"},
      {"element": "Zn", "percent": 1.0, "unit": "wt%"}
    ],
    "extraction_confidence": 0.92,
    "source": "Composition Agent"
  },
  "processing": {
    "methods": ["hot rolling", "annealing"],
    "temperatures": [{"value": 350, "unit": "°C"}],
    "durations": [{"value": 2.5, "unit": "h"}],
    "cooling_method": "air cooling",
    "extraction_confidence": 0.85,
    "source": "Processing Agent"
  },
  "microstructure": {
    "grain_size_um": 15.5,
    "grain_size_original_unit": "μm",
    "phases_present": ["α-Mg"],
    "texture": "strong basal texture",
    "morphology": "equiaxed",
    "extraction_confidence": 0.88,
    "source": "Microstructure Agent"
  },
  "properties": [
    {
      "yield_strength_mpa": 170.0,
      "ultimate_tensile_strength_mpa": 245.0,
      "elongation_percent": 12.5,
      "extraction_confidence": 0.90,
      "source": "Mechanical Properties Agent"
    }
  ],
  "evidence_chain": [
    {
      "claim": "AZ31B composition: 96% Mg, 3% Al, 1% Zn",
      "source": "Table 1, page 2",
      "agent": "Composition Agent",
      "confidence": 0.95
    },
    {
      "claim": "Hot rolling at 350°C for 2.5 hours",
      "source": "Section 3.2 (Processing Routes)",
      "agent": "Processing Agent",
      "confidence": 0.88
    },
    {
      "claim": "Grain size: 15.5 μm, strong basal texture",
      "source": "SEM analysis, Section 4.1",
      "agent": "Microstructure Agent",
      "confidence": 0.91
    }
  ],
  "extraction_confidence": 0.88,
  "consolidation_status": "success",
  "consolidation_method": "master_agent_v1",
  "consolidation_timestamp": "2026-04-17T14:32:45.123456",
  "conflict_report": {
    "total_conflicts_detected": 1,
    "resolved_conflicts": 1,
    "grain_size_conflict": {
      "agent_1_value": 15.5,
      "agent_2_value": 16.2,
      "difference_percent": 4.3,
      "within_tolerance": true,
      "resolution": "weighted_average",
      "final_value": 15.8
    }
  },
  "agent_contributions": {
    "mechanical_properties": 1,
    "composition": 1,
    "processing": 1,
    "microstructure": 1
  }
}
```

**Key Features:**
- ✅ **Normalized units**: All stress values in MPa, lengths in μm, temperature in °C
- ✅ **Standardized names**: "AZ31B" (not "AZ-31 B" or "AZ 31")
- ✅ **Element symbols**: "Mg", "Al", "Zn" (not "Magnesium", "aluminum")
- ✅ **Evidence chain**: Every claim traceable to source with confidence
- ✅ **Conflict resolution**: Contradictions automatically detected and resolved
- ✅ **Confidence metrics**: Per-field and overall extraction confidence scores

## Tech Stack

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Python 3.13+, FastAPI, asyncio | REST API, request handling, orchestration |
| **Frontend** | TypeScript, Next.js 14+, React 18+ | Modern UI with server-side rendering |
| **Styling** | Tailwind CSS | Responsive, utility-first CSS |
| **Database** | MongoDB Atlas / Local MongoDB | Document storage for results & metadata |
| **LLM Inference** | Ollama | Local, private LLM execution (qwen2.5:3b model) |
| **PDF Processing** | PyMuPDF (fitz) | Fast text extraction & page handling |
| **Table Extraction** | Custom TableParser (Phase 2) | Multi-strategy table detection & parsing |
| **Data Normalization** | Custom DataNormalizer (Phase 2) | Unit conversion, standardization, validation |
| **Conflict Resolution** | Custom ConflictResolver (Phase 1) | Tolerance-based conflict detection & resolution |
| **Consolidation** | Custom ConsolidationAgent (Phase 1) | Master agent for merging 4-agent outputs |
| **Pattern Matching** | regex | Deterministic section/entity parsing |
| **Task Management** | Python asyncio | Parallel job execution & background tasks |

> **System Requirements:**
> - Python 3.13+
> - Node.js 18+ (for frontend)
> - Virtual environment (venv recommended)
> - MongoDB instance (local or cloud)
> - Ollama with qwen2.5:3b model loaded locally
> - 2+ GB RAM minimum (4+ GB recommended)

## ▶️ Quick Start Guide

### Prerequisites
- Python 3.13+
- Node.js 18+ (for frontend)
- Virtual environment (recommended)
- MongoDB instance (local or Atlas)
- Ollama installed with qwen2.5:3b model loaded locally

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
USE_MONGODB=False

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

#### 1. Start Ollama (in one terminal)
```bash
ollama serve
```

#### 2. Start Backend Server (in another terminal)
```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8000`

#### 3. Start Frontend (in another terminal)
```bash
cd frontend
pnpm dev
# or: npm run dev
```

#### 4. Access Application
Open browser and navigate to: **`http://localhost:3000`**

### Usage Workflow

1. **Upload PDF** → Upload research paper via web interface (up to 50 MB)
2. **Processing** → Real-time progress tracking (text extraction → table parsing → 4 agents → consolidation → normalization)
3. **Results Display** → View extracted material records with conflict reports and evidence chains
4. **Export** → Download normalized results in JSON format

## Pipeline Components

### Phase 1: Core Extraction & Consolidation
- ✅ **ConflictResolver** (`backend/app/services/conflict_resolver.py`)
  - Detects contradictory values across agents
  - Property-specific tolerance ranges (YS ±5%, elongation ±10%, grain_size ±15%)
  - Weighted averaging for conflict resolution
  
- ✅ **ConsolidationAgent** (`backend/app/services/consolidation_agent.py`)
  - Merges outputs from 4 parallel extraction agents
  - Identifies multiple materials in single document
  - Builds evidence chains with source attribution
  - Calculates multi-criteria confidence scores

### Phase 2: Advanced Parsing & Normalization
- ✅ **TableParser** (`backend/app/services/table_parser.py`)
  - 5 detection strategies: tabulated, CSV, pipe-delimited, structured pairs, column inference
  - Materials-aware keyword detection
  - Column type inference (numeric_stress, numeric_length, etc.)
  - Per-table confidence scoring
  
- ✅ **DataNormalizer** (`backend/app/services/data_normalizer.py`)
  - Unit conversion: 15+ types (MPa↔GPa↔kPa, μm↔nm↔mm, °C↔F↔K, etc.)
  - Material name standardization (AZ31B, Ti-6Al-4V, AISI4140)
  - Element symbol normalization (Al, Mg, Zn, etc.)
  - Semantic validation with property-specific ranges
  - Atomic number to symbol lookup


## Why MatExtractAI?

| Challenge | Generic LLMs | Traditional Tools | MatExtractAI |
|-----------|--------------|------------------|--------------|
| **Accuracy** | ❌ Prone to hallucination | ⚠️ Limited scope | ✅ Evidence-backed, validated |
| **Traceability** | ❌ Black-box outputs | ⚠️ Partial attribution | ✅ All claims linked to source |
| **Conflict Detection** | ❌ Ignores contradictions | ❌ No cross-checking | ✅ Automatic detection & resolution |
| **Data Normalization** | ❌ Inconsistent units | ⚠️ Manual cleanup | ✅ Automatic standardization |
| **Privacy** | ❌ Cloud-dependent | ✅ Local | ✅ 100% local & offline |
| **Reproducibility** | ❌ Non-deterministic | ✅ Deterministic | ✅ Deterministic + validated |
| **Domain Knowledge** | ❌ Generic | ⚠️ Limited materials science | ✅ Specialized agents |
| **Cost** | ❌ API/subscription fees | ✅ One-time | ✅ One-time setup |
| **Confidence Metrics** | ❌ Not available | ❌ Not available | ✅ Detailed scoring |


## Development Status

### ✅ Completed
- Phase 1: Conflict resolution & master consolidation agent
- Phase 2: Advanced table parsing & data normalization
- Core extraction agents (mechanical, composition, processing, microstructure)
- Evidence chain generation & confidence scoring
- Local Ollama LLM integration

### 🚀 Future Work
- **Phase 3**: Multi-material coordination & parallel agent optimization
- **Multi-paper Aggregation** — Consolidate data across research paper collections
- **Knowledge Graph Export** — RDF/OWL format for semantic integration  
- **Dataset-Level Analysis** — Cross-dataset consistency validation
- **REST API Documentation** — Interactive Swagger/OpenAPI interface
- **Docker Deployment** — Container images for reproducible deployment
- **Extended Material Coverage** — Ceramics, polymers, composites beyond alloys
- **Advanced Visualization** — Interactive dashboards for data exploration



## Implementation Details

For comprehensive documentation of implementation phases:
- **[Phase 1: Conflict Resolution & Consolidation](./PHASE_1_IMPLEMENTATION.md)** — Automatic conflict detection and master agent consolidation
- **[Phase 2: Table Parsing & Data Normalization](./PHASE_2_IMPLEMENTATION.md)** — Advanced table extraction and unit/name standardization

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