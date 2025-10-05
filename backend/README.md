# Backend - Dropbox Chatbot Organizer

API REST desarrollada con FastAPI para gestionar la autenticación con Dropbox y el flujo de organización de archivos.

## Tecnologías

- **FastAPI 0.104+**: Framework web moderno para APIs
- **Python 3.8+**: Lenguaje de programación
- **httpx**: Cliente HTTP asíncrono
- **Pydantic**: Validación de datos
- **Uvicorn**: Servidor ASGI de alto rendimiento

## Estructura del proyecto

```
backend/
├── app/
│   ├── main.py              # Aplicación principal FastAPI
│   ├── auth.py              # Autenticación OAuth2 con Dropbox
│   ├── validators.py        # Validadores de entrada con sugerencias
│   ├── questions.py         # Flujo de preguntas
│   ├── path_mapper.py       # Mapeo de rutas de Dropbox
│   └── dropbox_uploader.py  # Subida de archivos a Dropbox
├── requirements.txt         # Dependencias del proyecto
└── README.md               # Este archivo
```

## Instalación

### 1. Crear entorno virtual

```bash
cd backend
python -m venv venv
```

### 2. Activar entorno virtual

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar credenciales de Dropbox

Edita `app/auth.py` con tus credenciales de Dropbox App Console:

```python
DROPBOX_APP_KEY = "tu_app_key"
DROPBOX_APP_SECRET = "tu_app_secret"
DROPBOX_REDIRECT_URI = "http://localhost:8000/auth/dropbox/callback"
```

