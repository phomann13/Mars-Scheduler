# Schedule Indexing Guide

Complete guide for scraping and indexing UMD's current semester schedule data for AI-powered schedule generation.

## Overview

The schedule indexing system consists of three main components:

1. **Schedule Scraper** - Scrapes current semester data from Testudo (app.testudo.umd.edu/soc)
2. **Data Indexer** - Indexes scraped data into Pinecone vector store for AI access
3. **Update Script** - Convenience script that runs both scraper and indexer

## What Gets Indexed

For each course section, the system captures:

- ✅ Course code and name
- ✅ Section ID
- ✅ Instructor name
- ✅ Meeting times (days, start/end times)
- ✅ Building and room location
- ✅ Seat availability (total, open, waitlist)
- ✅ Delivery mode (face-to-face, online, blended)
- ✅ Credits
- ✅ Grading method
- ✅ Course description
- ✅ Restrictions
- ✅ Cross-listings

## Prerequisites

1. **Python environment** with required packages:
   ```bash
   pip install httpx beautifulsoup4 pinecone-client openai
   ```
   
   **Note:** The scraper uses Testudo's sections API (`/soc/{semester}/sections?courseIds={courseId}`) for direct access to section data. No browser automation needed!

2. **Pinecone API key** set in `.env`:
   ```
   PINECONE_API_KEY=your_key_here
   PINECONE_INDEX_NAME=umd-courses
   ```

## Usage

### Quick Start (Recommended)

Use the all-in-one script to scrape and index in one command:

```bash
# Index ALL departments for Spring 2026
./backend/scripts/update_schedule_index.sh --semester 202601 --all

# Index only Computer Science courses
./backend/scripts/update_schedule_index.sh --semester 202601 --department CMSC

# Index only Mathematics courses
./backend/scripts/update_schedule_index.sh --semester 202601 --department MATH
```

### Semester Codes

Format: `YYYYMM`

| Semester      | Code Format | Example      |
|---------------|-------------|--------------|
| Spring        | YYYY01      | 202601       |
| Summer        | YYYY05      | 202605       |
| Fall          | YYYY08      | 202608       |
| Winter        | YYYY12      | 202612       |

### Manual Steps

If you want more control, run the scripts separately:

#### Step 1: Scrape Schedule Data

```bash
# Single department
python3 backend/scripts/scrape_current_schedule.py \
  --semester 202601 \
  --department CMSC \
  --output backend/data/schedule_cmsc.json

# All departments
python3 backend/scripts/scrape_current_schedule.py \
  --semester 202601 \
  --all \
  --output backend/data/schedule_all.json
```

#### Step 2: Index into Pinecone

```bash
python3 backend/scripts/index_schedule_data.py backend/data/schedule_all.json
```

## Data Structure

### Scraped JSON Format

```json
{
  "courseCode": "CMSC131",
  "courseName": "Object-Oriented Programming I",
  "department": "CMSC",
  "credits": 4,
  "gradingMethod": "Regular",
  "description": "Introduction to programming and computer science...",
  "restrictions": "Restriction: Must be in Engineering...",
  "crossListedWith": [],
  "semester": "202601",
  "totalSections": 15,
  "sections": [
    {
      "sectionId": "0101",
      "courseCode": "CMSC131",
      "instructor": "Pedram Sadeghian",
      "totalSeats": 200,
      "openSeats": 45,
      "waitlist": 0,
      "deliveryMode": "face-to-face",
      "meetingTimes": [
        {
          "days": "MWF",
          "startTime": "10:00am",
          "endTime": "10:50am",
          "building": "CSI",
          "room": "2118"
        }
      ]
    }
  ]
}
```

### Indexed Vector Store Format

Each course and section is indexed with rich embeddings that capture:

**Course-level documents:**
- Course name and description
- All available instructors
- Total sections and seat availability
- Cross-listings and restrictions

**Section-level documents:**
- Specific instructor
- Meeting times and location
- Seat availability status
- Delivery mode

