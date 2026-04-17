# MongoDB Atlas Configuration Guide for MatExtractAI

## Overview
MatExtractAI is now configured to use **MongoDB Atlas exclusively** with no fallback to local MongoDB or file-based storage. This ensures data consistency and cloud-ready deployment.

## Getting Your MongoDB Atlas Connection String

### Step 1: Create a MongoDB Atlas Account
1. Visit [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Sign up for a free account
3. Create an organization and project

### Step 2: Create a Cluster
1. Click "Create" to deploy a new cluster
2. Choose "Free Tier" for development
3. Select your preferred cloud provider (AWS, Google Cloud, Azure)
4. Choose a region close to your location
5. Click "Create Deployment"

### Step 3: Get Your Connection String
1. When cluster creation is complete, click "Connect"
2. Choose "Connect your application"
3. Select "Python" and version "3.12 or later"
4. Copy the connection string (it will look like below)

### Step 4: Create a Database User
1. Go to "Security" → "Database Access" in Atlas console
2. Click "Add New Database User"
3. Create username and strong password
4. Click "Add User"
5. Copy the username and password

### Step 5: Whitelist Your IP Address
1. Go to "Security" → "Network Access"
2. Click "Add IP Address"
3. Click "Allow access from anywhere" (for development)
   - For production, specify your server's IP address
4. Confirm

## Update .env File

Edit `backend/.env` with your MongoDB Atlas credentials:

```env
# MongoDB Atlas Configuration (REQUIRED)
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=mat_extract_ai
```

### Connection String Format
```
mongodb+srv://username:password@cluster.net/?retryWrites=true&w=majority
```

Replace:
- `username`: Your MongoDB Atlas database user
- `password`: Your database user password
- `cluster`: Your cluster name (e.g., `cluster0.abc123def`)

### Example
```env
MONGODB_URL=mongodb+srv://aiuser:P@ssw0rd123@cluster0.12345ab.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=mat_extract_ai
```

## Complete .env Configuration

```env
# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://localhost:3000

# File Storage
UPLOAD_DIR=./uploads
RESULTS_DIR=./results
LOGS_DIR=./logs
MAX_FILE_SIZE=52428800

# Processing
JOB_TIMEOUT=1800
CLEANUP_DAYS=7

# Ollama (Local LLM)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b

# Logging
LOG_LEVEL=INFO
DEBUG=false

# MongoDB Atlas (REQUIRED - NO LOCAL FALLBACK)
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=mat_extract_ai
```

## Verify Connection

### Test from Command Line
```bash
cd backend
python test_mongodb_atlas.py
```

Expected output:
```
✅ MongoDB Atlas connected successfully
   Database: mat_extract_ai
   Cluster: cluster0.12345ab
✅ MongoDB Atlas indexes created successfully
```

### Test from Python Code
```python
from app.config import settings
from app.storage.mongodb_client import MongoDBClient

# Initialize connection
client = MongoDBClient.get_instance()

# Check connection
print(f"Database: {client.db}")
print("✅ Connected to MongoDB Atlas")
```

## Troubleshooting

### Error: "CRITICAL: MongoDB connection string must be MongoDB Atlas format"
- **Cause**: Connection string doesn't start with `mongodb+srv://`
- **Solution**: Use MongoDB Atlas connection string, not local MongoDB format

### Error: "Failed to connect to MongoDB Atlas - Connection failed"
- **Cause**: Invalid credentials or cluster not found
- **Solution**: 
  - Verify username and password
  - Check cluster name spelling
  - Ensure user was created in correct project

### Error: "Server selection timeout"
- **Cause**: IP not whitelisted or network issues
- **Solution**:
  - Go to MongoDB Atlas "Network Access"
  - Add your IP address (or 0.0.0.0 for development)
  - Wait 1-2 minutes for changes to propagate

### Error: "Authentication failed"
- **Cause**: Wrong username/password
- **Solution**:
  - Go to "Database Access" in MongoDB Atlas
  - Verify the username and password
  - Reset password if needed

### Error: "Database 'mat_extract_ai' does not exist"
- **Cause**: Database hasn't been created yet
- **Solution**: This is normal! Database will be auto-created on first connection

## Security Best Practices

### For Production:
1. **IP Whitelist**: Instead of "0.0.0.0", specify your server's IP address
2. **Strong Password**: Use a generated password with 16+ characters
3. **Environment Variables**: Never commit `.env` to Git
4. **Rotate Credentials**: Change passwords periodically
5. **Monitor Activity**: Check Atlas Activity Log for unusual access

### For Development:
1. Use a separate development cluster
2. Use simple credentials in .env (local development only)
3. Add `.env` to `.gitignore`

## File Storage

**Important**: MatExtractAI now requires MongoDB Atlas exclusively. The following have been removed:
- ❌ Local MongoDB support
- ❌ mongomock in-memory database
- ❌ File-based fallback storage (as primary)

File storage (`.json` files in `results/` folder) is kept as **backup only** for development/debugging.

## Connection Pooling

The following connection parameters are optimized for performance:
```python
serverSelectionTimeoutMS=10000   # 10 second timeout
connectTimeoutMS=15000            # 15 second connect timeout
socketTimeoutMS=15000             # 15 second socket timeout
retryWrites=True                  # Automatic retry on transient errors
maxPoolSize=50                    # Max 50 concurrent connections
minPoolSize=10                    # Keep 10 connections open
```

## Next Steps

1. ✅ Create MongoDB Atlas account and cluster
2. ✅ Get connection string
3. ✅ Update `.env` file with credentials
4. ✅ Run `test_mongodb_atlas.py` to verify
5. ✅ Start backend: `python main.py`

## Support

- MongoDB Atlas Documentation: https://docs.mongodb.com/atlas/
- Connection String Format: https://docs.mongodb.com/manual/reference/connection-string/
- Troubleshooting: https://docs.mongodb.com/atlas/troubleshoot-connection/

---

**Important**: Do not commit your `.env` file with real credentials to Git. Add it to `.gitignore`.
