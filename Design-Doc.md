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

## 11. Implementation Status

### ✅ Completed (Phase 1 MVP)

**Backend (FastAPI)**
- ✅ Core API with FastAPI including all main endpoints
- ✅ Database models (SQLAlchemy) for Users, Courses, Professors, Sections, Schedules, Plans
- ✅ Pydantic schemas for request/response validation
- ✅ PlanetTerp API integration service
- ✅ RateMyProfessor GraphQL API integration service
- ✅ UMD Schedule of Classes API integration service
- ✅ AI Assistant service with OpenAI GPT-4
- ✅ RAG-ready architecture (LangChain compatible)
- ✅ Scheduling engine with optimization algorithms
- ✅ Four-year plan generator with prerequisite validation
- ✅ Preference system (time, professor, difficulty, workload)
- ✅ CORS configuration for frontend integration
- ✅ API documentation (Swagger/ReDoc)

**Frontend (Next.js + Material-UI)**
- ✅ Next.js 14 with App Router
- ✅ Material-UI (MUI) components with UMD theming
- ✅ Chat interface with real-time messaging
- ✅ Schedule visualization (weekly calendar view)
- ✅ Four-year plan visualization (timeline view)
- ✅ TypeScript type definitions
- ✅ API service layer (Axios)
- ✅ Responsive design
- ✅ Tab-based navigation
- ✅ Suggestion chips for guided interaction

**Configuration & Documentation**
- ✅ requirements.txt for Python dependencies
- ✅ package.json for Node.js dependencies
- ✅ Environment variable configuration
- ✅ Comprehensive README files
- ✅ API endpoint documentation
- ✅ Development setup instructions

### 📋 API Endpoints Implemented

**Chat**
- `POST /api/v1/chat/chat` - Send message to AI assistant

**Schedules**
- `POST /api/v1/schedules/generate` - Generate optimized schedules
- `GET /api/v1/schedules/{scheduleId}` - Get schedule details
- `DELETE /api/v1/schedules/{scheduleId}` - Delete schedule

**Four-Year Plans**
- `POST /api/v1/plans/generate` - Generate academic plan
- `GET /api/v1/plans/{planId}` - Get plan details
- `GET /api/v1/plans/user/{userId}` - Get user plans
- `PUT /api/v1/plans/{planId}` - Update plan
- `DELETE /api/v1/plans/{planId}` - Delete plan

**Courses & Professors**
- `GET /api/v1/courses` - Search courses
- `GET /api/v1/courses/{courseCode}` - Get course details
- `GET /api/v1/professors/{professorName}` - Get professor details
- `GET /api/v1/departments` - List departments

**Users**
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{userId}` - Get user details
- `PUT /api/v1/users/{userId}` - Update user
- `GET /api/v1/users/{userId}/profile` - Get complete profile

### 🔄 Next Steps

1. **Database Setup**
   - Initialize PostgreSQL database
   - Run migrations
   - Seed with initial curriculum data

2. **Vector Store Integration**
   - Set up Pinecone or Chroma
   - Create embeddings for course descriptions
   - Implement semantic search

3. **Data Population**
   - Scrape/import UMD curriculum data
   - Cache professor ratings
   - Import current semester course data

4. **Testing**
   - Unit tests for services
   - Integration tests for API endpoints
   - End-to-end testing

5. **Deployment**
   - Containerize with Docker
   - Set up CI/CD pipeline
   - Deploy to cloud platform (AWS/Azure/GCP)

---

