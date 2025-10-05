# 🎯 AD-5: Autenticación OAuth2 con Dropbox (BLOQUEANTE)

## Contexto Actualizado
**CAMBIO CRÍTICO**: El usuario DEBE autenticarse en Dropbox ANTES de cualquier interacción con el chat.

**Flujo anterior** (AD-1 a AD-4):
1. Usuario sube archivo
2. Responde preguntas
3. Ve preview

**Nuevo flujo** (AD-5 como prerequisito):
1. **🔒 Usuario inicia sesión en Dropbox (AD-5)** ← BLOQUEANTE
2. Usuario sube archivo (AD-1)
3. Responde preguntas (AD-2, AD-3)
4. Ve preview (AD-4)
5. Confirma y sube a Dropbox (AD-6)

## User Story
**US-00 (nueva)**: Como usuario, quiero iniciar sesión en Dropbox antes de usar el chat, para autorizar la subida de archivos a mi cuenta.

## Criterios de Aceptación (Gherkin)

```gherkin
Background:
  Given la aplicación está iniciada
  And el usuario NO ha iniciado sesión en Dropbox

Scenario: Mostrar pantalla de login al iniciar
  Given el usuario abre la aplicación
  When la app detecta que no hay sesión activa
  Then muestra la pantalla de "Iniciar sesión con Dropbox"
  And NO muestra el chat ni el upload de archivos

Scenario: Iniciar OAuth2 flow
  Given el usuario está en la pantalla de login
  When hace click en "Conectar con Dropbox"
  Then el backend genera la URL de autorización
  And redirige al usuario a Dropbox OAuth2

Scenario: Callback exitoso de Dropbox
  Given el usuario autorizó la app en Dropbox
  When Dropbox redirige con el código de autorización
  Then el backend intercambia el código por access_token
  And almacena el token de forma segura
  And redirige al usuario al chat principal

Scenario: Sesión activa - Skip login
  Given el usuario ya tiene una sesión activa
  When abre la aplicación
  Then va directamente al chat
  And NO muestra la pantalla de login

Scenario: Logout
  Given el usuario tiene sesión activa
  When hace click en "Cerrar sesión"
  Then el sistema elimina el token
  And redirige a la pantalla de login
```

## Invariantes del Producto

### OAuth2 Flow (Dropbox)
- **App Key**: `rvsal3as0j73d3y`
- **App Secret**: `h933ko0ruapay5i`
- **Redirect URI**: `http://localhost:8000/auth/dropbox/callback`
- **Scopes**: `files.content.write` (para subir archivos)

### Almacenamiento de Token
- **Backend**: Memoria (sesión) - En producción sería DB
- **Frontend**: SessionStorage (NO localStorage para mayor seguridad)
- **Formato**: `{ "access_token": "...", "account_id": "...", "expires_at": "..." }`

### Endpoints OAuth2

```python
GET /auth/dropbox/login
# Genera URL de autorización y redirige

GET /auth/dropbox/callback?code=...
# Recibe código, intercambia por token, almacena, redirige a frontend

GET /auth/status
# Verifica si hay sesión activa
# Response: { "authenticated": true/false, "account_id": "..." }

POST /auth/logout
# Elimina token de sesión
# Response: { "success": true }
```

## Componente Frontend Esperado

### LoginScreen Component
```tsx
interface LoginScreenProps {
  onLoginSuccess: () => void
}

// Muestra:
// - Logo de Dropbox
// - Botón "Conectar con Dropbox"
// - Mensaje: "Necesitas conectar tu cuenta de Dropbox para continuar"
```

### AuthContext (opcional pero recomendado)
```tsx
interface AuthContextValue {
  isAuthenticated: boolean
  accountId: string | null
  login: () => void
  logout: () => void
}
```

### App.tsx - Guard de autenticación
```tsx
function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check auth status on mount
    checkAuthStatus()
  }, [])

  if (isLoading) return <div>Cargando...</div>
  if (!isAuthenticated) return <LoginScreen onLoginSuccess={...} />

  // Chat normal (AD-1 a AD-4)
  return <ChatInterface />
}
```

## Archivos a Crear/Modificar

**Backend**:
- ✨ `backend/app/auth.py` - Módulo de autenticación OAuth2
- ✨ `backend/tests/test_auth.py` - Tests de OAuth2 flow
- ✏️ `backend/app/main.py` - Agregar endpoints de auth
- ✨ `backend/.env.example` - Variables de entorno

**Frontend**:
- ✨ `frontend/src/components/LoginScreen.tsx` - Pantalla de login
- ✨ `frontend/src/components/LoginScreen.test.tsx` - Tests
- ✨ `frontend/src/hooks/useAuth.ts` - Hook de autenticación
- ✏️ `frontend/src/App.tsx` - Guard de autenticación
- ✏️ `frontend/src/types/api.ts` - Tipos de auth

