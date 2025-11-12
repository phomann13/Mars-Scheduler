# Mars Scheduler - UMD AI Scheduling Assistant

## Overview

Mars Scheduler is an intelligent course scheduling assistant for University of Maryland students. It combines AI-powered natural language processing with real-time data from multiple sources to help students build optimal semester schedules and four-year academic plans.

## Key Features

### 1. AI-Powered Chat Interface
- Natural language query processing using OpenAI GPT models
- Intent detection for schedule generation, course search, and general questions
- Context-aware responses with markdown formatting
- Quick suggestion prompts for common queries

### 2. Intelligent Schedule Generation
- Integration with **Venus UMD Schedule API** for real schedule data
- Automatic fallback to sample data when API authentication is required
- Multi-schedule generation (displays top 5 optimal schedules)
- Semester and year-specific planning (Spring, Fall, Winter, Summer)
- Credit hour constraints (min/max credits)

### 3. Interactive Schedule Visualization
- Weekly calendar grid view
- Color-coded time blocks by course
- Hover tooltips showing course details
- Schedule navigation (cycle through multiple schedule options)
- Display of professor names, sections, and class types

### 4. Campus Route Mapping
- **OpenStreetMap (OSM)** integration with Leaflet.js
- **OSRM (Open Source Routing Machine)** for actual walking routes
- Day-by-day class route visualization
- Color-coded markers matching route segments
- Walking distance and duration calculations
- Interactive markers with class details and route metrics

### 5. Semantic Course Search
- **Pinecone vector database** for semantic similarity search
- Natural language course queries (e.g., "find intro programming courses")
- OpenAI embeddings for course descriptions and metadata
- Integration of course data from UMD catalog and PlanetTerp
- Fast retrieval of relevant courses with similarity scoring

### 6. Course & Professor Information
- **PlanetTerp API** integration for course data
- **RateMyProfessor** data for professor ratings
- Course descriptions, prerequisites, and requirements
- Professor quality metrics and difficulty ratings

### 7. Four-Year Academic Planning
- Semester-by-semester course planning
- Visual timeline of academic progression
- Credit hour tracking across semesters
- Prerequisite validation (planned)

## Technology Stack

### Frontend
- **Framework**: Next.js 14 (React 18)
- **UI Library**: Material-UI (MUI) v5
- **Mapping**: Leaflet.js with react-leaflet
- **Language**: TypeScript
- **Styling**: Emotion (CSS-in-JS)
- **HTTP Client**: Fetch API

### Backend
- **Framework**: FastAPI (Python)
- **AI/ML**: OpenAI GPT-4/GPT-3.5-turbo
- **Vector Database**: Pinecone (for semantic search)
- **Database**: PostgreSQL (user data, courses, schedules)
- **Cache**: Redis (session data, API caching)
- **HTTP Client**: httpx (async)
- **Data Processing**: pandas, numpy
- **Web Scraping**: BeautifulSoup4, Selenium

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Database**: PostgreSQL 15 (relational data)
- **Cache**: Redis 7 (key-value store)
- **Vector Store**: Pinecone (cloud-hosted embeddings)
- **Web Server**: Uvicorn (ASGI)
- **Development Server**: Next.js dev server

### External APIs & Services
1. **Venus UMD Schedule API** - Official UMD schedule generation
2. **OSRM API** - Walking route calculation (router.project-osrm.org)
3. **OpenStreetMap** - Campus map tiles
4. **PlanetTerp API** - UMD course and professor data
5. **RateMyProfessor** - Professor ratings (scraped)
6. **OpenAI API** - GPT models for natural language processing

