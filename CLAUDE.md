# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Dropbox AI Organizer is a full-stack web application with a specialized legal document organization system (URSALL). It uses a conversational chatbot to guide users through uploading files to Dropbox with intelligent naming and folder structures.

The application operates in HTTPS mode with a custom domain `dropboxaiorganizer.com` for both development and production.

## Architecture

### Two-System Design

The application supports **two distinct workflows**:

1. **Standard Workflow**: General document organization (facturas, contratos, presupuestos)
2. **URSALL Legal System**: Specialized for legal case management with complex folder structures

The codebase is unified in `backend/app/main.py` which handles both workflows. URSALL functionality is integrated directly into the main application.

### Backend (FastAPI + Python)

**Main Components:**
- `backend/app/main.py` - Single unified FastAPI app with URSALL endpoints
- `backend/app/auth.py` - OAuth2 session management with persistent file storage at `~/.dropbox_chatbot_session.json`
- `backend/app/dropbox_uploader.py` - Handles file uploads and folder creation in Dropbox

**URSALL Legal System:**
- `backend/app/questions_ursall.py` - Question flow (11 for procedures, 7 for projects)
- `backend/app/path_mapper_ursall.py` - Generates complex folder structures following legal naming conventions
- `backend/app/nlp_extractor_legal.py` - Extracts legal information from natural language (jurisdictions, case numbers, parties)
- `backend/app/gemini_rest_extractor.py` - AI-powered document information extraction using Gemini

**Validation:**
- `backend/app/validators.py` - File validation (size, extensions) and input sanitization

### Frontend (React + TypeScript + Vite)

**Key Components:**
- `frontend/src/App.tsx` - Main app with conversation state management
- `frontend/src/components/QuestionFlow.tsx` - Handles the question/answer flow (24KB, complex)
- `frontend/src/components/UserInfo.tsx` - User panel with 5-minute localStorage cache
- `frontend/src/components/NotificationIcon.tsx` - Persistent notification system
- `frontend/src/contexts/UserContext.tsx` - Shared authentication state

**UI Features:**
- Smooth CSS animations (200ms transitions)
- Click-outside-to-close behavior for panels
- Drag-and-drop file upload
- Real-time typing indicators

## Common Commands

### Development

**Start both servers (recommended):**
```bash
# Windows
scripts\start-dev.bat

# Linux/Mac
./scripts/start-dev.sh
```

This script:
- Checks/installs dependencies automatically
- Starts backend on `http://0.0.0.0:8000` with auto-reload
- Starts frontend on `https://dropboxaiorganizer.com:5173`
- Opens in separate terminal windows

**Manual start:**
```bash
# Backend (in backend/)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (in frontend/)
npm install
npm run dev
```

### Testing

**Backend:**
```bash
cd backend
pytest                                    # Run all tests
pytest tests/test_validators.py          # Single test file
pytest -v                                 # Verbose output
pytest --cov=app                          # With coverage
```

**Frontend:**
```bash
cd frontend
npm test                                  # Run tests with Vitest
npm run test:ui                          # Interactive test UI
npm run coverage                         # Coverage report
```

**Test specific component:**
```bash
npm test -- QuestionFlow.test.tsx
```

### Build

```bash
# Frontend production build
cd frontend
npm run build                            # Output to dist/

# Preview production build
npm run preview
```

### API Documentation

FastAPI provides auto-generated docs:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## HTTPS & Domain Setup

**Critical:** This app requires HTTPS and uses a custom domain for OAuth callbacks.

### hosts file configuration (required):

**Windows:** `C:\Windows\System32\drivers\etc\hosts`
**Linux/Mac:** `/etc/hosts`

Add:
```
127.0.0.1 dropboxaiorganizer.com
```

### SSL Certificates

Self-signed certificates are in `frontend/ssl/`:
- `cert.pem` - Certificate
- `key.pem` - Private key

