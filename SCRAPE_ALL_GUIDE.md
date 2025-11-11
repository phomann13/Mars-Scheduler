# 🚀 Complete UMD Course Scraping & Indexing Guide

## Overview

The `scrape_all_umd_courses.py` script is an **automated orchestrator** that:

1. ✅ Scrapes https://academiccatalog.umd.edu/undergraduate/approved-courses/
2. ✅ Extracts all department codes (AAST, CMSC, MATH, etc.)
3. ✅ Scrapes each department's course catalog
4. ✅ Enriches with PlanetTerp data (GPA, professors, reviews)
5. ✅ Automatically indexes everything into Pinecone
6. ✅ Generates comprehensive JSON with all UMD courses

---

## 🎯 Quick Start

### Scrape & Index Everything (One Command!)

```bash
cd /home/parker/Mars-Scheduler/backend
source venv/bin/activate

# Scrape ALL departments and auto-index
python scripts/scrape_all_umd_courses.py
```

**This will:**
- Scrape ~100+ departments
- Enrich with PlanetTerp (GPA, reviews, professors)
- Generate AI review summaries
- Index into Pinecone automatically
- Take ~30-60 minutes depending on API rate limits

---

## 📋 Usage Options

### 1. Full Auto Mode (Recommended)

```bash
# Scrape everything with PlanetTerp + Auto-index
python scripts/scrape_all_umd_courses.py
```

**Output:**
```
Fetching department list from https://academiccatalog.umd.edu/undergraduate/approved-courses/...
✅ Found 127 departments

============================================================
Starting comprehensive scrape of 127 departments
PlanetTerp enrichment: ENABLED
============================================================

[1/127] Scraping AAAS - African American and Africana Studies
URL: https://academiccatalog.umd.edu/undergraduate/approved-courses/aaas/
  Found 23 courses
  Enriching courses with PlanetTerp data...
  ✅ Enriched 20/23 courses with PlanetTerp data
  ✅ Found 23 courses

[2/127] Scraping AAST - Asian American Studies
...

============================================================
SCRAPING COMPLETE
============================================================
✅ Successful departments: 125/127
❌ Failed departments: NAVY, ARMY
📚 Total courses scraped: 8,432
⏱️  Duration: 1847.3 seconds (30.8 minutes)
💾 Saved to: /home/parker/Mars-Scheduler/backend/data/scraped_all_courses.json
============================================================

Starting automatic indexing into Pinecone...
```

### 2. Scrape Only (No Indexing)

```bash
# Scrape everything but don't index yet
python scripts/scrape_all_umd_courses.py --no-index
```

**When to use:**
- You want to review the data first
- Testing scraper changes
- Pinecone not configured yet

Then index later:
```bash
python scripts/index_courses.py data/scraped_all_courses.json
```

### 3. Fast Mode (No PlanetTerp)

```bash
# Skip PlanetTerp enrichment (much faster)
python scripts/scrape_all_umd_courses.py --no-planetterp
```

**When to use:**
- Quick testing
- Only need basic course info
- PlanetTerp API down
- Want to scrape quickly then enrich later

**Speed:** ~5-10 minutes instead of 30-60 minutes

### 4. Specific Departments Only

```bash
# Scrape only CS, Math, and Physics
python scripts/scrape_all_umd_courses.py --departments CMSC MATH PHYS

# Scrape just one department
python scripts/scrape_all_umd_courses.py --departments CMSC
```

**When to use:**
- Testing changes
- Updating specific departments
- Student only cares about certain majors

**Output file:** `data/scraped_CMSC_MATH_PHYS.json`

### 5. Combination Modes

```bash
# Fast scrape of specific departments, no auto-index
python scripts/scrape_all_umd_courses.py \
  --departments CMSC MATH \
  --no-planetterp \
  --no-index
```

---

## 📊 Output Files

### Main Output: `data/scraped_all_courses.json`

```json
{
  "metadata": {
    "scrapedAt": "2025-11-11T15:30:00",
    "totalDepartments": 127,
    "successfulDepartments": 125,
    "failedDepartments": ["NAVY", "ARMY"],
    "totalCourses": 8432,
    "enrichedWithPlanetTerp": true
  },
  "courses": [
    {
      "courseCode": "CMSC131",
      "courseName": "Object-Oriented Programming I",
      "department": "CMSC",
      "departmentCode": "CMSC",
      "departmentName": "Computer Science",
      "description": "Introduction to programming and computer science...",
      "credits": 4,
      "avgGPA": 3.12,
      "professors": ["Nelson Padua-Perez", "Fawzi Emad"],
      "reviewCount": 15,
      "reviews": [
        {
          "professor": "Nelson Padua-Perez",
          "review": "Great professor! Clear lectures.",
          "rating": 5,
          "created": "2023-05-15T10:30:00Z"
        }
      ],
      "planetTerp": {
        "department": "CMSC",
        "courseNumber": "131",
        "title": "Object-Oriented Programming I",
        "averageGPA": 3.12,
        "professors": ["Nelson Padua-Perez", "Fawzi Emad"],
        "reviews": [...]
      }
    }
  ]
}
```

