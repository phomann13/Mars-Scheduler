# UMD AI Scheduling Assistant (Mars Scheduler)

An AI-powered web application that helps University of Maryland students plan their academic careers intelligently using GPT-4 and RAG (Retrieval-Augmented Generation).

## Features

### Phase 1 - MVP (✅ Implemented)

1. **Conversational AI Scheduling Assistant**
   - Natural language chat interface
   - Intelligent understanding of student preferences and goals
   - Context-aware responses using GPT-4

2. **PlanetTerp + RateMyProfessor Integration**
   - Aggregate professor ratings from multiple sources
   - Grade distributions and GPA averages
   - Professor difficulty ratings and reviews

3. **UMD Schedule & Curriculum Integration**
   - Real-time course availability data
   - Major curriculum requirements tracking
   - Prerequisite validation

4. **Four-Year Plan Generator**
   - Personalized academic plans based on major and goals
   - Automatic prerequisite ordering
   - Credit distribution optimization

5. **Preference-Based Scheduling**
   - Time-of-day preferences (morning/afternoon/evening)
   - Professor quality prioritization
   - Workload optimization
   - Back-to-back class avoidance

### Phase 2 - Extended Features (✅ Implemented)

1. **Interactive Schedule Visualization**
   - Visual weekly calendar with drag-and-drop UI
   - Color-coded course blocks
   - Hover interactions for section details
   - Walking time warnings display

2. **Campus Building & Walking Time Integration**
   - OpenStreetMap integration for building locations
   - Real-time walking time calculations
   - Schedule validation based on walking feasibility
   - 30+ pre-cached UMD building coordinates

4. **Course & Career Insights (RAG)**
   - Semantic course search using Pinecone vector store
   - Career path-based recommendations
   - Similar course discovery
   - AI-enhanced responses with relevant context

**See `PHASE2_IMPLEMENTATION.md` for detailed documentation.**

## Architecture

```
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── main.py         # Application entry
│   └── requirements.txt
│
└── frontend/               # Next.js frontend
    ├── src/
    │   ├── app/           # Next.js App Router
    │   ├── components/    # React components
    │   ├── services/      # API services
    │   └── types/         # TypeScript types
    └── package.json
```

## Tech Stack

### Backend
- **Framework**: FastAPI
- **AI/ML**: OpenAI GPT-4, LangChain
- **Database**: PostgreSQL
- **Cache**: Redis
- **Vector Store**: Pinecone/Chroma

### Frontend
- **Framework**: Next.js 14 (App Router)
- **UI Library**: Material-UI (MUI)
- **Language**: TypeScript
- **HTTP Client**: Axios

### External APIs
- PlanetTerp API
- RateMyProfessor GraphQL API
- UMD Schedule of Classes API

## Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `env.example`:
```bash
cp env.example .env
```

5. Configure environment variables in `.env`:
   - Add your OpenAI API key
   - Configure database connection
   - Set up Pinecone credentials (optional)

6. Run the backend server:
```bash
python -m app.main
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file:
```bash
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
```

4. Run the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Usage

1. **Start the Backend**: Run the FastAPI server
2. **Start the Frontend**: Run the Next.js development server
3. **Open the Application**: Navigate to `http://localhost:3000`
4. **Chat with the AI**: Ask questions about scheduling, courses, or academic planning

### Example Queries

- "Help me plan a schedule for Fall 2025 with morning classes"
- "Generate a 4-year plan for Computer Science major"
- "Find courses with the best professors"
- "What are the easiest CS electives?"
- "Show me CMSC courses with high GPA averages"

## API Endpoints

### Chat
- `POST /api/v1/chat/chat` - Send a message to the AI assistant

### Schedules
- `POST /api/v1/schedules/generate` - Generate optimized schedules
- `GET /api/v1/schedules/{scheduleId}` - Get schedule details
- `DELETE /api/v1/schedules/{scheduleId}` - Delete a schedule

### Four-Year Plans
- `POST /api/v1/plans/generate` - Generate a four-year plan
- `GET /api/v1/plans/{planId}` - Get plan details
- `GET /api/v1/plans/user/{userId}` - Get all user plans
- `PUT /api/v1/plans/{planId}` - Update a plan
- `DELETE /api/v1/plans/{planId}` - Delete a plan

### Courses & Professors
- `GET /api/v1/courses` - Search for courses
- `GET /api/v1/courses/{courseCode}` - Get course details
- `GET /api/v1/professors/{professorName}` - Get professor details
- `GET /api/v1/departments` - List all departments

## Development

### Backend Development

The backend follows a modular architecture:

- **Routes** (`app/api/routes/`): API endpoint definitions
- **Services** (`app/services/`): Business logic and external API integrations
- **Models** (`app/models/`): Database models using SQLAlchemy
- **Schemas** (`app/schemas/`): Request/response validation using Pydantic

### Frontend Development

The frontend uses Next.js App Router with Material-UI:

- **Components** (`src/components/`): Reusable React components
- **Services** (`src/services/`): API communication layer
- **Types** (`src/types/`): TypeScript type definitions
- **App** (`src/app/`): Next.js pages and routing

### Code Style

Following user-defined nomenclature rules:
- UPPERCASE for environment variables
- camelCase for variables, functions, and methods
- Verbs for boolean variables (isLoading, hasError, canDelete)
- Complete words instead of abbreviations
- Functions with single purpose (<20 instructions)
- Use arrow functions for simple functions
- Use named functions for complex logic

## Future Roadmap

### Phase 2 - Extended Features
1. Interactive schedule visualization with drag-and-drop
2. Campus building and walking time integration
3. Collaborative planning with friends
4. Course and career insights using embeddings

### Phase 3 - Advanced Features
1. Mobile application (iOS/Android)
2. Real-time notifications for course availability
3. Integration with Testudo for automatic registration
4. Advanced analytics and recommendations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is for educational purposes.

## Acknowledgments

- University of Maryland
- PlanetTerp
- RateMyProfessor
- OpenAI

## Support

For questions or issues, please open an issue on GitHub.
