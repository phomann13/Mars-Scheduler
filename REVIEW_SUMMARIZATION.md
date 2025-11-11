# 🤖 AI-Powered Review Summarization

## Overview

The Mars Scheduler now uses **OpenAI GPT-4o-mini** to automatically generate comprehensive summaries of all student reviews for each course. These summaries are indexed into Pinecone and used by the chatbot to provide informed course recommendations.

---

## 🎯 How It Works

### 1. **During Indexing**

When you index courses, the system:
1. Detects if a course has reviews (from PlanetTerp)
2. Extracts up to 20 reviews with ratings
3. Sends them to OpenAI GPT-4o-mini
4. Generates a 150-200 word summary paragraph
5. Includes the summary in the vector embedding
6. Stores the summary in Pinecone metadata

### 2. **Automatic Processing**

```python
# In vector_store_service.py
async def generateReviewSummary(self, reviews: List[Dict[str, Any]]) -> Optional[str]:
    """
    Generate a concise summary paragraph of all course reviews using OpenAI.
    """
    # Takes all reviews and creates a comprehensive summary including:
    # - Overall sentiment (positive/negative/mixed)
    # - Common themes (teaching quality, difficulty, workload)
    # - Specific strengths and weaknesses
    # - Notable professor feedback
```

### 3. **Indexed for Search**

The summary is added to the embedding text:

```
Course: CMSC131 |
Title: Object-Oriented Programming I |
Description: Introduction to programming... |
Professors: Nelson Padua-Perez, Fawzi Emad |
Difficulty: Moderate (GPA: 3.12) |
Student Review Summary: Students consistently praise the clear teaching style and well-structured lectures, particularly appreciating the hands-on projects and responsive TAs. The workload is considered manageable with regular practice, though exam difficulty varies by professor. Many note excellent preparation for CMSC132, with strong fundamentals in Java and OOP concepts. Some mention fast pacing in the second half of the semester.
```

---

## 📊 Example Output

### Input: 15 PlanetTerp Reviews

```json
[
  {
    "review": "Nelson is an amazing professor. His lectures are clear and he genuinely cares about students.",
    "rating": 5,
    "professor": "Nelson Padua-Perez"
  },
  {
    "review": "Great intro class. Projects are challenging but doable. TA support is excellent.",
    "rating": 4,
    "professor": "Nelson Padua-Perez"
  },
  {
    "review": "Fast paced but good preparation for 132. Make sure to attend lectures.",
    "rating": 4,
    "professor": "Fawzi Emad"
  },
  // ... 12 more reviews
]
```

### Output: AI-Generated Summary

```
Students consistently praise the clear teaching style and well-structured lectures, 
particularly appreciating the hands-on projects and responsive TAs. The workload is 
considered manageable with regular practice, though exam difficulty varies by professor. 
Many note excellent preparation for CMSC132, with strong fundamentals in Java and OOP 
concepts. Some mention fast pacing in the second half of the semester. Professor 
Nelson Padua-Perez receives especially high marks for caring about student success and 
providing helpful office hours. Overall sentiment is highly positive, with students 
recommending the course for beginners with no prior programming experience.
```

---

## 🚀 Usage

### Automatic During Indexing

```bash
cd /home/parker/Mars-Scheduler/backend
source venv/bin/activate

# When you run indexing, summaries are automatically generated
python scripts/index_courses.py data/scraped_CMSC.json
```

**Output:**
```
Processing batch 1/2 (50 courses)...
  Generating review summary for CMSC131...
  Generating review summary for CMSC132...
  Generating review summary for CMSC216...
  ✅ Success: 50
  ❌ Failed: 0
```

### Query API for Summaries

```bash
curl -X POST http://localhost:8001/api/v1/insights/search-courses \
  -H "Content-Type: application/json" \
  -d '{
    "query": "courses with positive student feedback",
    "topK": 3
  }'
```

**Response:**
```json
{
  "results": [
    {
      "courseCode": "CMSC131",
      "courseName": "Object-Oriented Programming I",
      "avgGPA": 3.12,
      "professors": "Nelson Padua-Perez, Fawzi Emad",
      "reviewCount": 15,
      "reviewSummary": "Students consistently praise the clear teaching style...",
      "similarityScore": 0.91
    }
  ]
}
```

---

## 🤖 Chatbot Integration

The AI assistant now has access to review summaries for better recommendations:

### User Query:
> "What's an easy CS class with good professors and positive reviews?"

### Chatbot Response:
> Based on student feedback, I'd recommend **CMSC131** with Professor Nelson Padua-Perez. 
> Students consistently praise his clear teaching style and well-structured lectures. 
> The course has an average GPA of 3.12 (moderate difficulty) and students appreciate 
> the hands-on projects and responsive TA support. It's great preparation for upper-level 
> CS courses and requires no prior programming experience.

### How It Works:

1. User query is embedded: `"easy CS class with good professors"`
2. Pinecone searches for similar courses
3. Returns courses with matching review summaries
4. AI assistant includes summary in context:

```python
# In ai_assistant_service.py
def _formatRAGContext(self, courses):
    for course in courses:
        courseInfo.append(f"Student Reviews: {course['reviewSummary']}")
    # This rich context helps the chatbot give informed recommendations
```

---

## 💰 Cost Considerations

### OpenAI Pricing (GPT-4o-mini)
- **Input**: ~$0.15 per 1M tokens
- **Output**: ~$0.60 per 1M tokens

