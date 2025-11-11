# Installation Guide - Phase 2 Features

Quick guide to get Phase 2 features running.

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (optional for full app)
- Pinecone account (optional for RAG features)

---

## Step 1: Install Backend Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**New dependencies installed:**
- `pinecone-client==3.0.0` - Vector store
- `langchain==0.0.350` - RAG framework
- `httpx==0.25.2` - Async HTTP client

---

## Step 2: Install Frontend Dependencies

```bash
cd frontend

# Install all dependencies including new ones
npm install
```

**New dependencies installed:**
- `leaflet@^1.9.4` - OpenStreetMap library
- `react-leaflet@^4.2.1` - React bindings
- `@types/leaflet@^1.9.8` - TypeScript types

---

## Step 3: Configure Environment Variables

### Backend (.env)

```bash
cd backend
cp env.example .env
```

Edit `.env`:

```bash
# Required
OPENAI_API_KEY=your-openai-key

# Optional (for RAG features)
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=umd-courses
```

### Frontend (.env.local)

```bash
cd frontend
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
```

---

## Step 4: Start Services

### Terminal 1: Backend

```bash
cd backend
source venv/bin/activate
python -m app.main
```

Server starts at: http://localhost:8000

### Terminal 2: Frontend

```bash
cd frontend
npm run dev
```

App starts at: http://localhost:3000

---

## Step 5: Verify Installation

### Check Backend

```bash
# Health check
curl http://localhost:8000/health

# Check buildings API
curl http://localhost:8000/api/v1/campus/buildings

# Check vector store status (will show disabled if Pinecone not configured)
curl http://localhost:8000/api/v1/insights/vector-store/stats
```

### Check Frontend

1. Open http://localhost:3000
2. Navigate to Schedule view
3. Look for campus map features
4. Try chat interface

---

## Step 6: Optional - Set Up Pinecone

### Create Pinecone Account

1. Go to https://www.pinecone.io/
2. Sign up for free account
3. Create new project

### Create Index

1. In Pinecone console, click "Create Index"
2. **Name:** `umd-courses`
3. **Dimensions:** `1536` (for text-embedding-3-small)
4. **Metric:** `cosine`
5. **Region:** `us-east-1` (or your preferred region)

### Add to .env

```bash
PINECONE_API_KEY=your-api-key-from-console
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=umd-courses
```

### Restart Backend

```bash
# In backend terminal
# Ctrl+C to stop
python -m app.main
```

### Verify RAG is Working

```bash
curl http://localhost:8000/api/v1/insights/vector-store/stats
# Should show: {"enabled": true, "totalVectors": 0, ...}
```

---

## Step 7: Index Sample Courses (Optional)

If using Pinecone, index some sample data:

```python
# In Python shell
from app.services.vector_store_service import vectorStoreService
import asyncio

async def index_sample():
    sample_course = {
        "courseCode": "CMSC131",
        "courseName": "Object-Oriented Programming I",
        "department": "Computer Science",
        "description": "Introduction to programming and computer science. Emphasizes understanding and implementation of applications using object-oriented techniques. Requires no prior programming background.",
        "credits": 4,
        "topics": ["Java", "OOP", "Programming", "Computer Science"]
    }
    
    await vectorStoreService.indexCourse(sample_course)
    print("Indexed sample course!")

asyncio.run(index_sample())
```

---

## Troubleshooting

### Issue: Backend won't start

**Check Python version:**
```bash
python --version  # Should be 3.11+
```

**Check all dependencies installed:**
```bash
pip list | grep -E 'pinecone|langchain|httpx'
```

### Issue: Frontend build errors

**Clear cache and reinstall:**
```bash
rm -rf node_modules package-lock.json
npm install
```

### Issue: Pinecone connection fails

**Verify API key:**
```bash
# Check .env file has correct key
cat backend/.env | grep PINECONE_API_KEY
```

**Check index exists:**
- Log into Pinecone console
- Verify index name matches .env
- Verify region matches .env

### Issue: OpenStreetMap rate limiting

**Solution:** Use pre-cached building data

The system automatically falls back to cached UMD buildings. For development, this is sufficient.

### Issue: Walking times not calculating

**Check building codes:**
```bash
# List all cached buildings
curl http://localhost:8000/api/v1/campus/buildings
```

Building codes must match those in the database.

---

## Quick Test Commands

### Test Campus Features

```bash
# Get all buildings
curl http://localhost:8000/api/v1/campus/buildings

# Get walking time between two buildings
curl "http://localhost:8000/api/v1/campus/walking-time?building1=AVW&building2=IRB"

# Validate a schedule's walking times
curl -X POST http://localhost:8000/api/v1/campus/validate-schedule-walking-times \
  -H "Content-Type: application/json" \
  -d '{"sections": [], "maxWalkingMinutes": 10}'
```

### Test RAG Features (requires Pinecone)

```bash
# Search courses semantically
curl -X POST http://localhost:8000/api/v1/insights/search-courses \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning courses", "limit": 5}'

# Get career recommendations
curl "http://localhost:8000/api/v1/insights/career-courses?career=software%20engineering&limit=10"
```

---

## Next Steps

1. **Explore the API:** Visit http://localhost:8000/docs
2. **Read Implementation Guide:** See `PHASE2_IMPLEMENTATION.md`
3. **Try Features:** Use the frontend at http://localhost:3000
4. **Index Courses:** Add your course data to vector store

---

## Uninstallation

### Remove Virtual Environment

```bash
cd backend
rm -rf venv
```

### Remove Node Modules

```bash
cd frontend
rm -rf node_modules
```

### Remove Pinecone Index

1. Go to Pinecone console
2. Select your index
3. Click "Delete Index"

---

## Support

If you encounter issues:

1. Check this guide first
2. Review `PHASE2_IMPLEMENTATION.md`
3. Check API docs at `/docs`
4. Inspect browser console
5. Check backend logs

---

*Last Updated: November 11, 2025*