Browser will show security warning on first visit - this is expected for development.

## Environment Configuration

### Backend `.env` (required)

Create `backend/.env`:
```bash
DROPBOX_APP_KEY=your_app_key
DROPBOX_APP_SECRET=your_app_secret
GEMINI_API_KEY=your_gemini_api_key
FRONTEND_URL=https://dropboxaiorganizer.com
```

**Dropbox OAuth Setup:**
- Create app at https://www.dropbox.com/developers/apps
- Add redirect URI: `http://localhost:8000/auth/dropbox/callback` (dev)
- For production: Update to your production domain

### Frontend `.env` (optional)

Frontend uses `VITE_API_BASE_URL` but defaults to `http://localhost:8000`.

## URSALL Legal System

### Folder Structure Generation

URSALL creates **procedimiento** (judicial procedure) or **proyecto** (legal project) folder structures:

**Procedimiento format:**
```
/CLIENTE/1. Procedimientos Judiciales/
  AAAA_MM_Juzgado_Demarcación_NºProc/AAAA_ParteA Vs ParteB_Materia/
    01. Escritos presentados/
    02. Resoluciones judiciales/
    03. Pruebas/
      03.1 Testifical/
      03.2 Pericial/
      03.3 Documental/
    ... (10 standard folders total)
```

**Proyecto format:**
```
/CLIENTE/2. Proyectos Jurídicos/
  AAAA_MM_Cliente_Proyecto_Materia/
    00. General/
    01. Documentación recibida/
    02. Borradores/
    ... (8 standard folders total)
```

### Key URSALL Functions

**Path generation:** `backend/app/path_mapper_ursall.py`
- `suggest_path_ursall()` - Main entry point, returns full structure
- `build_procedimiento_name()` - Constructs procedure folder name
- `build_proyecto_name()` - Constructs project folder name

**NLP extraction:** `backend/app/nlp_extractor_legal.py`
- Parses natural language: "Juzgado Social 2 de Tenerife" → extracts jurisdiction, number, location
- `extract_partes()` - Extracts parties from "A vs B" or "Actor contra Demandado"
- Handles various date formats and case number formats (XXX/YYYY)

**Question flow:** `backend/app/questions_ursall.py`
- Procedimiento: 11 questions (tipo_trabajo, client, jurisdiccion, juzgado_num, etc.)
- Proyecto: 7 questions (tipo_trabajo, client, proyecto_year, etc.)
- `get_next_question_ursall()` - Dynamically determines next question based on tipo_trabajo

### URSALL Endpoints

All under `/api/`:
- `POST /api/questions/start` - Begin question flow
- `POST /api/questions/answer` - Submit answer (NLP extraction happens here)
- `POST /api/questions/generate-path` - Generate full path + folder structure
- `POST /api/upload-final` - Create folders + upload file

## Key Implementation Patterns

### Session Management

URSALL sessions are stored in-memory:
```python
ursall_sessions: Dict[str, Dict] = {}
# Key: file_id
# Value: {current_question, answers, extracted_answers}
```

For production, migrate to database or Redis.

### Dropbox Session Persistence

OAuth tokens stored at `~/.dropbox_chatbot_session.json`:
```json
{
  "default_session": {
    "access_token": "...",
    "account_id": "...",
    "uid": "...",
    "token_type": "bearer"
  }
}
```

### Frontend User Info Caching

`UserInfo.tsx` implements 5-minute localStorage cache:
```typescript
const CACHE_DURATION = 5 * 60 * 1000  // 5 minutes
```

Cache key: `userInfoCache`

### Notification System

Persistent notifications in `NotificationIcon.tsx`:
- Don't auto-dismiss
- User must click "X" to dismiss
- Click-outside closes dropdown
- Smooth slide-in/slide-out animations

### Answer Extraction Flow

