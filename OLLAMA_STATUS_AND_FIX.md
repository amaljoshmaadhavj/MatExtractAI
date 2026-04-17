# 🔍 MatExtractAI - OLLAMA Status and Fix Guide

## Problem Identified

Your extraction system is returning **mock/dummy data for all PDF files** because:

### Root Cause: OLLAMA is Not Running
- **OLLAMA service is not available** at the configured endpoint (`http://localhost:11434`)
- When OLLAMA is unreachable, the system automatically falls back to mock data
- This happens silently - the extraction "succeeds" but returns hardcoded dummy results

## Evidence
Looking at your screenshots:
1. **First screen**: Shows "Materials: 2" with 85% and 88% confidence - These are **hardcoded mock values**
2. **Second screen**: Shows "Grain Size (μm)" chart with AZ31/ZE10 data - These are **mock values from the fallback**
3. **Third screen**: Shows "Raw Text" with "No text..." - Indicates **text extraction might be failing OR empty**

## How the System Currently Works

```
PDF Upload
    ↓
PDF Text Extraction (PyMuPDF) ✅ [Working]
    ↓
Extract Sections (abstract, methods, results, etc.) ✅ [Working]
    ↓
OLLAMA Service Check ❌ [FAILING]
    ├─ Is OLLAMA running at http://localhost:11434?
    ├─ If YES → Extract real data from OLLAMA ✅
    └─ If NO → Use mock/dummy data ❌ [CURRENT STATE]
```

## Solution: Start OLLAMA

### Step 1: Install OLLAMA (if not installed)
```powershell
# Download from https://ollama.ai
# Or install via Windows installer
# Or use Chocolatey if you have it:
# choco install ollama
```

### Step 2: Start OLLAMA Service

**Option A: Using Command Line (Recommended for Development)**
```powershell
# In any PowerShell terminal (doesn't need to be in project folder)
ollama serve
```
This will:
- Start the OLLAMA server at `http://localhost:11434`
- Keep it running in the terminal
- Show debug logs

**Option B: Using Windows Service (Recommended for Production)**
```powershell
# OLLAMA installs as a Windows service by default
# Verify it's running:
Get-Service ollama

# If it's not running, start it:
Start-Service ollama
```

### Step 3: Verify OLLAMA is Running

```powershell
# Test the OLLAMA endpoint
$response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -ErrorAction SilentlyContinue
if ($response.StatusCode -eq 200) {
    Write-Host "✅ OLLAMA is running!"
    $response.Content | ConvertFrom-Json | Select-Object -ExpandProperty models
} else {
    Write-Host "❌ OLLAMA is not responding"
}
```

### Step 4: Verify a Model is Downloaded

```powershell
# List available models
ollama list

# If no models are listed, download one (e.g., mistral)
ollama pull mistral
# or for smaller model:
ollama pull neural-chat
# or for fastest:
ollama pull orca-mini
```

### Step 5: Check Backend Configuration

Edit `/backend/app/config.py`:
```python
# Should have:
ollama_host = "http://localhost:11434"  # ✅ Verify this URL
ollama_model = "mistral"                  # ✅ Or whatever model you downloaded
```

### Step 6: Restart Backend and Retest

```powershell
# In backend folder
cd C:\Users\admin\Projects\MatExtractAI\backend

# Kill any existing Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Start fresh
.venv\Scripts\python main.py
```

## What You Should See in Logs

### When OLLAMA is NOT Running
```
[OLLAMA] ⚠️ OLLAMA not available at http://localhost:11434: ...
[OLLAMA] ⚠️ Will use fallback mock data for extraction
```

### When OLLAMA IS Running
```
[OLLAMA] ✅ OLLAMA available at http://localhost:11434
[OLLAMA] Available models: ['mistral:latest', 'neural-chat:latest']
[OLLAMA] Using Results section: 2500 chars
[OLLAMA] Using Methods section: 1800 chars
[OLLAMA] Sending prompt to model mistral at http://localhost:11434
[OLLAMA] Received response: 450 chars
[OLLAMA] ✅ Mechanical properties extracted: 3 items
```

## Understanding Fallback Behavior

The system has **3 layers of fallback**:

1. **Preferred**: Real OLLAMA extraction (if OLLAMA running)
   - Uses actual PDF content
   - Extracts unique properties for each file
   - Returns confidence scores based on content

2. **Fallback 1**: If OLLAMA unavailable but PDF extracted
   - Uses hardcoded mock data
   - Same data for all files (what you're seeing)
   - Returns 2-3 dummy properties

3. **Fallback 2**: If PDF extraction fails
   - Uses mock data
   - Logs show "No text extracted"

## Troubleshooting Checklist

- [ ] OLLAMA is installed
- [ ] `ollama serve` is running or `Get-Service ollama` shows "Running"
- [ ] A model is downloaded (`ollama list` shows models)
- [ ] Backend configuration has correct `ollama_host` (http://localhost:11434)
- [ ] Backend logs show "✅ OLLAMA available"
- [ ] Test with `http://localhost:11434/api/tags` returns model list

## Performance Notes

Different models have different extraction quality and speed:
- **Fastest**: `orca-mini` (2GB) - ~5 sec per extraction
- **Balanced**: `neural-chat` (3.8GB) - ~10 sec per extraction
- **Best Quality**: `mistral` (5GB) - ~15 sec per extraction

Choose based on your available VRAM and time requirements.

## Next Steps

1. Deploy OLLAMA using the guide above
2. Verify OLLAMA is responding
3. Re-upload a PDF
4. Check logs for "✅ OLLAMA available"
5. New extractions should now show real data, not mock data

---

**Updated**: April 17, 2026
**Code Changes**: Enhanced logging and health checks added to detect OLLAMA availability
