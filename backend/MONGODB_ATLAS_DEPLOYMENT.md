# MongoDB Atlas Configuration - Verification & Deployment Guide

## ✅ Configuration Complete

Your MongoDB Atlas credentials have been successfully configured in the backend.

### Your Setup Details

**Database User:**
- Username: `[YOUR_DATABASE_USER]`
- Cluster: `[YOUR_CLUSTER_HOSTNAME]`
- Database: `mat_extract_ai`

**Connection String Format:**
```
mongodb+srv://[USERNAME]:[PASSWORD]@[CLUSTER].mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
```

**Location:** `backend/.env` (NOT committed to git)
```env
# ⚠️ NEVER commit .env file - store credentials locally only
MONGODB_URL=mongodb+srv://[USERNAME]:[PASSWORD]@[CLUSTER].mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
MONGODB_DATABASE=mat_extract_ai
```

---

## 📋 Pre-Deployment Checklist

Before running the application, ensure:

### Step 1: MongoDB Atlas Cluster Configuration ✅
- [ ] Cluster is running (check MongoDB Atlas dashboard)
- [ ] Database user exists
- [ ] IP whitelist includes your server's IP address:
  - **For Local Development:** Add `0.0.0.0/0` (allows any IP)
  - **For Production:** Add your specific server IP only

### Step 2: Verify IP Whitelist in MongoDB Atlas
1. Log in to MongoDB Atlas: https://cloud.mongodb.com
2. Go to **Security** → **Network Access**
3. Check that your IP is whitelisted
   - If using NAT/Proxy, whitelist `0.0.0.0/0` for testing

### Step 3: Verify Credentials
1. Go to **Security** → **Database Access**
2. Find your database user
3. Verify password is set correctly (store in .env only)
4. Click "Edit" if password needs reset

### Step 4: Test Connection from Server
```bash
# From project root
cd backend

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run MongoDB test
python test_mongodb_atlas.py
```

**Expected Output:**
```
✅ MongoDB Atlas connected successfully
   Database: mat_extract_ai
   Cluster: [YOUR_CLUSTER_NAME]
✅ MongoDB Atlas indexes created successfully
```

---

## 🚀 Running the Application

### 1. Install All Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start Ollama (Terminal 1)

```bash
ollama serve
```

**Expected Output:**
```
Listening on 127.0.0.1:11434 (http)
```

### 3. Start Backend (Terminal 2)

```bash
cd backend
python main.py
```

**Expected Output:**
```
✅ MongoDB Atlas connected successfully
   Database: mat_extract_ai
   Cluster: [YOUR_CLUSTER_NAME]
Starting MatExtractAI backend...
API listening on 0.0.0.0:8000
CORS enabled for: http://localhost:3000
```

### 4. Start Frontend (Terminal 3)

```bash
cd frontend
pnpm dev
```

**Expected Output:**
```
▲ Next.js 14.0.0
- Local: http://localhost:3000
```

### 5. Access Application

Open browser: **http://localhost:3000**

---

## 🔍 Verifying MongoDB Atlas Connection

### Method 1: Check Application Startup
Look for these messages in backend console:
```
✅ MongoDB Atlas connected successfully
   Database: mat_extract_ai
   Cluster: [YOUR_CLUSTER_NAME]
```

### Method 2: Manual Python Test
```python
from app.config import settings
from app.storage.mongodb_client import MongoDBClient

# Connect
client = MongoDBClient.get_instance()

# Check connection
print(f"✅ Connected to: {settings.mongodb_database}")
print(f"Collections: {client.db.list_collection_names()}")
```

### Method 3: MongoDB Atlas Dashboard
1. Log in to MongoDB Atlas
2. Go to **Clusters** → **cluster0** → **Collections**
3. You should see collections: `results`, `jobs`

---

## 🛠️ Troubleshooting

### Error: "DNSError" or "Nameservers failed"
**Cause:** Network cannot reach MongoDB Atlas  
**Solutions:**
1. Check your internet connection
2. Verify IP whitelist in MongoDB Atlas includes your IP
3. Try from a different network (if current network has firewall)
4. Contact your network administrator if behind corporate proxy

### Error: "Authentication failed"
**Cause:** Wrong username or password  
**Solution:**
```bash
# Go to MongoDB Atlas
# → Security → Database Access
# → Find your database user
# → Click "Edit" → Reset password
# → Update .env file with new password
```

### Error: "Connection refused"
**Cause:** MongoDB Atlas cluster is paused  
**Solution:**
1. Log in to MongoDB Atlas
2. Go to **Clusters** → **cluster0**
3. Click "Resume" if showing "Paused"