**Cómo obtener las credenciales:**
1. Ve a [Dropbox App Console](https://www.dropbox.com/developers/apps)
2. Crea una nueva app o usa una existente
3. En la configuración de la app, obtén el `App key` y `App secret`
4. Agrega `http://localhost:8000/auth/dropbox/callback` a las URIs de redirección

## Ejecutar el servidor

### Modo desarrollo (con auto-reload)

```bash
uvicorn app.main:app --reload
```

### Modo producción

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

El servidor estará disponible en `http://localhost:8000`

## Documentación de la API

FastAPI genera documentación automática:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Endpoints

### Autenticación

#### `GET /auth/dropbox/login`
Inicia el flujo de autenticación OAuth2 con Dropbox.

**Respuesta:** Redirección a la página de autorización de Dropbox

#### `GET /auth/dropbox/callback`
Callback de OAuth2. Dropbox redirige aquí después de la autorización.

**Query Parameters:**
- `code`: Código de autorización de Dropbox

**Respuesta:** Redirección al frontend

#### `GET /auth/status`
Verifica el estado de autenticación del usuario.

**Respuesta:**
```json
{
  "authenticated": true,
  "account_id": "dbid:..."
}
```

#### `POST /auth/logout`
Cierra la sesión del usuario.

**Respuesta:**
```json
{
  "success": true
}
```

### Información de usuario

#### `GET /api/user/info`
Obtiene información de la cuenta de Dropbox del usuario autenticado.

**Respuesta:**
```json
{
  "name": "Alberto Morin",
  "email": "usuario@ejemplo.com",
  "used_space": 1232370,
  "allocated_space": 2147483648,
  "account_type": "Basic",
  "profile_photo_url": "https://..."
}
```

### Gestión de archivos

#### `POST /api/upload-temp`
Sube un archivo al almacenamiento temporal.

**Request:**
- `Content-Type: multipart/form-data`
- `file`: Archivo a subir

**Validaciones:**
- Tamaño máximo: 10 MB
- Extensiones permitidas: .pdf, .docx, .txt, .jpg, .png

**Respuesta:**
```json
{
  "file_id": "uuid-generado",
  "original_name": "documento.pdf",
  "size": 1024,
  "extension": ".pdf"
}
```

#### `POST /api/questions/start`
Inicia el flujo de preguntas para clasificar el archivo.

**Request Body:**
```json
{
  "file_id": "uuid-del-archivo"
}
```

**Respuesta:**
```json
{
  "question_id": "doc_type",
  "question_text": "¿Qué tipo de documento es?",
  "examples": ["factura", "contrato", "presupuesto"]
}
```

#### `POST /api/questions/answer`
Envía la respuesta a una pregunta.

**Request Body:**
```json
{
  "file_id": "uuid-del-archivo",
  "question_id": "doc_type",
  "answer": "factura"
}
```

**Respuesta:**
```json
{
  "next_question": {
    "question_id": "client",
    "question_text": "¿Cuál es el nombre del cliente?",
    "examples": []
  },
  "completed": false
}
```

**Errores con sugerencias:**
```json
{
  "detail": {
    "detail": "Tipo de documento no válido",
    "suggestion": "Quizás quisiste decir: 'factura'"
  }
}
```

#### `POST /api/questions/generate-name`
Genera un nombre de archivo sugerido basado en las respuestas.

**Request Body:**
```json
{
  "file_id": "uuid-del-archivo",
  "answers": {
    "doc_type": "factura",
    "client": "Empresa XYZ",
    "date": "2025-01-15"
  },
  "original_extension": ".pdf"
}
```

**Respuesta:**
```json
{
  "suggested_name": "2025-01-15_factura_empresa-xyz.pdf",
  "original_extension": ".pdf",
  "suggested_path": "/Facturas",
  "full_path": "/Facturas/2025-01-15_factura_empresa-xyz.pdf"
}
```

#### `POST /api/suggest-path`
Sugiere una ruta de Dropbox basada en el tipo de documento.

**Request Body:**
```json
{
  "doc_type": "factura",
  "client": "Empresa XYZ",
  "date": "2025-01-15"
}
```

**Respuesta:**
```json
{
  "suggested_path": "/Facturas",
  "suggested_name": "2025-01-15_factura_empresa-xyz.pdf",
  "full_path": "/Facturas/2025-01-15_factura_empresa-xyz.pdf"
}
```

#### `POST /api/upload-final`
Sube el archivo definitivo a Dropbox.

**Request Body:**
```json
{
  "file_id": "uuid-del-archivo",
  "new_filename": "2025-01-15_factura_empresa-xyz.pdf",
  "dropbox_path": "/Facturas"
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Archivo subido exitosamente a Dropbox",
  "dropbox_path": "/Facturas/2025-01-15_factura_empresa-xyz.pdf",
  "dropbox_name": "2025-01-15_factura_empresa-xyz.pdf",
  "size": 1024
}
```

## Módulos principales

### `app/main.py`
Aplicación principal FastAPI con todos los endpoints y configuración de CORS.

### `app/auth.py`
Gestión de autenticación OAuth2 con Dropbox:
- Generación de URL de autorización
- Intercambio de código por token
- Gestión de sesiones persistentes en archivo local
- Obtención de access token

**Archivo de sesión:** `~/.dropbox_chatbot_session.json`

### `app/validators.py`
Validadores avanzados con sugerencias automáticas:
- Validación de archivos (tamaño y extensión)
- Validación de tipos de documento con fuzzy matching
- Validación de fechas con múltiples formatos
- Validación de nombres de cliente
- Generación de sugerencias para errores comunes

### `app/questions.py`
Define el flujo de preguntas:
- Secuencia: doc_type → client → date
- Generación de preguntas con ejemplos
- Navegación entre preguntas

### `app/path_mapper.py`
Mapeo de tipos de documento a rutas de Dropbox:
- Facturas → `/Facturas`
- Contratos → `/Contratos`
- Presupuestos → `/Presupuestos`
- Otros → `/Documentos`

### `app/dropbox_uploader.py`
Gestión de subida de archivos a Dropbox:
- Subida de archivos con manejo de errores
- Creación automática de carpetas
- Verificación de duplicados

## Validaciones

### Archivos
- **Tamaño máximo:** 10 MB
- **Extensiones permitidas:** `.pdf`, `.docx`, `.txt`, `.jpg`, `.png`, `.xlsx`, `.csv`

### Tipos de documento
Válidos: `factura`, `contrato`, `presupuesto`, `informe`, `certificado`, `recibo`, `nota`, `albarán`

Con sugerencias automáticas para variaciones comunes.

### Fechas
Formatos aceptados:
- `YYYY-MM-DD` (2025-01-15)
- `DD/MM/YYYY` (15/01/2025)
- `DD-MM-YYYY` (15-01-2025)

Conversión automática al formato estándar `YYYY-MM-DD`.

### Cliente
- Mínimo 2 caracteres
- Sanitización automática para nombres de archivo

## Gestión de sesiones

Las sesiones se almacenan en `~/.dropbox_chatbot_session.json`:

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

## Configuración CORS

El backend permite peticiones desde:
- `http://localhost:5173` (Frontend en desarrollo)

Para producción, actualiza `allow_origins` en `app/main.py`.

## Desarrollo

### Agregar nuevos tipos de documento

Edita `app/validators.py`:

```python
VALID_DOC_TYPES = [
    "factura", "contrato", "presupuesto",
    "nuevo_tipo"  # Agregar aquí
]
```

Edita `app/path_mapper.py`:

```python
def suggest_path(doc_type: str) -> str:
    mapping = {
        "factura": "/Facturas",
        "nuevo_tipo": "/NuevoTipo"  # Agregar aquí
    }
```

### Agregar nuevas preguntas

Edita `app/questions.py`:

```python
QUESTIONS = {
    "nueva_pregunta": {
        "text": "¿Nueva pregunta?",
        "examples": ["ejemplo1", "ejemplo2"]
    }
}

QUESTION_ORDER = ["doc_type", "client", "date", "nueva_pregunta"]
```

## Logging

El backend utiliza el logger de Python. Para ver logs detallados:

```bash
uvicorn app.main:app --log-level debug
```

## Testing

Ejecutar tests (cuando estén disponibles):

```bash
pytest
```

## Solución de problemas

### Error: "Not authenticated"
- Verifica que el usuario haya iniciado sesión
- Comprueba el archivo `~/.dropbox_chatbot_session.json`

### Error: "Error fetching Dropbox account info"
- Verifica las credenciales de Dropbox en `app/auth.py`
- Comprueba que el token de acceso sea válido
- Revisa los logs del servidor para más detalles

### Error al subir archivos
- Verifica que el tamaño del archivo sea menor a 10 MB
- Comprueba que la extensión sea válida
- Asegúrate de que el usuario tenga permisos en Dropbox

## Recursos

- [Documentación de FastAPI](https://fastapi.tiangolo.com/)
- [Dropbox API Documentation](https://www.dropbox.com/developers/documentation)
- [OAuth 2.0](https://oauth.net/2/)

## Contribución

Para contribuir al backend:
1. Crea una rama para tu feature
2. Asegúrate de que el código pase las validaciones de tipo
3. Documenta nuevos endpoints
4. Actualiza este README si es necesario