## Architecture

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Chat UI      │  │ Schedule View│  │  Four year   │  │  Map View    │       │
│  │ (MUI)        │  │ (Calendar)   │  │  Plan        │  │  (Leaflet)   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘       │
└───────────────────────────┬───────────────────────────────────────────────────┘
                            │ HTTP/JSON
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              API Routes Layer                        │   │
│  │  /chat  /schedule  /courses  /insights  /campus      │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │                                     │
│  ┌────────────────────┴──────────────────────────────────┐  │
│  │              Service Layer                            │  │
│  │  • AI Assistant Service (intent extraction)           │  │
│  │  • Venus Schedule Service (API integration)           │  │
│  │  • Vector Store Service (semantic search)             │  │
│  │  • PlanetTerp Service (course data)                   │  │
│  │  • RateMyProfessor Service (prof ratings)             │  │
│  └────────────────────┬──────────────────────────────────┘  │
│                       │                                     │
│  ┌────────────────────┴──────────────────────────────────┐  │
│  │              Data Layer                               │  │
│  │  • PostgreSQL (courses, users, schedules)             │  │
│  │  • Redis (cache, sessions)                            │  │
│  │  • Sample Schedules (JSON fallback)                   │  │
│  │  • Building Locations (Python dict)                   │  │
│  └───────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │  Redis       │  │  Pinecone    │
│  (Data)      │  │  (Cache)     │  │  (Vectors)   │
└──────────────┘  └──────────────┘  └──────────────┘
        │               
        ▼               
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  OpenAI API  │  │  Venus API   │  │  OSRM API    │
│  (GPT-4)     │  │  (Schedules) │  │  (Routes)    │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Data Flow

### Schedule Generation Flow
1. User asks: "Generate my schedule for Spring 2026 with CMSC131, MATH140, ENGL101"
2. Frontend sends message to `/chat` endpoint
3. Backend AI Assistant Service extracts intent and parameters
4. Venus Schedule Service attempts API call
5. If authentication fails, loads sample schedule data
6. Enriches schedule with building locations and metadata
7. Returns top 5 schedules to frontend
8. Frontend displays in calendar view

### Route Mapping Flow
1. User selects "Route Map" tab and chooses a day
2. Frontend filters classes for selected day
3. MapDisplay component extracts building locations
4. For each class transition, calls OSRM API:
   ```
   GET https://router.project-osrm.org/route/v1/foot/
       {start_lng},{start_lat};{end_lng},{end_lat}
       ?overview=full&geometries=geojson
   ```
5. OSRM returns walking path coordinates, distance, and duration
6. Frontend renders colored polylines and markers on OSM map

### Course Search Flow
1. User asks: "What are some good intro CS courses?"
2. Backend generates embedding for query using OpenAI text-embedding-ada-002
3. Pinecone performs vector similarity search against indexed courses
4. Returns top-k most relevant courses with similarity scores
5. Backend enriches results with PlanetTerp data (GPA, ratings, reviews)
6. Frontend displays formatted course information with metadata

## Key Implementation Details

### Intent Detection
- Uses OpenAI's JSON mode for structured output
- Extracts: intent type, courses, semester, year, credits
- Handles fallback for models without JSON support
- Robust JSON parsing with markdown unwrapping

### Sample Data Fallback
- Venus API requires UMD Shibboleth authentication
- Detects 301/302 redirects automatically
- Loads local `sample_semester_schedule.json`
- Injects building location data for map visualization

### Vector Search Indexing
- Pre-processes UMD course catalog with descriptions
- Enriches with PlanetTerp data (GPA, professors, reviews)
- Generates rich text embeddings using OpenAI text-embedding-ada-002
- Stores vectors in Pinecone with metadata (course code, name, credits, GPA, professors)
- Supports semantic similarity queries with filtering (department, level, credits)
- Includes review sentiment and professor names in embeddings for better search

### Map Visualization
- Custom colored SVG markers for each class
- Matches marker color to route polyline color
- Drop shadow effects for better visibility
- Responsive map bounds adjustment
- Loading indicators during route calculation

## Project Structure