### Department-Specific: `data/scraped_CMSC.json`

When using `--departments` flag, courses are saved to department-specific files.

---

## 🔄 Complete Workflow

### Initial Setup (First Time)

```bash
# 1. Activate environment
cd /home/parker/Mars-Scheduler/backend
source venv/bin/activate

# 2. Ensure dependencies are installed
pip install beautifulsoup4 lxml httpx

# 3. Verify environment variables
cat ../.env | grep -E "OPENAI_API_KEY|PINECONE"
```

### Full Scrape & Index (Production)

```bash
# One command to rule them all
python scripts/scrape_all_umd_courses.py

# Output:
# - Scrapes all departments (~30-60 min)
# - Enriches with PlanetTerp
# - Generates AI review summaries (OpenAI)
# - Indexes into Pinecone
# - Ready for chatbot queries!
```

### Update Workflow (Refreshing Data)

```bash
# 1. Re-scrape everything
python scripts/scrape_all_umd_courses.py --no-index

# 2. Review the data
cat data/scraped_all_courses.json | jq '.metadata'

# 3. Index when ready
python scripts/index_courses.py data/scraped_all_courses.json
```

### Testing Workflow (Development)

```bash
# Quick test with one department
python scripts/scrape_all_umd_courses.py \
  --departments CMSC \
  --no-planetterp \
  --no-index

# Review output
cat data/scraped_CMSC.json | jq '.courses | length'

# Test indexing
python scripts/index_courses.py data/scraped_CMSC.json
```

---

## 📈 Performance & Estimates

### Scraping Speed

| Mode | Departments | Time | Courses |
|------|-------------|------|---------|
| **Full** (with PlanetTerp) | 127 | ~30-60 min | ~8,000+ |
| **Fast** (no PlanetTerp) | 127 | ~5-10 min | ~8,000+ |
| **Single Dept** (CMSC) | 1 | ~1-2 min | ~80-100 |
| **Few Depts** (CMSC, MATH, PHYS) | 3 | ~3-5 min | ~300 |

### Indexing Speed (with AI Summaries)

| Courses | Time | Cost (OpenAI) |
|---------|------|---------------|
| 100 | ~2-3 min | ~$0.05 |
| 1,000 | ~20-30 min | ~$0.50 |
| 8,000+ | ~2-3 hours | ~$4.00 |

**Note:** AI review summarization uses GPT-4o-mini, which is very affordable.

### Rate Limits

The script includes built-in delays:
- **1 second** between departments (catalog scraping)
- **0.2 seconds** between PlanetTerp API calls
- **Automatic backoff** on OpenAI rate limits

---

## 🎯 What Gets Scraped

### From UMD Academic Catalog

- ✅ Course code (e.g., CMSC131)
- ✅ Course name/title
- ✅ Description (full text)
- ✅ Credit hours (including variable like "3-6")
- ✅ Department code & name

### From PlanetTerp API

- ✅ Average GPA
- ✅ Professors list
- ✅ Student reviews (text, rating, date)
- ✅ Review count

### Generated by AI (OpenAI)

- ✅ Review summaries (150-200 word paragraphs)

---

## 🔍 Monitoring Progress

### Real-Time Progress

```bash
# Watch the scraping in real-time
python scripts/scrape_all_umd_courses.py | tee scrape.log
```

### Check Output

```bash
# View metadata summary
cat data/scraped_all_courses.json | jq '.metadata'

# Count courses
cat data/scraped_all_courses.json | jq '.courses | length'

# Sample a course
cat data/scraped_all_courses.json | jq '.courses[0]'

# Find courses with reviews
cat data/scraped_all_courses.json | jq '[.courses[] | select(.reviewCount > 0)] | length'
```

---

## 🚨 Troubleshooting

### "No departments found to scrape"

**Problem:** Failed to parse the approved courses page

