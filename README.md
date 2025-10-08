# Dropbox Chatbot Organizer

Aplicación web completa para organizar y subir archivos a Dropbox de forma inteligente mediante un asistente conversacional.

## Descripción

Este proyecto permite a los usuarios interactuar con un chatbot que les guía en el proceso de subir archivos a Dropbox de manera organizada, generando nombres de archivo descriptivos y sugiriendo rutas basadas en el tipo de documento.

## Características principales

- **🔒 HTTPS Seguro**: Configuración completa con SSL/TLS para conexiones seguras
- **🌐 Dominio Personalizado**: Acceso a través de `https://dropboxaiorganizer.com` (sin puerto visible)
- **🔐 Autenticación OAuth2 con Dropbox**: Inicio de sesión seguro usando OAuth2
- **🤖 Asistente conversacional**: Guía paso a paso para organizar archivos
- **🧠 Sugerencias inteligentes**: Nombres de archivo y rutas sugeridas automáticamente
- **✅ Validación avanzada**: Validación de fechas, tipos de documento y clientes con sugerencias en caso de error
- **📊 Información de usuario**: Panel de información con datos de la cuenta de Dropbox en tiempo real con caché inteligente
- **🔔 Sistema de notificaciones**: Notificaciones persistentes con gestión avanzada y animaciones
- **🎨 Interfaz moderna**: UI responsive con diseño oscuro y animaciones fluidas
- **⚖️ Sistema URSALL Legal**: Gestión especializada de procedimientos judiciales y proyectos legales
- **📁 Organización inteligente**: Estructura de carpetas automática por año, cliente, jurisdicción, etc.

## Tecnologías utilizadas

### Backend
- **FastAPI**: Framework web moderno y rápido para Python
- **Python 3.8+**: Lenguaje de programación
- **OAuth2**: Autenticación con Dropbox
- **httpx**: Cliente HTTP asíncrono para llamadas a la API de Dropbox

### Frontend
- **React 18**: Biblioteca de interfaz de usuario
- **TypeScript**: Tipado estático para JavaScript
- **Vite**: Build tool rápido y moderno
- **CSS Modules**: Estilos encapsulados por componente

## Estructura del proyecto

```
Dropbox_Chatbot/
├── backend/                      # API de FastAPI
│   ├── app/
│   │   ├── main.py              # Punto de entrada principal
│   │   ├── main_ursall.py       # Endpoints URSALL Legal
│   │   ├── auth.py              # Autenticación OAuth2
│   │   ├── validators.py        # Validadores de entrada
│   │   ├── questions_ursall.py  # Flujo de preguntas URSALL
│   │   ├── path_mapper_ursall.py # Mapeo de rutas legales
│   │   └── dropbox_uploader.py  # Subida a Dropbox
│   ├── requirements.txt         # Dependencias Python
│   └── .env.example            # Plantilla variables entorno
│
├── frontend/                    # Aplicación React + TypeScript
│   ├── src/
│   │   ├── components/         # Componentes React
│   │   ├── contexts/           # Contextos (Auth, User)
│   │   └── App.tsx             # Componente principal
│   ├── ssl/                    # Certificados SSL
│   │   ├── cert.pem           # Certificado SSL
│   │   └── key.pem            # Clave privada
│   ├── vite.config.ts         # Configuración Vite (HTTPS)
│   ├── .env.development       # Variables desarrollo
│   ├── .env.production        # Variables producción
│   └── package.json           # Dependencias Node.js
│
├── docs/                       # 📚 Documentación
│   ├── HTTPS_SETUP.md         # Configuración HTTPS
│   ├── PRODUCTION_DEPLOYMENT.md # Despliegue producción
│   ├── CONFIGURACION_COMPLETADA.md # Resumen cambios
│   ├── RESUMEN_CONFIGURACION.txt # Resumen ejecutivo
│   └── ...                    # Otras guías
│
├── scripts/                    # 🚀 Scripts de inicio
│   ├── start-dev.bat          # Windows desarrollo
│   ├── start-dev.sh           # Linux/Mac desarrollo
│   ├── start-prod.bat         # Windows producción
│   └── start-prod.sh          # Linux/Mac producción
│
├── QUICK_START.md             # Inicio rápido (3 pasos)
└── README.md                  # Este archivo
```

## Requisitos previos