```
Mars-Scheduler/
├── frontend/                 # Next.js React application
│   ├── src/
│   │   ├── app/             # Next.js 14 app router
│   │   │   └── page.tsx     # Main application page
│   │   └── components/      # React components
│   │       ├── ChatInterface.tsx
│   │       ├── VenusScheduleView.tsx
│   │       ├── ScheduleMapView.tsx
│   │       ├── MapDisplay.tsx
│   │       ├── FourYearPlanView.tsx
│   │       └── MarkdownMessage.tsx
│   ├── Dockerfile
│   └── package.json
│
├── backend/                  # FastAPI Python application
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/      # API endpoints
│   │   │       ├── chat.py
│   │   │       ├── courses.py
│   │   │       ├── campus.py
│   │   │       └── schedule.py
│   │   ├── services/        # Business logic
│   │   │   ├── ai_assistant_service.py
│   │   │   ├── venus_schedule_service.py
│   │   │   ├── course_search_service.py
│   │   │   └── planetterp_service.py
│   │   ├── data/            # Data modules
│   │   │   └── umd_buildings.py
│   │   └── main.py          # FastAPI app
│   ├── data/                # Static data files
│   │   ├── sample_semester_schedule.json
│   │   ├── scraped_courses.json
│   │   └── scraped_all_courses.json
│   ├── scripts/             # Utility scripts
│   │   └── index_courses.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker-compose.yml       # Multi-container orchestration
├── .env                     # Environment variables (OpenAI key)
└── Description.md          # This file
```

## Environment Setup

### Required Environment Variables
```bash
# Backend (.env)
OPENAI_API_KEY=sk-...                    # OpenAI API key
PINECONE_API_KEY=...                     # Pinecone API key
PINECONE_ENVIRONMENT=...                 # Pinecone environment (e.g., us-east-1-aws)
PINECONE_INDEX_NAME=umd-courses          # Pinecone index name
DATABASE_URL=postgresql://...            # PostgreSQL connection string
REDIS_URL=redis://redis:6379             # Redis connection string

# Optional
VENUS_API_URL=https://venus.cs.umd.edu/api/schedules
PLANETTERP_API_URL=https://api.planetterp.com/v1
```

### Docker Compose Services
1. **frontend** - Next.js dev server (port 3000)
2. **backend** - FastAPI server (port 8000)
3. **postgres** - PostgreSQL 15 database (port 5432)
4. **redis** - Redis 7 cache (port 6379)

Note: Pinecone is a cloud-hosted service and doesn't require a local container.

## Usage

### Starting the Application
```bash
docker-compose up --build
```

### Indexing Courses (First Time Setup)
```bash
docker-compose exec backend python scripts/index_courses.py
```

### Accessing the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs
- PostgreSQL: localhost:5432 (use pgAdmin or psql)
- Redis: localhost:6379 (use redis-cli)

## Future Enhancements

1. **Authentication**
   - UMD CAS/Shibboleth integration
   - Direct Venus API access with user credentials

2. **Enhanced AI Features**
   - Multi-turn conversation context
   - Schedule optimization recommendations
   - Conflict detection and resolution

3. **Advanced Mapping**
   - Live bus tracking integration
   - Weather-aware route suggestions
   - Building accessibility information

4. **Social Features**
   - Share schedules with friends
   - Study group formation
   - Collaborative course planning

5. **Data Persistence** ✅ (Partially Implemented)
   - PostgreSQL for user data, courses, schedules
   - Pinecone for course embeddings and semantic search
   - Redis for caching API responses
   - Save multiple schedule versions (planned)
   - Historical plan tracking (planned)

6. **Mobile Application**
   - React Native mobile app
   - Push notifications for class reminders
   - Offline schedule access

## Performance Metrics

- **Schedule Generation**: ~2-3 seconds (with Venus API)
- **Course Search**: <500ms (vector similarity)
- **Route Calculation**: ~200-500ms per segment (OSRM)
- **Chat Response**: ~1-2 seconds (GPT-4)
- **Map Rendering**: <1 second for 5 classes

## Credits & Data Sources

- **UMD Venus API**: Official UMD schedule data
- **PlanetTerp**: Community-sourced course reviews and GPA data
- **RateMyProfessor**: Professor ratings and reviews
- **OpenStreetMap**: Map tiles and geodata
- **OSRM**: Open-source routing engine for pedestrian routes
- **OpenAI**: GPT models for NLP and text embeddings
- **Pinecone**: Vector similarity search and embeddings storage
- **PostgreSQL**: Relational database
- **Redis**: Caching layer

## License & Disclaimer

This is an educational project for UMD students. Course data, professor ratings, and schedule information are sourced from public APIs and websites. Always verify critical information with official UMD sources (Testudo, Student Records).

## Contact & Contributions

For questions, bug reports, or feature requests, please refer to the project repository or contact the development team.

---

**Built with ❤️ for UMD Terps** 🐢