This dual indexing allows the AI to:
1. Find relevant courses based on student queries
2. Access specific section details for schedule generation
3. Filter by instructor, time preferences, and availability

## How the AI Uses This Data

### 1. Course Discovery

When students ask "Show me CS courses about AI" or "What are easy electives?", the AI:
- Searches the vector store using semantic similarity
- Finds relevant courses based on descriptions and metadata
- Returns courses with their section information

### 2. Schedule Generation

When generating schedules, the system:
- Retrieves sections for requested courses
- Checks time conflicts
- Validates seat availability
- Considers instructor preferences
- Optimizes based on student constraints

### 3. Intelligent Recommendations

The AI can answer questions like:
- "Who teaches CMSC131 this semester?"
- "Are there any morning sections of MATH140?"
- "Which sections of CMSC216 still have open seats?"

## Regular Updates

Schedule data should be updated regularly as:
- Sections fill up
- New sections are added
- Instructors change

### Recommended Update Schedule

- **Before registration:** Daily
- **During registration:** Every few hours
- **After registration:** Weekly

### Example Cron Job

```bash
# Update every 6 hours during business days
0 */6 * * 1-5 cd /home/parker/Mars-Scheduler && ./backend/scripts/update_schedule_index.sh --semester 202601 --all
```

## Troubleshooting

### Error: "Pinecone is not enabled"

Make sure you have set the `PINECONE_API_KEY` in your `.env` file:
```bash
echo "PINECONE_API_KEY=your_key_here" >> backend/.env
```

### Error: "Failed to fetch: HTTP 404"

The semester code or department might not exist yet. Check:
1. Visit https://app.testudo.umd.edu/soc
2. Verify the semester is available
3. Verify the department code is correct

### Error: "No sections found" or sections are empty

This likely means the course has no sections for that semester. The scraper uses Testudo's sections API which returns actual data. If you see this consistently:
1. Verify the semester code is correct
2. Check that the course is actually offered that semester on Testudo
3. Try a different course/department

### Slow Scraping

Scraping all departments takes 10-25 minutes depending on:
- Network speed
- Number of courses per department (100+ per dept)
- Server response time
- Rate limiting (2-second delays between departments)

Use `--department` flag to scrape specific departments for faster testing.

### Rate Limiting

The scraper includes 2-second delays between departments to be respectful to UMD's servers. If you encounter rate limiting:
- Increase the delay in `scrape_current_schedule.py` (line ~398)
- Run during off-peak hours (late evening or early morning)
- Scrape departments in smaller batches

## Integration with Chat Interface

Once indexed, the schedule data is automatically available to the AI assistant. Students can:

```
User: "Create a schedule with CMSC131, MATH140, and ENGL101 for Spring 2026"

AI:   ✓ Extracts intent: schedule_generation
      ✓ Extracts courses: ["CMSC131", "MATH140", "ENGL101"]
      ✓ Extracts semester: Spring 2026 (202601)
      ✓ Searches vector store for sections
      ✓ Generates optimized schedule
      ✓ Returns schedule to frontend
```

The frontend automatically displays the generated schedule in the Schedule tab.

## Performance Tips

1. **Index incrementally:** For quick updates, index only changed departments
2. **Use department filters:** During development, test with single departments
3. **Cache scraped data:** Keep JSON files for re-indexing without re-scraping
4. **Monitor Pinecone usage:** Check your vector count and query limits

## Next Steps

After indexing:

1. ✅ Test with chat interface: "Show me CMSC courses for Spring 2026"
2. ✅ Generate a schedule: "Create a schedule with CMSC131 and MATH140"
3. ✅ Check section details: "Who teaches CMSC131 section 0101?"
4. ✅ Monitor seat availability: "Which CMSC216 sections have open seats?"

## Additional Resources

- [UMD Schedule of Classes](https://app.testudo.umd.edu/soc)
- [Pinecone Documentation](https://docs.pinecone.io/)
- [Project Indexing Reference](./INDEXING_REFERENCE.md)

