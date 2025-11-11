# Quick Start: Schedule Indexing

Get started with scraping and indexing UMD's current schedule in 5 minutes.

## Prerequisites

Install required Python packages:

```bash
pip install httpx beautifulsoup4
```

The scraper uses Testudo's sections API for direct access to section data (no browser automation required!).

## Step 1: Test with a Single Department (CMSC)

Start small to verify everything works:

```bash
cd /home/parker/Mars-Scheduler

# Scrape Computer Science courses for Spring 2026
python3 backend/scripts/scrape_current_schedule.py \
  --semester 202601 \
  --department CMSC \
  --output backend/data/test_schedule.json
```

**Expected output:**
```
📚 Fetching CMSC courses for semester 202601...
   URL: https://app.testudo.umd.edu/soc/202601/CMSC
   ✓ Found 45 courses
```

## Step 2: Verify the Scraped Data

Check the output file:

```bash
cat backend/data/test_schedule.json | jq '.[0]' | head -50
```

You should see course data with sections, instructors, and meeting times.

## Step 3: Index into Pinecone

Make sure your `.env` has:
```
PINECONE_API_KEY=your_key_here
PINECONE_INDEX_NAME=umd-courses
```

Then index the scraped data:

```bash
python3 backend/scripts/index_schedule_data.py backend/data/test_schedule.json
```

**Expected output:**
```
Indexing Schedule Data into Pinecone
====================================
✓ Courses indexed: 45
✓ Sections indexed: 280
====================================
```

## Step 4: Test with the AI

Start your backend server:

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Then ask in the chat interface:
- **"Show me CMSC courses for Spring 2026"**
- **"Who teaches CMSC131?"**
- **"Create a schedule with CMSC131 and CMSC132"**

## Step 5: Index More Departments

Once you verify it works, index more departments:

```bash
# Math
./backend/scripts/update_schedule_index.sh --semester 202601 --department MATH

# English
./backend/scripts/update_schedule_index.sh --semester 202601 --department ENGL

# Or index everything (takes 15-30 minutes)
./backend/scripts/update_schedule_index.sh --semester 202601 --all
```

## Common Semester Codes

| Semester         | Code   |
|------------------|--------|
| Spring 2025      | 202501 |
| Summer 2025      | 202505 |
| Fall 2025        | 202508 |
| Winter 2025      | 202512 |
| Spring 2026      | 202601 |
| Fall 2026        | 202608 |

## Troubleshooting

### "No courses found"

The semester might not be available yet on Testudo. Check:
```bash
# Visit in browser
open https://app.testudo.umd.edu/soc
```

### "Pinecone is not enabled"

Add to `backend/.env`:
```bash
PINECONE_API_KEY=pk-your-key-here
PINECONE_INDEX_NAME=umd-courses
```

### Permission denied

Make scripts executable:
```bash
chmod +x backend/scripts/*.sh backend/scripts/*.py
```

## What's Next?

After indexing:

1. ✅ The AI can now find courses and sections
2. ✅ Schedule generation will use real section data
3. ✅ Students can ask about specific instructors and times
4. ✅ Seat availability is tracked

Update the index regularly (especially during registration period) to keep data fresh!

## Full Documentation

See [SCHEDULE_INDEXING_GUIDE.md](../../SCHEDULE_INDEXING_GUIDE.md) for complete documentation.