When user answers in URSALL:
1. Raw answer received
2. NLP extractor processes based on question_id
3. Validation applied
4. Extracted value stored in session
5. Special handling for "partes" question → splits into parte_a and parte_b

## File Upload Flow

### Standard Flow:
1. Upload to temp → `POST /api/upload-temp`
2. Start questions → `POST /api/questions/start`
3. Answer each → `POST /api/questions/answer`
4. Generate name → `POST /api/questions/generate-name`
5. Upload final → `POST /api/upload-final`

### URSALL Flow:
Same endpoints but with URSALL-specific logic:
1. `POST /api/upload-temp` (same)
2. `POST /api/questions/start` (returns tipo_trabajo)
3. `POST /api/questions/answer` (NLP extraction + validation)
4. `POST /api/questions/generate-path` (complex folder structure)
5. `POST /api/upload-final` (creates all folders + uploads)

## Code Style & Conventions

### Backend
- Use `async/await` for all I/O operations
- Type hints on all functions
- Pydantic models for request/response validation
- Logging via `logging.getLogger(__name__)`
- HTTPException for error responses with detailed error objects

### Frontend
- TypeScript strict mode
- Functional components with hooks
- CSS Modules for component styles (`.css` files next to `.tsx`)
- Props defined as TypeScript interfaces
- Error boundaries for robustness

### Naming Conventions
- Backend: snake_case for functions/variables
- Frontend: camelCase for functions/variables, PascalCase for components
- CSS: BEM-style classes (`component__element--modifier`)

## Important Files to Know

**Session storage:**
- `~/.dropbox_chatbot_session.json` - Dropbox OAuth tokens

**Temp files:**
- System temp directory / `dropbox_chatbot/` - Uploaded files before processing

**Configuration:**
- `backend/.env` - Backend environment variables (not in git)
- `frontend/ssl/` - SSL certificates for HTTPS

**Documentation:**
- `docs/URSALL_IMPLEMENTATION.md` - Detailed URSALL technical docs
- `docs/URSALL_USAGE.md` - URSALL usage guide
- `docs/HTTPS_SETUP.md` - HTTPS configuration guide

## Common Gotchas

### CORS Issues
- Backend CORS configured for `dropboxaiorganizer.com` and localhost variants
- If adding new frontend URL, update `FRONTEND_URLS` in `main.py`

### OAuth Callback Mismatch
- OAuth redirect URI must match exactly between Dropbox App Console and backend
- Dev: `http://localhost:8000/auth/dropbox/callback`
- Prod: `https://yourdomain.com/auth/dropbox/callback`

### URSALL parte_a/parte_b Extraction
- The "partes" question returns a single answer but must be split into two fields
- Special handling in `POST /api/questions/answer` around line 366-407
- If extraction fails, provide helpful error message

### Frontend HTTPS Certificate
- Browser will warn about self-signed cert
- Users must click "Advanced" → "Proceed" on first visit
- For production, use Let's Encrypt or valid CA certificate

## Deployment

Production deployment uses IIS on Windows Server:
- See `docs/PRODUCTION_DEPLOYMENT.md` for complete guide
- See `deployment/` folder for PowerShell scripts
- Key: Update OAuth redirect URIs, SSL certificates, environment variables

## AI/ML Integration

**Gemini API** is used for intelligent document extraction:
- `backend/app/gemini_rest_extractor.py` - REST API client
- Fallback to NLP extractors if Gemini unavailable
- Check status: `GET /health` (includes Gemini status)

## Adding New Document Types

### For Standard Workflow:
1. Add to `VALID_DOC_TYPES` in `validators.py`
2. Add path mapping in `path_mapper.py`

### For URSALL:
1. Add to document type options in `questions_ursall.py`
2. Add mapping in `path_mapper_ursall.py`:
   - `DOC_TYPE_TO_PROCEDIMIENTO_FOLDER` for procedures
   - `DOC_TYPE_TO_PROYECTO_FOLDER` for projects