### Per Course Summary Cost
- **Input**: ~500 tokens (20 reviews)
- **Output**: ~200 tokens (summary)
- **Cost per course**: ~$0.00020 (0.02 cents)

### Batch Processing
- **100 courses**: ~$0.02
- **1000 courses**: ~$0.20
- **All UMD courses** (~3000): ~$0.60

**Conclusion:** Extremely affordable! You can summarize the entire UMD course catalog for less than a dollar.

---

## 🔧 Customization

### Adjust Summary Length

Edit `vector_store_service.py`:

```python
response = await self.openaiClient.chat.completions.create(
    model="gpt-4o-mini",
    messages=[...],
    max_tokens=300,  # ← Change this (default: 300)
    temperature=0.3
)
```

### Change Summary Style

Modify the prompt:

```python
prompt = f"""Summarize the following student reviews into a paragraph (150-200 words). 
Focus on:
- Overall sentiment
- Teaching quality
- Workload and difficulty
- Exam structure
- Project quality
- TA support

Reviews:
{chr(10).join(reviewTexts)}

Summary:"""
```

### Use Different Model

```python
model="gpt-4o-mini",  # Fast and cheap (default)
# model="gpt-3.5-turbo",  # Even cheaper
# model="gpt-4o",  # More detailed but expensive
```

---

## 📊 What Gets Stored

### In Pinecone Metadata (500 char limit)

```json
{
  "courseCode": "CMSC131",
  "courseName": "Object-Oriented Programming I",
  "reviewCount": 15,
  "reviewSummary": "Students consistently praise the clear teaching style and well-structured lectures, particularly appreciating the hands-on projects and responsive TAs. The workload is considered manageable with regular practice, though exam difficulty varies by professor..."
}
```

### In Vector Embedding (for semantic search)

The full summary is included in the text that gets embedded, enabling queries like:
- "courses with good TAs"
- "classes with manageable workload"
- "professors who care about students"
- "courses with fair exams"

---

## 🧪 Testing

### Test Summary Generation

```python
# In Python shell
import asyncio
from app.services.vector_store_service import vectorStoreService

reviews = [
    {"review": "Great class!", "rating": 5},
    {"review": "Challenging but fair", "rating": 4},
    {"review": "Professor is very helpful", "rating": 5}
]

summary = asyncio.run(vectorStoreService.generateReviewSummary(reviews))
print(summary)
```

### Test Chatbot with Summaries

```bash
# Start backend
cd /home/parker/Mars-Scheduler/backend
source venv/bin/activate
python -m app.main

# Test chat endpoint
curl -X POST http://localhost:8001/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the easiest CS classes with good reviews?",
    "conversationHistory": []
  }'
```

---

## 🎯 Benefits

### For Students:
- ✅ **Quick insights** without reading 50+ individual reviews
- ✅ **Balanced perspective** from all reviews, not just extremes
- ✅ **Key themes** highlighted (workload, difficulty, teaching quality)
- ✅ **Professor-specific** feedback when relevant

### For Chatbot:
- ✅ **Rich context** for recommendations
- ✅ **Semantic matching** on review content
- ✅ **Informed answers** about course quality
- ✅ **Better search** for soft criteria (e.g., "engaging lectures")

### For System:
- ✅ **Compact storage** (1 paragraph vs. 50 reviews)
- ✅ **Efficient indexing** (fits in Pinecone metadata limits)
- ✅ **Cost-effective** (~$0.60 for entire catalog)
- ✅ **Automatic updates** whenever re-indexing

---

## 🔄 Re-Indexing Workflow

When course reviews are updated:

```bash
# 1. Re-scrape with latest reviews
python scripts/scrape_umd_courses.py [URL]

# 2. Re-index (summaries regenerate automatically)
python scripts/index_courses.py data/scraped_CMSC.json

# 3. New summaries are now live in Pinecone
```

The system automatically:
- Detects new reviews
- Generates fresh summaries
- Updates vector embeddings
- Replaces old data in Pinecone

---

## ⚠️ Limitations

1. **Max 20 reviews**: To avoid token limits, only the first 20 reviews are summarized
2. **English only**: OpenAI works best with English reviews
3. **Cost**: Very low (~$0.60 for all UMD courses), but not zero
4. **Rate limits**: OpenAI has rate limits (handled with delays)
5. **Summary quality**: Depends on review quality; garbage in, garbage out

---

## 🚨 Error Handling

The system gracefully handles:
- **No reviews**: Summary is skipped, course still indexed
- **API errors**: Logs error, continues with other courses
- **Invalid reviews**: Filters out empty/malformed reviews
- **Token limits**: Truncates to 20 reviews automatically

---

## ✅ Verification Checklist

- [ ] `.env` has `OPENAI_API_KEY`
- [ ] Courses scraped with `reviews:true` in PlanetTerp API
- [ ] Indexing script shows "Generating review summary..." messages
- [ ] Search results include `reviewSummary` field
- [ ] Chatbot mentions review content in recommendations

---

## 🎉 Result

Your chatbot can now answer questions like:
- "Show me CS courses where students praise the professor"
- "What are some classes with manageable workload?"
- "Which courses have good TA support?"
- "Find me an engaging lecture-based class"

All powered by AI-generated summaries of real student reviews! 🚀

---

*Last Updated: November 11, 2025*

