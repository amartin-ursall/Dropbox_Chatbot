# Dropbox Chatbot Organizer

Aplicación web completa para organizar y subir archivos a Dropbox de forma inteligente mediante un asistente conversacional.

## Descripción

Este proyecto permite a los usuarios interactuar con un chatbot que les guía en el proceso de subir archivos a Dropbox de manera organizada, generando nombres de archivo descriptivos y sugiriendo rutas basadas en el tipo de documento.

## Características principales

- **Autenticación OAuth2 con Dropbox**: Inicio de sesión seguro usando OAuth2
- **Asistente conversacional**: Guía paso a paso para organizar archivos
- **Sugerencias inteligentes**: Nombres de archivo y rutas sugeridas automáticamente
- **Validación avanzada**: Validación de fechas, tipos de documento y clientes con sugerencias en caso de error
- **Información de usuario**: Panel de información con datos de la cuenta de Dropbox en tiempo real con caché inteligente
- **Sistema de notificaciones**: Notificaciones persistentes con gestión avanzada y animaciones
- **Interfaz moderna**: UI responsive con diseño oscuro y animaciones fluidas
- **Experiencia de usuario mejorada**: 
  - Notificaciones persistentes que no desaparecen automáticamente
  - Cierre con animación suave al hacer clic fuera de los componentes
  - Paneles de usuario e información con animaciones de entrada y salida
  - Gestión inteligente de estados de carga y error

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
App_Chatbot_Dropbox/
├── backend/                 # API de FastAPI
│   ├── app/
│   │   ├── main.py         # Punto de entrada de la aplicación
│   │   ├── auth.py         # Módulo de autenticación OAuth2
│   │   ├── validators.py   # Validadores de entrada
│   │   ├── questions.py    # Lógica de flujo de preguntas
│   │   ├── path_mapper.py  # Mapeo de rutas de Dropbox
│   │   └── dropbox_uploader.py  # Subida de archivos a Dropbox
│   ├── requirements.txt    # Dependencias de Python
│   └── README.md          # Documentación del backend
├── frontend/               # Aplicación React
│   ├── src/
│   │   ├── components/    # Componentes de React
│   │   ├── contexts/      # Contextos de React
│   │   └── App.tsx        # Componente principal
│   ├── package.json       # Dependencias de Node.js
│   └── README.md         # Documentación del frontend
└── README.md             # Este archivo
```

## Requisitos previos

- **Python 3.8+**
- **Node.js 16+** y **npm**
- **Cuenta de Dropbox** con una aplicación creada en [Dropbox App Console](https://www.dropbox.com/developers/apps)

## Instalación rápida

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd App_Chatbot_Dropbox
```

### 2. Configurar credenciales de Dropbox

Editar `backend/app/auth.py` con tus credenciales:

```python
DROPBOX_APP_KEY = "tu_app_key"
DROPBOX_APP_SECRET = "tu_app_secret"
DROPBOX_REDIRECT_URI = "http://localhost:8000/auth/dropbox/callback"
```

### 3. Configurar y ejecutar el backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

El backend estará disponible en `http://localhost:8000`

### 4. Configurar y ejecutar el frontend

```bash
cd frontend
npm install
npm run dev
```

El frontend estará disponible en `http://localhost:5173`

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

## Documentación detallada

Para información más detallada, consulta:
- [Documentación del Backend](./backend/README.md)
- [Documentación del Frontend](./frontend/README.md)

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
