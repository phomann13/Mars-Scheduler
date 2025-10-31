# UMD AI Scheduling Assistant — Design Document

## 1. Overview

### Purpose
The **UMD AI Scheduling Assistant** is a web-based application that helps University of Maryland students plan their academic careers intelligently. It leverages AI and RAG (Retrieval-Augmented Generation) to:
- Generate **four-year academic plans** based on a student’s major and goals.  
- Recommend and build **semester schedules** optimized for preferences (professors, class times, topics).  
- Integrate **data sources** like PlanetTerp and RateMyProfessor to enhance class and professor recommendations.  
- Eventually incorporate **campus spatial data** to calculate walking times and building proximity.

### Goals
- Help students make **data-driven class decisions**.
- Automate **degree planning**.
- Provide **conversational AI interaction** for scheduling and academic advising.

---

## 2. Key Features

### Phase 1 — MVP
1. **Conversational AI Scheduling Assistant**
   - Students can chat with an AI about their academic goals.
   - Example: “I want an easy schedule with morning classes and good professors.”

2. **PlanetTerp + RateMyProfessor Integration**
   - Pull grade distributions and professor ratings.
   - Aggregate and rank professors by GPA averages, difficulty, and reviews.

3. **UMD Schedule & Curriculum Integration**
   - Scrape or pull data from:
     - UMD Schedule of Classes (course availability, times, sections)
     - Major curriculum requirements (CS, ENES, PSYC, etc.)
   - Automatically track completed and remaining degree requirements.

4. **Four-Year Plan Generator**
   - Generate personalized academic plans based on major, AP credits, and interests.
   - Validate against prerequisites and university policies.

5. **Preference System**
   - Allow students to set preferences (professor quality, time of day, workload, topics).
   - Rank and recommend schedules accordingly.

---

### Phase 2 — Extended Features
1. **Interactive Schedule Visualization**
   - Calendar view for weekly classes.
   - Ability to swap classes and reoptimize schedule.

2. **Campus Building & Walking Time Integration**
   - Show locations of classes on a campus map.
   - Estimate walking time between classes using GIS data.

3. **Collaborative Planning**
   - Compare schedules with friends.
   - Suggest shared class opportunities.

4. **Course & Career Insights**
   - Use embeddings + RAG to recommend courses based on interest (“What classes are good for AI research?”).

---

## 3. System Architecture

### High-Level Architecture
 ┌────────────────────┐
 │  User Interface    │  ← React/Next.js web app
 └──────┬─────────────┘
        │
        ▼
 ┌────────────────────┐
 │  API Gateway       │  ← FastAPI / Node.js backend
 └──────┬─────────────┘
        │
        ▼
 ┌──────────────────────────────────────┐
 │             Backend Logic            │
 │ ┌──────────────────────────────────┐ │
 │ │  AI Assistant (LLM + RAG Engine) │ │
 │ │  - Handles natural language chat │ │
 │ │  - Queries knowledge base        │ │
 │ └──────────────────────────────────┘ │
 │ ┌──────────────────────────────────┐ │
 │ │  Data Aggregation Layer          │ │
 │ │  - PlanetTerp API                │ │
 │ │  - RateMyProfessor Scraper/API   │ │
 │ │  - UMD Schedule & Curriculum API │ │
 │ └──────────────────────────────────┘ │
 └──────────────────────────────────────┘
        │
        ▼
 ┌────────────────────────────┐
 │  Database / Vector Store   │
 │  - PostgreSQL: core data   │
 │  - Pinecone / FAISS: RAG   │
 │  - Redis: caching          │
 └────────────────────────────┘

---

## 4. Data Flow

1. **User Interaction**
   - Student describes preferences in natural language.
   - System parses intent (e.g., “prefer morning classes with Dr. Smith if possible”).

2. **RAG Query Pipeline**
   - Retrieves structured course/professor data from the knowledge base.
   - Augments LLM response with accurate, up-to-date data.

3. **Scheduling Engine**
   - Combines constraints: availability, degree requirements, preferences.
   - Generates candidate schedules using combinatorial optimization.

4. **AI Response**
   - AI summarizes options, explains tradeoffs, and can visualize schedules.

---

## 5. Technical Components

| Component | Technology | Description |
|------------|-------------|-------------|
| **Frontend** | React + Next.js | Interactive chat UI, schedule visualization |
| **Backend** | FastAPI / Node.js | Core API, connects AI and data layers |
| **AI Model** | GPT-4 or GPT-5 via OpenAI API | Natural language understanding & response |
| **RAG Engine** | LangChain / LlamaIndex | Context retrieval from UMD & course data |
| **Vector Store** | Pinecone / Chroma | Stores embeddings of course data |
| **Database** | PostgreSQL | Stores users, majors, preferences, schedules |
| **External APIs** | PlanetTerp, RateMyProfessor, UMD SOC | Real-time course & professor data |
| **Future** | Mapbox / OpenStreetMap API | Campus building & walking data |

---

## 6. Data Sources

| Source | Description | Access Method |
|---------|-------------|----------------|
| **PlanetTerp API** | Grade distributions, professor ratings | Public REST API |
| **RateMyProfessor** | Professor reviews, difficulty ratings | Web scraping or unofficial API |
| **UMD Schedule of Classes** | Current and upcoming course offerings | Scraping or API wrapper |
| **UMD Curriculum Sites** | Degree requirements per major | HTML parsing or custom dataset |

---

## 7. AI + RAG Workflow

1. **User Prompt:** “Make a 4-year plan for a CS major who wants to focus on AI and avoid morning classes.”
2. **Query RAG:**  
   - Retrieve CS curriculum requirements.  
   - Retrieve AI-related courses and their availability.  
   - Retrieve professor data (PlanetTerp + RMP).
3. **Generate Draft Plan:**  
   - Ensure prerequisites are followed.
   - Distribute core + elective courses per semester.
4. **Validate & Refine:**  
   - Re-query if conflicts exist.
   - Adjust based on feedback (“Make Fall lighter”).

---

## 8. Future Roadmap

| Phase | Features |
|--------|-----------|
| **1. MVP** | Chat-based schedule generation, PlanetTerp/RMP data, curriculum parser |
| **2. Smart Scheduling** | Optimization algorithms, real-time course filtering |
| **3. Campus Map Integration** | Walking time estimation, building visualization |
| **4. Social Features** | Shared planning, course overlap with friends |
| **5. Mobile App** | Simplified version for iOS/Android |

---

## 9. Security & Privacy

- Store minimal user data (hashed identifiers, no grades/transcripts).
- Comply with UMD IT policies if deployed for public/student use.
- Respect Terms of Service for APIs and data scraping (use caching, rate-limiting).

---

## 10. Success Metrics

- **User satisfaction** (survey feedback)
- **Accuracy of degree plan** vs official requirements
- **Schedule generation time**
- **User retention & engagement**

---


