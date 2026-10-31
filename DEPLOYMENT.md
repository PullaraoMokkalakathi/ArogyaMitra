# ArogyaMitra - Deployment Guide

## A. Project Architecture

- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS + React Router DOM
- **Backend**: Python FastAPI + Uvicorn
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL (production) / SQLite (development)
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose) with bcrypt password hashing
- **AI Integrations**: Groq API (LLaMA models) and Google Gemini API
- **Computer Vision**: MediaPipe Pose for posture tracking
- **Rate Limiting**: slowapi
- **State Management**: Zustand (frontend)

## B. Local Development

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+ (tested on 3.13)
- Git

### Backend Setup (Windows PowerShell)

`powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
Copy-Item .env.example .env

# Edit .env with your configuration (API keys, etc.)
# For local dev, SQLite is used by default
`

### Frontend Setup (Windows PowerShell)

`powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment variables
Copy-Item .env.example .env

# Edit .env if needed (VITE_API_BASE_URL defaults to http://127.0.0.1:8000)
`

### Running Locally

`powershell
# Terminal 1 - Backend (from backend directory with venv activated)
=".\"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2 - Frontend (from frontend directory)
npm run dev
`

Frontend will be available at http://localhost:5173, backend at http://localhost:8000. API docs at http://localhost:8000/docs (disabled in production).

## C. Registration Schema

**POST /api/v1/auth/register** requires:
`json
{
  "email": "user@example.com",
  "password": "StrongPass123!",
  "confirm_password": "StrongPass123!",
  "full_name": "User Name"  // optional
}
`
Password must be at least 8 characters with uppercase, lowercase, and digit. Passwords must match.

## D. Environment Variables

### Backend (.env)
| Variable | Required | Description |
|----------|----------|-------------|
| ENVIRONMENT | Yes | development or production |
| DEBUG | Yes | 	rue/alse - disable in production |
| DATABASE_URL | Yes | SQLite or PostgreSQL connection string |
| JWT_SECRET_KEY` - **REQUIRED in production**. Generate with `python -c "import secrets; print(secrets.token_hex(32))"`. Must be at least 32 chars, cannot be empty or use the insecure default. App will refuse to start in production with invalid secret.
| JWT_ALGORITHM | Yes | Default HS256 |
| CORS_ORIGINS | Yes | Comma-separated allowed origins |
| GROQ_API_KEY | Optional | For AI features via Groq |
| GEMINI_API_KEY | Optional | For AI features via Gemini |
| PORT | Yes | Server port (Render sets automatically) |

### Frontend (.env)
| Variable | Required | Description |
|----------|----------|-------------|
| VITE_API_BASE_URL | Yes | Backend API base URL (no trailing slash) |

## D. Database Setup & Migrations

### Using Alembic

`powershell
# From backend directory with venv activated
# Check migration status
alembic current

# View migration history
alembic history

# Apply all migrations (production command)
alembic upgrade head

# Create new migration (after model changes)
alembic revision --autogenerate -m "description"

# Rollback one migration
alembic downgrade -1
`

**Note**: For production, always run lembic upgrade head before starting the application. The app also calls init_db() on startup which creates tables if missing (non-destructive).

## E. Deployment to Render (Backend)

### Setup
1. Create a new Web Service on [Render](https://render.com)
2. Connect your GitHub repository
3. Configure:
   - **Root Directory**: ackend
   - **Build Command**: pip install -r requirements.txt
   - **Start Command**: uvicorn app.main:app --host 0.0.0.0 --port
   - **Environment**: Python 3

### Environment Variables (Render)
Set the following in Render dashboard:
- ENVIRONMENT=production
- DEBUG=false
- DATABASE_URL - Use PostgreSQL from Render or Supabase (format: postgresql+psycopg://...)
- JWT_SECRET_KEY` - **REQUIRED in production**. Generate with `python -c "import secrets; print(secrets.token_hex(32))"`. Must be at least 32 chars, cannot be empty or use the insecure default. App will refuse to start in production with invalid secret.
- CORS_ORIGINS - Your Vercel frontend URL (e.g., https://your-app.vercel.app)
- GROQ_API_KEY / GEMINI_API_KEY as needed
- PORT is automatically set by Render

### Post-Deploy
Run migrations via Render Shell: lembic upgrade head

Health check endpoint: https://your-backend.onrender.com/health

## F. Deployment to Vercel (Frontend)

### Setup
1. Import project on [Vercel](https://vercel.com)
2. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: rontend (or use root vercel.json)
   - **Build Command**:
pm run build (or as specified in vercel.json)
   - **Output Directory**: dist

The included ercel.json handles SPA routing with rewrites to index.html.

### Environment Variables (Vercel)
Set in Project Settings > Environment Variables:
- VITE_API_BASE_URL - Your Render backend URL (e.g., https://your-backend.onrender.com)

## G. Database - Supabase (PostgreSQL)

1. Create project on [Supabase](https://supabase.com)
2. Get connection string from Settings > Database
3. Use format: postgresql+psycopg://postgres:[PASSWORD]@[HOST]:5432/postgres
4. Set as DATABASE_URL in backend environment
5. Run migrations: lembic upgrade head

**Note**: The app normalizes postgres:// URLs automatically to postgresql+psycopg://.

## H. CORS Configuration

- **Development**: Allows localhost origins from CORS_ORIGINS; if not specified or wildcard, allows all origins without credentials.
- **Production**: Only explicitly configured origins in CORS_ORIGINS are allowed (no wildcards, no automatic Vercel trust). Set to your exact frontend URL(s). To add additional trusted origins, update CORS_ORIGINS in environment variables.
- **Credentials**: Enabled when using specific origins; disabled in dev wildcard mode for safety.

## I. Security Checklist

- [ ] Change default JWT_SECRET_KEY` - **REQUIRED in production**. Generate with `python -c "import secrets; print(secrets.token_hex(32))"`. Must be at least 32 chars, cannot be empty or use the insecure default. App will refuse to start in production with invalid secret.
- [ ] Set DEBUG=false in production
- [ ] Configure specific CORS_ORIGINS (no wildcards in production)
- [ ] Use strong database credentials
- [ ] Never commit .env files (ensure in .gitignore)
- [ ] Rotate API keys if exposed
- [ ] Keep dependencies updated
- [ ] Disable Swagger/OpenAPI docs in production (automatic when DEBUG=false/ENVIRONMENT=production)
- [ ] Use HTTPS in production

## I. Testing

### Backend Tests
`powershell
cd backend
=".\"
pytest -v
`

### Frontend Build Test
`powershell
cd frontend
npm run build
`

## J. Troubleshooting

### Backend import errors
Ensure PYTHONPATH includes backend directory or run from backend folder.

### Database connection issues
- SQLite: Check file permissions
- PostgreSQL: Verify connection string format and network access

### CORS errors
Verify CORS_ORIGINS includes your frontend URL exactly (no trailing slash).

### Build errors
Check TypeScript errors with
pm run build and fix before deploying.

## K. Important Notes

- Camera/MediaPipe features require HTTPS in production browsers
- AI features require valid API keys (Groq/Gemini)
- The app uses rate limiting - configure as needed
- Health check at /health is used by deployment platforms for readiness
