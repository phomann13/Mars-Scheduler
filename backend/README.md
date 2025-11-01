# UMD AI Scheduling Assistant - Backend

FastAPI backend for the UMD AI Scheduling Assistant.

## Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes/         # API endpoint routes
│   │       ├── chat.py     # Chat/conversation endpoints
│   │       ├── schedules.py # Schedule generation endpoints
│   │       ├── plans.py    # Four-year plan endpoints
│   │       ├── users.py    # User management endpoints
│   │       └── courses.py  # Course/professor data endpoints
│   ├── core/
│   │   └── config.py       # Configuration and settings
│   ├── models/
│   │   └── database.py     # SQLAlchemy database models
│   ├── schemas/
│   │   └── schemas.py      # Pydantic request/response schemas
│   ├── services/           # Business logic layer
│   │   ├── ai_assistant_service.py      # OpenAI integration
│   │   ├── scheduling_engine.py         # Schedule optimization
│   │   ├── four_year_plan_service.py    # Plan generation
│   │   ├── planet_terp_service.py       # PlanetTerp API
│   │   ├── rate_my_professor_service.py # RateMyProfessor API
│   │   └── umd_schedule_service.py      # UMD Schedule API
│   └── main.py             # Application entry point
├── requirements.txt
└── env.example
```

## Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp env.example .env
# Edit .env with your API keys and configuration
```

## Running the Server

Development mode:
```bash
python -m app.main
```

Or with uvicorn:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

Key environment variables to configure:

- `OPENAI_API_KEY`: Your OpenAI API key for GPT-4
- `DATABASE_URL`: PostgreSQL connection string
- `PINECONE_API_KEY`: Pinecone API key for vector storage (optional)
- `REDIS_URL`: Redis connection string for caching

See `env.example` for complete list.

## Services

### AI Assistant Service
Uses OpenAI GPT-4 to:
- Understand natural language queries
- Extract user intent and parameters
- Generate schedule recommendations
- Provide conversational responses

### Scheduling Engine
Optimizes schedules based on:
- Time preferences
- Professor ratings
- Course difficulty
- Gap optimization
- Conflict detection

### Four-Year Plan Service
Generates academic plans:
- Major requirement tracking
- Prerequisite validation
- Credit distribution
- Semester balancing

### External API Services
- **PlanetTerp**: Grade distributions, professor ratings
- **RateMyProfessor**: Professor reviews and difficulty
- **UMD Schedule**: Course availability and sections

## Database Models

Key models:
- `User`: Student profile and preferences
- `Course`: Course information
- `Professor`: Professor ratings and data
- `Section`: Course sections with schedules
- `Schedule`: Generated schedules
- `FourYearPlan`: Academic plans
- `Conversation`: Chat history

## Testing

Run tests:
```bash
pytest
```

## Development

### Adding New Routes

1. Create route file in `app/api/routes/`
2. Define endpoints using FastAPI decorators
3. Add router to `app/main.py`

### Adding New Services

1. Create service file in `app/services/`
2. Implement business logic
3. Import and use in routes

### Code Style

- Use camelCase for variables and functions
- Use type hints
- Write docstrings for functions
- Keep functions small and focused

