# PlanetTerp Data Structure

## Course Data Fields Captured

When you scrape with PlanetTerp enrichment, the following structure is created:

---

## Complete Course Object

```json
{
  // === From UMD Catalog Scraping ===
  "courseCode": "CMSC131",
  "courseName": "Object-Oriented Programming I",
  "department": "Computer Science",
  "description": "Introduction to programming and computer science...",
  "credits": 4,
  "level": "100",
  "prerequisites": ["CMSC130"],
  "corequisites": [],
  "restrictions": "",
  "topics": ["Java", "OOP", "Programming"],
  
  // === From PlanetTerp API (top-level) ===
  "avgGPA": 3.12,
  "professors": ["Nelson Padua-Perez", "Fawzi Emad", "Larry Herman"],
  
  // === Complete PlanetTerp Response (nested) ===
  "planetTerp": {
    "department": "CMSC",
    "courseNumber": "131",
    "title": "Object-Oriented Programming I",
    "description": "Introduction to programming...",
    "credits": 4,
    "averageGPA": 3.12,
    "professors": ["Nelson Padua-Perez", "Fawzi Emad", "Larry Herman"]
  },
  
  // === Optional: Alternative Description ===
  "descriptionPlanetTerp": "Longer description from PlanetTerp..."
}
```

---

## Field Descriptions

### UMD Catalog Fields (Always Present)

| Field | Type | Description | Source |
|-------|------|-------------|--------|
| `courseCode` | string | Course code (e.g., "CMSC131") | UMD Catalog |
| `courseName` | string | Full course title | UMD Catalog |
| `department` | string | Department name | Mapped from code |
| `description` | string | Course description | UMD Catalog |
| `credits` | number | Credit hours | UMD Catalog |
| `level` | string | Course level ("100", "200", etc.) | Parsed from code |
| `prerequisites` | array | List of prerequisite course codes | UMD Catalog |
| `corequisites` | array | List of corequisite course codes | UMD Catalog |
| `restrictions` | string | Course restrictions | UMD Catalog |
| `topics` | array | Extracted topic keywords | Generated |

### PlanetTerp Fields (When Available)

| Field | Type | Description | Source |
|-------|------|-------------|--------|
| `avgGPA` | number | Average GPA (e.g., 3.12) | PlanetTerp API |
| `professors` | array | List of professors who taught it | PlanetTerp API |
| `planetTerp` | object | Complete PlanetTerp response | PlanetTerp API |
| `descriptionPlanetTerp` | string | Alternative description (if longer) | PlanetTerp API |

---

## PlanetTerp Nested Object

The `planetTerp` field contains the complete API response:

```json
{
  "department": "CMSC",           // Department code
  "courseNumber": "131",          // Course number
  "title": "...",                 // Course title
  "description": "...",           // Full description
  "credits": 4,                   // Credit hours
  "averageGPA": 3.12,            // Average GPA
  "professors": ["..."]          // All professors
}
```

---

## Why Two Structures?

### Top-Level Fields (`avgGPA`, `professors`)
- ✅ Easy access for common operations
- ✅ Used directly in RAG/indexing
- ✅ Flat structure for database queries

### Nested `planetTerp` Object
- ✅ Preserves complete API response
- ✅ Useful for debugging/verification
- ✅ Can compare with catalog data
- ✅ Future-proof (if API adds fields)

---

## Example Usage

### Access Common Data
```python
course["avgGPA"]           # 3.12
course["professors"]       # ["Nelson Padua-Perez", ...]
course["description"]      # UMD catalog description
```

### Access Complete PlanetTerp Data
```python
course["planetTerp"]["averageGPA"]     # 3.12 (same as top-level)
course["planetTerp"]["department"]     # "CMSC"
course["planetTerp"]["courseNumber"]   # "131"
```

### Compare Descriptions
```python
catalog_desc = course["description"]
planetter_desc = course.get("descriptionPlanetTerp")

if planetter_desc and len(planetter_desc) > len(catalog_desc):
    print("PlanetTerp has more detailed description")
```

---

## In Vector Store (Pinecone)

When indexed to Pinecone, metadata includes:

```json
{
  "courseCode": "CMSC131",
  "courseName": "Object-Oriented Programming I",
  "department": "Computer Science",
  "credits": 4,
  "description": "Introduction to programming...",
  "level": "100",
  "avgGPA": 3.12,
  "professors": "Nelson Padua-Perez, Fawzi Emad, Larry Herman"
}
```

**Note:** 
- `professors` array is converted to comma-separated string
- Only first 5 professors included (metadata size limit)
- Nested `planetTerp` object not included (too large)

---

## Handling Missing Data

Not all courses have PlanetTerp data:

```json
{
  "courseCode": "CMSC198",
  "courseName": "Special Topics",
  "description": "...",
  "credits": 3,
  // avgGPA: undefined (not in PlanetTerp)
  // professors: undefined
  // planetTerp: undefined
}
```

**In code:**
```python
# Safe access
gpa = course.get("avgGPA")  # None if not available
if gpa:
    print(f"Average GPA: {gpa}")

# Check if PlanetTerp data exists
if "planetTerp" in course:
    print("Has PlanetTerp data")
```

---

## Scraping Output Example

When you run:
```bash
python scripts/scrape_umd_courses.py <URL>
```

You'll see:
```
Found 89 courses

Enriching courses with PlanetTerp data...
  ✅ Enriched 85/89 courses with PlanetTerp data

✅ Saved 89 courses to data/scraped_CMSC.json
```

**Result:**
- 85 courses: Full data (catalog + PlanetTerp)
- 4 courses: Catalog data only (no PlanetTerp match)

---

## Benefits of Complete Data

### For RAG/Recommendations
- **GPA-based filtering**: "Show me easy courses" (avgGPA > 3.5)
- **Professor matching**: "Courses taught by good professors"
- **Workload estimation**: Based on GPA distribution

### For Students
- **Informed decisions**: See historical GPA averages
- **Professor lists**: Know who teaches what
- **Course selection**: Compare difficulty across courses

### For Analysis
- **Department trends**: Average GPA by department
- **Course difficulty**: Identify hard vs easy courses
- **Professor impact**: Compare same course, different professors

---

## JSON File Structure

Scraped file (`data/scraped_CMSC.json`):

```json
{
  "courses": [
    {
      "courseCode": "CMSC131",
      "courseName": "...",
      "avgGPA": 3.12,
      "professors": ["..."],
      "planetTerp": {
        "department": "CMSC",
        "averageGPA": 3.12,
        "professors": ["..."]
      }
    },
    // ... more courses
  ]
}
```

---

## API Reference

**PlanetTerp Course Endpoint:**
```
GET https://api.planetterp.com/v1/course?name=CMSC131
```

**Response:**
```json
{
  "department": "CMSC",
  "course_number": "131",
  "title": "Object-Oriented Programming I",
  "description": "Introduction to programming...",
  "credits": 4,
  "average_gpa": 3.12,
  "professors": ["Nelson Padua-Perez", "Fawzi Emad", "Larry Herman"]
}
```

---

*For usage examples, see `ENHANCED_SCRAPING.md`*

