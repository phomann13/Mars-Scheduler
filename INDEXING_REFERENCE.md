# 📊 Complete Indexing Reference

## What Gets Indexed into Pinecone

This document details all the data that is indexed into the Pinecone vector store for RAG-powered course search.

---

## 🔍 Data Sources

### 1. **UMD Academic Catalog** (Scraped)
- Course Code (e.g., `CMSC131`)
- Course Name/Title
- Description
- Credits (e.g., `4` or `3-6` for variable)
- Department

### 2. **PlanetTerp API** (Enrichment)
- Average GPA
- Professors list
- Reviews (text, rating, date)
- Review count
- Alternative description (if better)

---

## 📝 Vector Embeddings (What Gets Searched)

When you search for courses, the following text is converted into a vector embedding using OpenAI:

```
Course: CMSC131 | 
Title: Object-Oriented Programming I | 
Description: [Full course description from catalog or PlanetTerp] |
Department: CMSC |
Level: 100 |
Prerequisites: [None or list] |
Topics: [Java, OOP, Programming Fundamentals] |
Professors: Nelson Padua-Perez, Fawzi Emad, ... |
Difficulty: Moderate (GPA: 3.12) |
Student Reviews: 15 reviews available |
Student Feedback: Great professor! Clear lectures... | Engaging teacher, tough but fair... | ...
```

### Why This Matters:
- **Semantic Search**: Searches like "easy Java class" will match courses with high GPA and Java topics
- **Professor Search**: "courses taught by Nelson" will find relevant matches
- **Difficulty Search**: "challenging algorithms course" will match based on GPA and review sentiment
- **Topic Search**: "learn about recursion and data structures" finds semantically similar content

---

## 🏷️ Pinecone Metadata (What Gets Filtered & Returned)

The following fields are stored as **queryable metadata** in Pinecone:

| Field | Type | Example | Purpose |
|-------|------|---------|---------|
| `courseCode` | string | `"CMSC131"` | Unique identifier |
| `courseName` | string | `"Object-Oriented Programming I"` | Display name |
| `department` | string | `"CMSC"` | Filter by department |
| `credits` | number | `4` | Filter by credit hours |
| `description` | string (1000 char limit) | `"Introduction to..."` | Preview text |
| `level` | string | `"100"` | Filter by course level |
| `avgGPA` | number | `3.12` | Filter by difficulty |
| `avgRating` | number | `4.5` | Filter by quality |
| `professors` | string | `"Nelson Padua-Perez, Fawzi Emad"` | Filter by instructor |
| `reviewCount` | number | `15` | Indicates popularity |
| `prerequisites` | string | `"CMSC131, CMSC132"` | Course dependencies |
| `topics` | string | `"Java, OOP, Algorithms"` | Subject tags |

### Metadata Filtering Examples:
```python
# Find CS courses with GPA > 3.0
filters = {
    "department": "CMSC",
    "avgGPA": {"$gte": 3.0}
}

# Find 4-credit upper-level courses
filters = {
    "credits": 4,
    "level": {"$in": ["300", "400"]}
}

# Find courses taught by a specific professor
filters = {
    "professors": {"$contains": "Nelson Padua-Perez"}
}
```

---

## 🔄 Complete Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Scraping (scrape_umd_courses.py)                        │
├─────────────────────────────────────────────────────────────┤
│   • Fetch course catalog HTML                               │
│   • Parse: courseCode, name, description, credits           │
│   • Call PlanetTerp API for each course                     │
│   • Merge: avgGPA, professors, reviews                      │
│   • Save to JSON                                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Indexing (index_courses.py)                             │
├─────────────────────────────────────────────────────────────┤
│   • Load JSON course data                                   │
│   • Validate required fields                                │
│   • Pass to VectorStoreService                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Vector Store Service                                     │
├─────────────────────────────────────────────────────────────┤
│   • Format course as text (description + metadata)          │
│   • Generate embedding via OpenAI (1536 dimensions)         │
│   • Extract metadata (all fields from JSON)                 │
│   • Upsert to Pinecone                                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Pinecone Vector Database                                 │
├─────────────────────────────────────────────────────────────┤
│   • Store vector (1536-dim array)                           │
│   • Store metadata (12+ fields)                             │
│   • Enable semantic search + filtering                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Search & Retrieval                                       │
├─────────────────────────────────────────────────────────────┤
│   • User query: "easy AI courses with good professors"      │
│   • Generate query embedding                                │
│   • Semantic search in Pinecone                             │
│   • Filter by avgGPA, department, etc.                      │
│   • Return top-K matches with metadata                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Sample Scraped Course (JSON)