### Error: "Cluster IP whitelist does not include..."
**Cause:** Your IP not whitelisted  
**Solution:**
1. Go to MongoDB Atlas → **Security** → **Network Access**
2. Click "Add IP Address"
3. Enter your IP or use "Allow access from anywhere" for testing
4. Wait 1-2 minutes for changes to apply

---

## 📊 Application Architecture with MongoDB Atlas

```
Frontend (Next.js/React)
    ↓
    ↓ HTTP/REST
    ↓
Backend (FastAPI)
    ├─ ExtractionService (PyMuPDF)
    ├─ AgentService (Ollama LLMs)
    ├─ ValidationService
    └─ MongoDBManager ←→ MongoDB Atlas (CLOUD)
                         ├─ mat_extract_ai (db)
                         │  ├─ results (collection)
                         │  ├─ jobs (collection)
                         │  └─ other metadata
```

**Data Flow:**
1. User uploads PDF → Backend (/upload)
2. Backend extracts text → ExtractionService
3. Runs LLM agents → Ollama (local)
4. Validates results → ValidationService
5. **Saves to MongoDB Atlas** ← PRIMARY STORAGE
6. Returns results → Frontend

---

## 🔐 Security Notes

### Current Configuration (Development)
```env
# ⚠️ NEVER commit .env to repository
MONGODB_URL=mongodb+srv://[USERNAME]:[PASSWORD]@[CLUSTER].mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
```

**⚠️ Important:**
- Never commit `.env` file to Git
- `.env` contains database credentials
- Use `.gitignore` to exclude it
- Store credentials in environment variables only

### For Production Deployment
1. **Use Environment Secrets:**
   - Store `MONGODB_URL` in:
     - Docker secrets
     - AWS Secrets Manager
     - Azure Key Vault
     - Kubernetes secrets

2. **Restrict IP Whitelist:**
   - Instead of `0.0.0.0/0`, use your server's IP
   - Example: `203.0.113.45` (your production server IP)

3. **Rotate Credentials Regularly:**
   - Change password every 3 months
   - Update in MongoDB Atlas
   - Update in application secrets

---

## 📦 Included Files

All MongoDB configuration files have been updated:

| File | Changes |
|------|---------|
| `.env` | ✅ Updated with your credentials |
| `app/config.py` | ✅ MongoDB Atlas only (no local fallback) |
| `app/storage/mongodb_client.py` | ✅ Atlas TLS connection with validation |
| `app/storage/mongodb_manager.py` | ✅ All operations require MongoDB |
| `app/main.py` | ✅ Application fails without MongoDB |
| `app/routes/upload.py` | ✅ MongoDB required for all endpoints |
| `app/routes/jobs.py` | ✅ MongoDB required |
| `app/routes/results.py` | ✅ MongoDB required |

---

## ⚡ Quick Reference Commands

```bash
# Install dependencies
cd backend && pip install -r requirements.txt

# Activate environment
.venv\Scripts\activate

# Test MongoDB connection
python test_mongodb_atlas.py

# Start backend
python main.py

# Run specific test
python -m pytest tests/ -v

# Check MongoDB with CLI (if mongo shell installed)
# ⚠️ Replace with your actual MongoDB URI from .env
mongosh "mongodb+srv://[USERNAME]:[PASSWORD]@[CLUSTER].mongodb.net/[DATABASE]"
```

---

## 📞 Support Resources

- **MongoDB Atlas Docs:** https://docs.mongodb.com/atlas/
- **PyMongo Docs:** https://pymongo.readthedocs.io/
- **Connection String:** https://docs.mongodb.com/manual/reference/connection-string/
- **Network Access:** https://docs.mongodb.com/atlas/security/add-ip-address-to-list/
- **Troubleshooting:** https://docs.mongodb.com/atlas/troubleshoot-connection/

---

## ✅ Next Steps

1. **Verify MongoDB Atlas:**
   - Check cluster is running
   - Check IP whitelist includes your server IP
   - Verify database user exists

2. **Install Dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Test Connection:**
   ```bash
   python test_mongodb_atlas.py
   ```

4. **Start Services:**
   - Terminal 1: `ollama serve`
   - Terminal 2: `cd backend && python main.py`
   - Terminal 3: `cd frontend && pnpm dev`

5. **Access Application:**
   - Browser: http://localhost:3000

---

## 🎉 You're All Set!

Your MatExtractAI application is configured to:
- ✅ Use MongoDB Atlas for all data persistence
- ✅ Connect securely with TLS encryption
- ✅ Require MongoDB for operation (no fallback)
- ✅ Store results in cloud for scalability

Happy extracting! 🚀