- **Python 3.8+**
- **Node.js 16+** y **npm**
- **Cuenta de Dropbox** con una aplicación creada en [Dropbox App Console](https://www.dropbox.com/developers/apps)

## 🚀 Inicio Rápido

> 📖 **Guía completa de 3 pasos:** Ver [QUICK_START.md](./QUICK_START.md)

### Opción 1: Scripts Automáticos (Windows)

**1. Configurar hosts file** (Una sola vez):
```
Añade a C:\Windows\System32\drivers\etc\hosts:
127.0.0.1 dropboxaiorganizer.com
```

**2. Iniciar aplicación:**
```cmd
# Desarrollo (puerto 5173)
scripts\start-dev.bat

# Producción-like (puerto 443, requiere Administrador)
scripts\start-prod.bat  # Clic derecho → Ejecutar como Administrador
```

### Opción 2: Instalación Manual

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd Dropbox_Chatbot
```

### 2. Configurar credenciales de Dropbox

Crear `backend/.env` con tus credenciales:

```bash
DROPBOX_APP_KEY=tu_app_key
DROPBOX_APP_SECRET=tu_app_secret
GEMINI_API_KEY=tu_gemini_key
FRONTEND_URL=https://dropboxaiorganizer.com
```

**Configurar OAuth Redirect URI en Dropbox:**
- Para desarrollo: `http://localhost:8000/auth/dropbox/callback`
- Para producción: `https://dropboxaiorganizer.com/auth/dropbox/callback`

### 3. Configurar y ejecutar el backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El backend estará disponible en `http://localhost:8000`

### 4. Configurar y ejecutar el frontend

```bash
cd frontend
npm install

# Desarrollo
npm run dev

# Producción (puerto 443)
npm run dev -- --mode production  # Requiere sudo en Linux/Mac
```

**Acceso:**
- Desarrollo: `https://dropboxaiorganizer.com:5173`
- Producción: `https://dropboxaiorganizer.com` (¡sin puerto!)

## Uso

1. **Inicia sesión con Dropbox**: Haz clic en "Iniciar sesión con Dropbox"
2. **Sube un archivo**: Arrastra y suelta o selecciona un archivo
3. **Responde las preguntas**: El chatbot te guiará para clasificar el archivo
   - Tipo de documento (factura, contrato, presupuesto, etc.)
   - Nombre del cliente
   - Fecha del documento
4. **Revisa y confirma**: Verifica el nombre sugerido y la ruta
5. **Sube a Dropbox**: El archivo se organizará automáticamente en la carpeta correspondiente

## Características avanzadas

### Sistema de caché
- Los datos del usuario se cachean durante 5 minutos
- Carga instantánea desde localStorage
- Actualización automática cuando expira el caché

### Sistema de notificaciones mejorado
- **Notificaciones persistentes**: No desaparecen automáticamente, requieren acción del usuario
- **Gestión inteligente**: Click fuera del panel para cerrar con animación suave
- **Animaciones fluidas**: Transiciones de entrada y salida con CSS animations
- **Estados optimizados**: Prevención de múltiples activaciones durante animaciones

### Experiencia de usuario (UX/UI)
- **Paneles interactivos**: UserInfo y Notificaciones con comportamiento consistente
- **Animaciones sincronizadas**: Misma duración y curva de easing en todos los componentes
- **Click-outside functionality**: Cierre intuitivo al hacer clic fuera de los paneles
- **Estados de carga**: Indicadores visuales durante operaciones asíncronas

### Validación inteligente
- Sugerencias automáticas para tipos de documento comunes
- Corrección de formatos de fecha
- Validación de nombres de cliente

### Gestión de sesión
- Persistencia de sesión en archivo local
- Tokens de acceso seguros
- Cierre de sesión con limpieza de caché

## API Endpoints principales

### Autenticación
- `GET /auth/dropbox/login` - Inicia el flujo OAuth2
- `GET /auth/dropbox/callback` - Callback de OAuth2
- `GET /auth/status` - Estado de autenticación
- `POST /auth/logout` - Cerrar sesión

### Información de usuario
- `GET /api/user/info` - Información de la cuenta de Dropbox

### Gestión de archivos
- `POST /api/upload-temp` - Subir archivo temporal
- `POST /api/questions/start` - Iniciar flujo de preguntas
- `POST /api/questions/answer` - Responder pregunta
- `POST /api/questions/generate-name` - Generar nombre sugerido
- `POST /api/upload-final` - Subir archivo a Dropbox

## 📚 Documentación detallada

### 🚀 Inicio y Configuración
- **[QUICK_START.md](./QUICK_START.md)** - Inicio rápido en 3 pasos
- **[docs/RESUMEN_CONFIGURACION.txt](./docs/RESUMEN_CONFIGURACION.txt)** - Resumen ejecutivo completo

### ⚙️ Configuración y Despliegue
- **[docs/HTTPS_SETUP.md](./docs/HTTPS_SETUP.md)** - Configuración HTTPS para desarrollo local
- **[docs/PRODUCTION_DEPLOYMENT.md](./docs/PRODUCTION_DEPLOYMENT.md)** - Guía completa de despliegue en producción
- **[docs/CONFIGURACION_COMPLETADA.md](./docs/CONFIGURACION_COMPLETADA.md)** - Resumen de cambios implementados

### 📖 Documentación técnica
- [Documentación del Backend](./backend/README.md)
- [Documentación del Frontend](./frontend/README.md)
- [docs/URSALL_IMPLEMENTATION.md](./docs/URSALL_IMPLEMENTATION.md) - Sistema URSALL Legal
- [docs/URSALL_USAGE.md](./docs/URSALL_USAGE.md) - Uso del sistema URSALL

## 🔒 Seguridad y Certificados SSL

La aplicación está configurada para funcionar con HTTPS usando:
- **Puerto 443** (estándar HTTPS, sin puerto visible en URL)
- **Certificados SSL/TLS** (incluye certificados auto-firmados para desarrollo)
- **Configuración CORS** correcta para comunicación segura frontend-backend

### Para desarrollo local:
1. Certificados auto-firmados ya generados en `frontend/ssl/`
2. Configurar hosts file: `127.0.0.1 dropboxaiorganizer.com`
3. Confiar en el certificado en el navegador (ver [docs/HTTPS_SETUP.md](./docs/HTTPS_SETUP.md))

### Para producción:
1. Obtener certificado SSL válido (Let's Encrypt recomendado)
2. Configurar DNS para apuntar al servidor
3. Actualizar OAuth redirect URIs en Dropbox
4. Ver guía completa en [docs/PRODUCTION_DEPLOYMENT.md](./docs/PRODUCTION_DEPLOYMENT.md)

## Contribución

Las contribuciones son bienvenidas. Por favor:
1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT.

## Contacto

Para preguntas o sugerencias, por favor abre un issue en el repositorio.

## Estado del proyecto

✅ Funcional y en desarrollo activo