```json
{
  "courseCode": "CMSC131",
  "courseName": "Object-Oriented Programming I",
  "department": "CMSC",
  "description": "Introduction to programming and computer science...",
  "credits": 4,
  "avgGPA": 3.12,
  "professors": [
    "Nelson Padua-Perez",
    "Fawzi Emad"
  ],
  "reviewCount": 15,
  "reviews": [
    {
      "professor": "Nelson Padua-Perez",
      "course": "CMSC131",
      "review": "Great professor! Clear lectures and helpful.",
      "rating": 5,
      "created": "2023-05-15T10:30:00Z"
    }
  ],
  "planetTerp": {
    "department": "CMSC",
    "courseNumber": "131",
    "title": "Object-Oriented Programming I",
    "description": "Introduction to programming...",
    "credits": 4,
    "averageGPA": 3.12,
    "professors": ["Nelson Padua-Perez", "Fawzi Emad"],
    "reviews": [...]
  }
}
```

---

## 🎯 What's NOT Indexed

The following data is **preserved in JSON** but **NOT sent to Pinecone**:

- Full review list (only snippets in embeddings)
- Raw PlanetTerp response
- Timestamps
- Very long descriptions (truncated to 1000 chars in metadata)

### Why?
- **Cost**: Pinecone charges per vector dimension and metadata size
- **Relevance**: Full reviews aren't needed for search, only summaries
- **Retrieval**: Full data can be fetched from JSON or API later

---

## 🧪 Testing Your Index

### 1. Check Vector Store Stats
```bash
curl http://localhost:8001/api/v1/insights/vector-store/stats
```

Expected response:
```json
{
  "enabled": true,
  "totalVectors": 89,
  "dimension": 1536,
  "indexFullness": 0.0089
}
```

### 2. Test Semantic Search
```bash
curl -X POST http://localhost:8001/api/v1/insights/search-courses \
  -H "Content-Type: application/json" \
  -d '{
    "query": "easy programming courses with good professors",
    "topK": 5,
    "department": "CMSC"
  }'
```

Expected response:
```json
{
  "results": [
    {
      "courseCode": "CMSC131",
      "courseName": "Object-Oriented Programming I",
      "avgGPA": 3.12,
      "professors": "Nelson Padua-Perez, Fawzi Emad",
      "reviewCount": 15,
      "similarityScore": 0.87
    }
  ]
}
```

### 3. Test Filtering
```bash
curl -X POST http://localhost:8001/api/v1/insights/search-courses \
  -H "Content-Type: application/json" \
  -d '{
    "query": "algorithms and data structures",
    "topK": 5,
    "filters": {
      "avgGPA": {"$gte": 3.0},
      "level": {"$in": ["300", "400"]}
    }
  }'
```

---

## 🔧 Troubleshooting

### "Vector dimension mismatch"
- **Problem**: Index created with wrong dimensions
- **Solution**: Delete and recreate index with 1536 dimensions

### "Metadata value must be string/number/boolean"
- **Problem**: `None` values in metadata
- **Solution**: Already handled - we filter out `None` values

### "No results found"
- **Problem**: No courses indexed or wrong index name
- **Solution**: Check stats endpoint, verify `PINECONE_INDEX_NAME` in `.env`

### "Search returns irrelevant results"
- **Problem**: Poor embedding quality or missing context
- **Solution**: Ensure all fields (especially descriptions, reviews) are populated

---

## 📈 Performance & Limits

| Metric | Value | Notes |
|--------|-------|-------|
| **Embedding Dimension** | 1536 | OpenAI `text-embedding-3-small` |
| **Max Metadata Size** | ~40KB | Pinecone limit per vector |
| **Description Limit** | 1000 chars | Truncated to fit metadata |
| **Professor Limit** | 5 names | To avoid metadata bloat |
| **Review Snippets** | Top 3 | For embedding text |
| **Batch Size** | 50 courses | For indexing performance |
| **API Rate Limit** | OpenAI varies | Backoff handled automatically |

---

## ✅ Verification Checklist

Before using the RAG system, ensure:

- [ ] Pinecone index created with **1536 dimensions**
- [ ] `.env` has `PINECONE_API_KEY`, `PINECONE_ENVIRONMENT`, `PINECONE_INDEX_NAME`
- [ ] `.env` has `OPENAI_API_KEY`
- [ ] Courses scraped with `enrichWithPlanetTerp=True` (default)
- [ ] Courses indexed successfully (check stats endpoint)
- [ ] Search API returns results with `similarityScore > 0.7`

---

## 🚀 Next Steps

1. **Index All Courses**: Run scraper on all departments
2. **Test RAG Chat**: Ask chatbot course recommendation questions
3. **Monitor Performance**: Check search quality and response times
4. **Tune Parameters**: Adjust `topK`, filters, embedding strategies
5. **Add More Data**: Consider adding grade distributions, semester info

---

*Last Updated: November 11, 2025*