**E2E**:
- ✨ `e2e/auth-flow.spec.ts` - Tests E2E de login

## Lista de Pruebas Derivadas

| # | Descripción | Capa | Estado |
|---|------------|------|--------|
| 1 | Backend genera URL de autorización correcta | Backend | ❌ |
| 2 | URL incluye app_key, redirect_uri, response_type | Backend | ❌ |
| 3 | Callback intercambia código por token | Backend | ❌ |
| 4 | Callback almacena token en sesión | Backend | ❌ |
| 5 | /auth/status retorna true si hay token | Backend | ❌ |
| 6 | /auth/status retorna false si no hay token | Backend | ❌ |
| 7 | /auth/logout elimina token | Backend | ❌ |
| 8 | Frontend muestra LoginScreen si no auth | Frontend | ❌ |
| 9 | Frontend muestra chat si auth | Frontend | ❌ |
| 10 | Botón "Conectar" inicia OAuth flow | Frontend | ❌ |
| 11 | E2E: Login completo redirige al chat | E2E | ❌ |
| 12 | E2E: Logout redirige a login | E2E | ❌ |

## Implementación Backend - OAuth2

### Módulo auth.py
```python
from typing import Optional
import httpx
from fastapi import HTTPException

DROPBOX_APP_KEY = "rvsal3as0j73d3y"
DROPBOX_APP_SECRET = "h933ko0ruapay5i"
DROPBOX_REDIRECT_URI = "http://localhost:8000/auth/dropbox/callback"

# In-memory token storage (producción: DB)
sessions: dict[str, dict] = {}

def generate_auth_url() -> str:
    """Generate Dropbox OAuth2 authorization URL"""
    return (
        f"https://www.dropbox.com/oauth2/authorize"
        f"?client_id={DROPBOX_APP_KEY}"
        f"&redirect_uri={DROPBOX_REDIRECT_URI}"
        f"&response_type=code"
        f"&token_access_type=offline"
    )

async def exchange_code_for_token(code: str) -> dict:
    """Exchange authorization code for access token"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.dropboxapi.com/oauth2/token",
            data={
                "code": code,
                "grant_type": "authorization_code",
                "client_id": DROPBOX_APP_KEY,
                "client_secret": DROPBOX_APP_SECRET,
                "redirect_uri": DROPBOX_REDIRECT_URI,
            }
        )
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code")
        return response.json()
```

## Notas de Seguridad

1. **NO exponer App Secret en frontend**
2. **Usar HTTPS en producción** (localhost OK para dev)
3. **Token en SessionStorage** (se borra al cerrar pestaña)
4. **Validar redirect_uri** en Dropbox App Console

## Definition of Done (DoD)

- [ ] ✅ 12 tests passing (7 backend, 3 frontend, 2 E2E)
- [ ] ✅ OAuth2 flow completo funciona
- [ ] ✅ Usuario NO puede acceder al chat sin login
- [ ] ✅ Token se almacena correctamente
- [ ] ✅ Logout funciona y redirige a login
- [ ] ✅ Sin regresiones en AD-1 a AD-4
- [ ] ✅ Commits con mensaje "(AD-5)"
- [ ] ✅ PR description completo

## Notas Técnicas

### Dropbox API - Verificar cuenta
```python
# Endpoint para verificar token
GET https://api.dropboxapi.com/2/users/get_current_account
Headers:
  Authorization: Bearer <access_token>

Response:
{
  "account_id": "dbid:...",
  "name": { "display_name": "..." },
  "email": "..."
}
```

### Frontend - Check auth on mount
```tsx
useEffect(() => {
  async function checkAuth() {
    const response = await fetch('/auth/status')
    const data = await response.json()
    setIsAuthenticated(data.authenticated)
    setIsLoading(false)
  }
  checkAuth()
}, [])
```

## Comandos

```bash
# Backend - Instalar httpx para OAuth2
pip install httpx

# Backend - Tests
pytest tests/test_auth.py -v

# Frontend - Tests
pnpm test LoginScreen --run

# E2E
pnpm test:e2e auth-flow
```

## Flujo de Ejecución

1. **Usuario abre app** → Frontend verifica `/auth/status`
2. **Si no auth** → Muestra `LoginScreen`
3. **Click "Conectar"** → Backend genera URL → Redirige a Dropbox
4. **Usuario autoriza** → Dropbox redirige a `/auth/dropbox/callback?code=...`
5. **Backend intercambia código** → Obtiene token → Almacena → Redirige a frontend
6. **Frontend detecta auth** → Muestra chat normal

## Integración con AD-1 a AD-4

Todos los endpoints existentes requerirán validar autenticación:
- `POST /api/upload-temp` → Verificar token
- `POST /api/questions/*` → Verificar token
- Etc.

Esto se implementará en AD-6 como middleware de autenticación.