**Solution:**
```bash
# Test the URL manually
curl https://academiccatalog.umd.edu/undergraduate/approved-courses/ | grep -i "aast"

# Check if website structure changed
python3 << 'EOF'
import httpx
from bs4 import BeautifulSoup

response = httpx.get("https://academiccatalog.umd.edu/undergraduate/approved-courses/")
soup = BeautifulSoup(response.text, 'html.parser')
links = soup.find_all('a', href=lambda h: h and '/approved-courses/' in h)
print(f"Found {len(links)} links")
for link in links[:5]:
    print(f"  {link.get('href')} -> {link.text}")
EOF
```

### "Error during indexing"

**Problem:** Pinecone not configured or invalid data

**Solution:**
```bash
# Check Pinecone config
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/parker/Mars-Scheduler/backend')
from app.core.config import settings
print(f"Pinecone Key: {'***' + settings.PINECONE_API_KEY[-4:] if settings.PINECONE_API_KEY else 'NOT SET'}")
print(f"Pinecone Index: {settings.PINECONE_INDEX_NAME}")
EOF

# Manually index
python scripts/index_courses.py data/scraped_all_courses.json
```

### "PlanetTerp API errors"

**Problem:** Rate limiting or API down

**Solution:**
```bash
# Skip PlanetTerp enrichment
python scripts/scrape_all_umd_courses.py --no-planetterp

# Or scrape in smaller batches
python scripts/scrape_all_umd_courses.py --departments CMSC
# (wait a bit)
python scripts/scrape_all_umd_courses.py --departments MATH
```

### "OpenAI API errors during indexing"

**Problem:** Rate limits or invalid API key

**Solution:**
```bash
# Check OpenAI key
echo $OPENAI_API_KEY

# Disable AI summaries temporarily
# Edit vector_store_service.py line 151:
# useAISummary = False

# Or wait and retry
sleep 60
python scripts/index_courses.py data/scraped_all_courses.json
```

---

## 📅 Recommended Schedule

### Initial Population

```bash
# Day 1: Scrape everything
python scripts/scrape_all_umd_courses.py --no-index

# Review the data
cat data/scraped_all_courses.json | jq '.metadata'

# Day 2: Index (slow, 2-3 hours for AI summaries)
python scripts/index_courses.py data/scraped_all_courses.json
```

### Monthly Updates

```bash
# Re-scrape to get latest reviews/GPA
python scripts/scrape_all_umd_courses.py

# Pinecone automatically updates existing courses
```

### On-Demand Updates

```bash
# Update just CS department
python scripts/scrape_all_umd_courses.py --departments CMSC

# Will create data/scraped_CMSC.json and auto-index
```

---

## ✅ Verification Checklist

After running the script:

- [ ] `data/scraped_all_courses.json` exists and is ~50-100MB
- [ ] Metadata shows ~8,000+ courses
- [ ] Sample courses have `avgGPA`, `professors`, `reviews` fields
- [ ] Pinecone stats show correct vector count
- [ ] Chatbot can answer course questions
- [ ] Search API returns relevant results

### Quick Test

```bash
# 1. Check scraped data
cat data/scraped_all_courses.json | jq '.courses | length'

# 2. Check Pinecone stats
curl http://localhost:8001/api/v1/insights/vector-store/stats

# 3. Test search
curl -X POST http://localhost:8001/api/v1/insights/search-courses \
  -H "Content-Type: application/json" \
  -d '{"query": "easy programming course", "topK": 3}'

# 4. Test chatbot
curl -X POST http://localhost:8001/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the best CS courses for beginners?"}'
```

---

## 🎉 Expected Results

After successful completion:

```
============================================================
SCRAPING COMPLETE
============================================================
✅ Successful departments: 127/127
📚 Total courses scraped: 8,432
⏱️  Duration: 1847.3 seconds (30.8 minutes)
💾 Saved to: data/scraped_all_courses.json
============================================================

Starting automatic indexing into Pinecone...

Indexing 8432 valid courses...

Processing batch 1/169 (50 courses)...
  Generating review summary for CMSC131...
  Generating review summary for CMSC132...
  ✅ Success: 50
  ❌ Failed: 0

...

==================================================
Indexing complete!
✅ Total successfully indexed: 8432
❌ Total failed: 0
==================================================
```

**Your chatbot now knows about ALL UMD courses!** 🚀

---

## 🔗 Related Documentation

- [INDEXING_REFERENCE.md](INDEXING_REFERENCE.md) - What gets indexed
- [REVIEW_SUMMARIZATION.md](REVIEW_SUMMARIZATION.md) - AI review summaries
- [Design-Doc.md](Design-Doc.md) - Overall architecture

---

*Last Updated: November 11, 2025*

