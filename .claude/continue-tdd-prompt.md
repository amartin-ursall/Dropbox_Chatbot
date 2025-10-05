Handoff (Markdown) — Retomar proyecto más adelante
Objetivo

App web (React + Vite) + FastAPI que:

Bloquea el chat hasta que el usuario inicie sesión OAuth2 con Dropbox.

Un chatbot guía para renombrar el archivo y subirlo a una ruta sugerida en Dropbox.

Estado actual
AD-4 (Completado ✅)

Mapeo de rutas por tipo (insensible a mayúsculas/acentos).

Vista previa de nombre sugerido y ruta antes de subir.

Tests: 26 pasando (16 backend, 10 frontend).

Archivos clave:

backend/app/path_mapper.py

frontend/src/components/UploadPreview.tsx

Endpoints de subida integrados en app.main.

AD-5 (En progreso ⏳) — OAuth2 Dropbox (bloqueante)

Backend: backend/app/auth.py + endpoints en app.main → 10 tests pasando.

Frontend: LoginScreen.tsx con estilos + 6 tests creados (3 arreglados, 1 pendiente por matcher toBeDisabled).

Falta: Guard de autenticación en App.tsx (consultar /auth/status y bloquear chat si no hay sesión).

Datos de entorno (dev)

Frontend: http://localhost:5173

Backend: http://localhost:8000

Redirect URI Dropbox: http://localhost:8000/auth/dropbox/callback

Credenciales:

App Key: rvsal3as0j73d3y

App Secret: h933ko0ruapay5i

Sesión: en memoria (sessions dict, SESSION_KEY="default_session")

Endpoints relevantes

Auth (FastAPI)

GET /auth/dropbox/login → redirige a Dropbox

GET /auth/dropbox/callback?code=... → canjea token, guarda sesión, redirige al front

GET /auth/status → { authenticated: bool, account_id: str|null }

POST /auth/logout → limpia sesión

Flujo de archivos (AD-4)

POST /upload-temp → guarda temporal

POST /suggest-path → sugiere ruta y nuevo nombre

POST /upload-final → sube a Dropbox con el nombre final

Archivos clave

Backend

backend/app/main.py (endpoints auth + flujo AD-4)

backend/app/auth.py (OAuth2: generate_auth_url, exchange_code_for_token, store_session, get_session, clear_session)

backend/app/path_mapper.py (normaliza y mapea tipos a carpetas)

Tests: backend/tests/test_auth.py (10 OK) + tests AD-4

Frontend

frontend/src/components/LoginScreen.tsx (UI login Dropbox)

frontend/src/components/LoginScreen.test.tsx (6 tests; ajustar 1)

frontend/src/components/UploadPreview.tsx (vista previa nombre/ruta)

Pendiente: guard en App.tsx + (opcional) useAuth/context

Cómo ejecutar
# Backend
uvicorn app.main:app --reload --port 8000

# Frontend
npm run dev   # o pnpm dev

# Tests
pytest -q             # backend
npm run test          # frontend


Nota: CORS habilitado para http://localhost:5173 (ver middleware si falla).
Temp cross-platform: se usa tempfile.gettempdir() para evitar errores en Windows.

Punto exacto donde retomar

Arreglar test pendiente en LoginScreen.test.tsx

Error: Invalid Chai property: toBeDisabled

Cambiar por:

expect((connectButton as HTMLButtonElement).disabled).toBe(false)
// o
expect(connectButton).not.toHaveAttribute('disabled')


Añadir guard de autenticación en App.tsx (bloqueante)

Al montar: GET /auth/status

Si authenticated=false → renderizar <LoginScreen />

Si authenticated=true → mostrar chat/flujo AD-4.

Añadir tests:

Renderiza LoginScreen si no autenticado.

Renderiza chat si autenticado (mock /auth/status).

Verificar redirección post-callback

Backend redirige al front (:5173); el front debe re-consultar /auth/status y continuar al chat si ya hay sesión.

Flujo esperado (resumen)

Login: “Conectar con Dropbox” → Dropbox → callback → sesión guardada.

Chatbot: recoge tipo/cliente/fecha → genera nombre nuevo y ruta.

Vista previa: usuario confirma → subida a Dropbox con nombre final en ruta.

Criterios mínimos (Gherkin)
Background:
  Given el usuario ha iniciado sesión en Dropbox

Scenario: Subida guiada por chatbot
  When el usuario sube un archivo temporal
  And responde tipo, cliente y fecha
  Then el sistema sugiere nombre y ruta en Dropbox
  And al confirmar, el archivo se sube con el nombre final a la ruta indicada

Notas TDD y testing

Backend OAuth2 testea el callback con mock: patch("app.auth.exchange_code_for_token", new_callable=AsyncMock).

Frontend RTL: “Dropbox” aparece varias veces → usar getAllByText(/dropbox/i).

Mensaje informativo: usar getByText(/Conecta tu cuenta/i).

Definition of Done (AD-5)

✅ 10/10 tests backend OAuth2 en verde.

✅ Tests LoginScreen en verde (incluido el fix de toBeDisabled).

✅ App.tsx bloquea chat si no hay sesión.

✅ Tras callback, se entra al chat si authenticated=true.

Último archivo editado: frontend/src/components/LoginScreen.test.tsx (tests 10 y 12 ajustados; queda matcher de disabled).