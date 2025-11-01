# Project Structure

```
Mars-Scheduler/
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # Application entry point
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes/               # API endpoints
│   │   │       ├── __init__.py
│   │   │       ├── chat.py           # Chat/conversation routes
│   │   │       ├── courses.py        # Course & professor routes
│   │   │       ├── plans.py          # Four-year plan routes
│   │   │       ├── schedules.py      # Schedule generation routes
│   │   │       └── users.py          # User management routes
│   │   ├── core/
│   │   │   └── config.py             # Configuration & settings
│   │   ├── models/
│   │   │   └── database.py           # SQLAlchemy database models
│   │   ├── schemas/
│   │   │   └── schemas.py            # Pydantic request/response schemas
│   │   └── services/                 # Business logic layer
│   │       ├── ai_assistant_service.py        # OpenAI GPT-4 integration
│   │       ├── four_year_plan_service.py      # Academic plan generation
│   │       ├── planet_terp_service.py         # PlanetTerp API client
│   │       ├── rate_my_professor_service.py   # RateMyProfessor API client
│   │       ├── scheduling_engine.py           # Schedule optimization
│   │       └── umd_schedule_service.py        # UMD Schedule API client
│   ├── Dockerfile                    # Backend container configuration
│   ├── README.md                     # Backend documentation
│   ├── requirements.txt              # Python dependencies
│   └── env.example                   # Environment variables template
│
├── frontend/                         # Next.js Frontend
│   ├── src/
│   │   ├── app/                      # Next.js App Router
│   │   │   ├── layout.tsx            # Root layout
│   │   │   ├── page.tsx              # Main page
│   │   │   └── theme.ts              # MUI theme configuration
│   │   ├── components/               # React components
│   │   │   ├── ChatInterface.tsx     # Chat UI component
│   │   │   ├── FourYearPlanView.tsx  # Plan visualization
│   │   │   └── ScheduleView.tsx      # Schedule visualization
│   │   ├── services/
│   │   │   └── api.ts                # Backend API client
│   │   └── types/
│   │       └── index.ts              # TypeScript type definitions
│   ├── Dockerfile                    # Frontend container configuration
│   ├── README.md                     # Frontend documentation
│   ├── next.config.js                # Next.js configuration
│   ├── package.json                  # Node.js dependencies
│   └── tsconfig.json                 # TypeScript configuration
│
├── .gitignore                        # Git ignore rules
├── Design-Doc.md                     # System design documentation
├── docker-compose.yml                # Multi-container orchestration
├── PROJECT_STRUCTURE.md              # This file
├── README.md                         # Project documentation
└── SETUP.md                          # Setup instructions

```

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **AI/ML**: OpenAI GPT-4, LangChain
- **Database**: PostgreSQL 15+ (SQLAlchemy ORM)
- **Cache**: Redis
- **Vector Store**: Pinecone/Chroma (for RAG)
- **HTTP Client**: httpx

### Frontend
- **Framework**: Next.js 14 (App Router)
- **UI Library**: Material-UI (MUI)
- **Language**: TypeScript
- **HTTP Client**: Axios
- **Styling**: Emotion (CSS-in-JS)

### External APIs
- PlanetTerp API (course/professor data)
- RateMyProfessor GraphQL API (professor reviews)
- UMD Schedule of Classes API (course schedules)

## Key Files

### Backend
- `app/main.py` - FastAPI application initialization and route registration
- `app/core/config.py` - Environment configuration using Pydantic
- `app/models/database.py` - SQLAlchemy models for database tables
- `app/schemas/schemas.py` - Request/response validation schemas
- `app/services/*.py` - Business logic and external API integrations

### Frontend
- `src/app/page.tsx` - Main application page with tab navigation
- `src/components/ChatInterface.tsx` - AI chat interface
- `src/components/ScheduleView.tsx` - Weekly schedule calendar
- `src/components/FourYearPlanView.tsx` - Timeline view of academic plan
- `src/services/api.ts` - Backend API communication layer

## Database Schema

### Tables
- `users` - Student profiles and preferences
- `courses` - Course information and requirements
- `professors` - Professor ratings and data
- `sections` - Course sections with schedules
- `schedules` - Generated semester schedules
- `four_year_plans` - Academic plans
- `conversations` - Chat history

## API Endpoints

### Chat
- `POST /api/v1/chat/chat` - Send message to AI assistant

### Schedules
- `POST /api/v1/schedules/generate` - Generate optimized schedules
- `GET /api/v1/schedules/{scheduleId}` - Get schedule
- `DELETE /api/v1/schedules/{scheduleId}` - Delete schedule

### Plans
- `POST /api/v1/plans/generate` - Generate four-year plan
- `GET /api/v1/plans/{planId}` - Get plan
- `GET /api/v1/plans/user/{userId}` - Get user plans
- `PUT /api/v1/plans/{planId}` - Update plan
- `DELETE /api/v1/plans/{planId}` - Delete plan

### Courses
- `GET /api/v1/courses` - Search courses
- `GET /api/v1/courses/{courseCode}` - Get course details
- `GET /api/v1/professors/{professorName}` - Get professor details
- `GET /api/v1/departments` - List departments

### Users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{userId}` - Get user
- `PUT /api/v1/users/{userId}` - Update user
- `GET /api/v1/users/{userId}/profile` - Get profile

## Development Workflow

1. **Start Backend**: `cd backend && python -m app.main`
2. **Start Frontend**: `cd frontend && npm run dev`
3. **Access Application**: http://localhost:3000
4. **API Documentation**: http://localhost:8000/docs

## Deployment

Use Docker Compose for easy deployment:
```bash
docker-compose up -d
```

This starts:
- PostgreSQL database
- Redis cache
- Backend API server
- Frontend web server

