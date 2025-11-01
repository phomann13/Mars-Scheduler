# Quick Setup Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (optional, can use Docker)
- Redis (optional, can use Docker)

## Option 1: Docker Setup (Recommended)

The easiest way to get started is using Docker Compose:

1. **Install Docker and Docker Compose**
   - Follow instructions at https://docs.docker.com/get-docker/

2. **Set environment variables**
   ```bash
   echo "OPENAI_API_KEY=your-openai-api-key" > .env
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

5. **Stop services**
   ```bash
   docker-compose down
   ```

## Option 2: Manual Setup

### Backend Setup

1. **Create virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your settings
   ```

4. **Start backend server**
   ```bash
   python -m app.main
   ```

   Or with uvicorn:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment**
   ```bash
   echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

## Database Setup (Optional)

If running PostgreSQL locally:

1. **Create database**
   ```bash
   createdb umd_scheduler
   ```

2. **Run migrations** (if available)
   ```bash
   cd backend
   alembic upgrade head
   ```

## Configuration

### Required Environment Variables

**Backend (.env)**
- `OPENAI_API_KEY` - Your OpenAI API key (required for AI features)
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string

**Frontend (.env.local)**
- `NEXT_PUBLIC_API_URL` - Backend API URL

### Optional Environment Variables

- `PINECONE_API_KEY` - For vector store (Phase 2)
- `PINECONE_ENVIRONMENT` - Pinecone environment
- `PINECONE_INDEX_NAME` - Pinecone index name

## Testing the Setup

1. **Backend health check**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Frontend**
   - Open http://localhost:3000
   - You should see the chat interface

3. **Test API endpoints**
   - Visit http://localhost:8000/docs for interactive API documentation

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (should be 3.11+)
- Verify all environment variables are set
- Check database connection

### Frontend won't start
- Check Node version: `node --version` (should be 18+)
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`
- Check that backend is running

### Database connection errors
- Verify PostgreSQL is running
- Check DATABASE_URL format: `postgresql://user:password@host:port/database`
- Test connection: `psql $DATABASE_URL`

### OpenAI API errors
- Verify OPENAI_API_KEY is set correctly
- Check API key has sufficient credits
- Test key: `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`

## Next Steps

1. **Populate curriculum data** - Add course and major requirements
2. **Import professor ratings** - Fetch data from PlanetTerp and RateMyProfessor
3. **Test schedule generation** - Try generating schedules with the AI
4. **Create four-year plans** - Test plan generation for different majors

## Development

### Backend Development
- Code is in `backend/app/`
- FastAPI auto-reloads on file changes
- API docs at http://localhost:8000/docs

### Frontend Development
- Code is in `frontend/src/`
- Next.js hot-reloads on file changes
- Components are in `src/components/`

### Code Style
- Follow nomenclature rules in user_rules
- Use camelCase for variables/functions
- Use type hints (Python) and TypeScript
- Keep functions small and focused

## Getting Help

- Check README.md for detailed documentation
- Review Design-Doc.md for architecture details
- Open an issue on GitHub for bugs

