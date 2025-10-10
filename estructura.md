# Estructura y Funcionalidades - Dropbox AI Organizer URSALL

## Descripción General

El **Dropbox AI Organizer URSALL** es una aplicación web avanzada diseñada específicamente para la organización inteligente de documentos legales siguiendo la estructura organizacional de URSALL Legal. La aplicación combina inteligencia artificial, procesamiento de lenguaje natural (NLP) y una interfaz conversacional para automatizar completamente el proceso de clasificación y almacenamiento de documentos jurídicos en Dropbox.

## Arquitectura del Sistema

### Backend (FastAPI + Python)
- **Framework**: FastAPI con Python 3.8+
- **Servidor**: Uvicorn con soporte HTTPS
- **Base de datos**: Sistema en memoria para sesiones (escalable a PostgreSQL/MongoDB)
- **Autenticación**: OAuth2 con Dropbox
- **IA**: Google Gemini para análisis de documentos
- **NLP**: Procesamiento de lenguaje natural para extracción legal

### Frontend (React + TypeScript)
- **Framework**: React 18 con TypeScript
- **Build Tool**: Vite para desarrollo y producción
- **Styling**: CSS Modules con diseño responsive
- **Estado**: Context API para gestión de estado global
- **Comunicación**: Fetch API para llamadas REST

## Funcionalidades Principales

### 1. Sistema URSALL Legal Completo

#### Procedimientos Judiciales
- **Estructura automática**: Genera carpetas siguiendo el formato `AAAA_MM_Juzgado_Demarcación_NºProcedimiento/AAAA_ParteA Vs ParteB_Materia`
- **11 preguntas guiadas**: Flujo inteligente que extrae toda la información necesaria
- **Subcarpetas automáticas**: Crea 10 subcarpetas estándar (Escritos, Resoluciones, Pruebas, etc.)
- **Mapeo inteligente**: Clasifica automáticamente documentos en la subcarpeta correcta

#### Proyectos Jurídicos
- **Estructura automática**: Genera carpetas siguiendo el formato `AAAA_MM_Cliente_Proyecto_Materia`
- **7 preguntas guiadas**: Flujo optimizado para proyectos no judiciales
- **Subcarpetas automáticas**: Crea 8 subcarpetas estándar (General, Borradores, Informes, etc.)
- **Clasificación automática**: Organiza documentos según su tipo y propósito

### 2. Extracción Inteligente con NLP

#### Procesamiento de Lenguaje Natural
- **Extracción de jurisdicciones**: Identifica automáticamente el tipo de juzgado (Social, Civil, Penal, etc.)
- **Reconocimiento de partes**: Extrae demandante y demandado de texto natural
- **Análisis de materias**: Identifica la materia legal del procedimiento
- **Formateo automático**: Convierte texto libre a formatos estructurados

#### Ejemplos de Extracción
```
Entrada: "Juzgado Social número 2 de Tenerife"
Salida: jurisdiccion="SC", numero="2", demarcacion="Tenerife"

Entrada: "Pedro Pérez vs Cabildo Gomera"
Salida: parte_a="Pedro Pérez", parte_b="Cabildo Gomera"

Entrada: "Artículo 316 CP"
Salida: materia="Art316CP"
```

### 3. Validación y Seguridad

#### Validaciones de Archivos
- **Tipos permitidos**: PDF, DOC, DOCX, TXT, JPG, PNG
- **Tamaño máximo**: 50MB por archivo
- **Validación de contenido**: Verificación de headers de archivo
- **Sanitización**: Limpieza automática de nombres de archivo

#### Seguridad
- **OAuth2**: Autenticación segura con Dropbox
- **HTTPS**: Comunicación encriptada
- **CORS**: Configuración segura para múltiples dominios
- **Validación de entrada**: Sanitización de todos los inputs del usuario

### 4. APIs y Endpoints

#### Endpoints Principales
```
POST /api/upload-temp          # Subida temporal de archivos
POST /api/questions/start      # Inicio del flujo de preguntas
POST /api/questions/answer     # Procesamiento de respuestas
POST /api/questions/generate-path  # Generación de rutas
POST /api/upload-final         # Subida final a Dropbox
GET  /api/user/info           # Información del usuario
GET  /auth/dropbox/login      # Inicio de autenticación
GET  /auth/status             # Estado de autenticación
```

#### Flujo de API
1. **Upload temporal**: El archivo se sube temporalmente al servidor
2. **Inicio de preguntas**: Se inicia el flujo URSALL específico
3. **Procesamiento de respuestas**: Cada respuesta se procesa con NLP
4. **Generación de ruta**: Se calcula la ruta final en Dropbox
5. **Creación de estructura**: Se crean todas las carpetas necesarias
6. **Upload final**: El archivo se mueve a su ubicación definitiva

## Estructura Visual Detallada

### 1. Pantalla Principal (AppShell)

#### Layout General
- **Header fijo**: Barra superior con información del usuario y notificaciones
- **Área principal**: Zona central para el contenido dinámico
- **Sidebar responsive**: Panel lateral que se adapta a diferentes tamaños de pantalla
- **Footer informativo**: Información de estado y versión

#### Componentes Visuales
```typescript
// Estructura del AppShell
<div className="app-shell">
  <ChatHeader />           // Header con usuario y notificaciones
  <main className="main-content">
    <FileUploadWidget />   // Widget de subida de archivos
    <MessageViewport />    // Área de mensajes y chat
    <QuestionFlow />       // Flujo de preguntas URSALL
  </main>
  <NotificationContainer /> // Sistema de notificaciones
</div>
```

### 2. Header de Chat (ChatHeader)

#### Elementos Visuales
- **Logo y título**: Branding de la aplicación
- **Información del usuario**: Avatar, nombre y estado de conexión
- **Indicadores de estado**: Estado de Dropbox, conexión, etc.
- **Botones de acción**: Logout, configuración, ayuda

#### Diseño Responsive
- **Desktop**: Header completo con todos los elementos
- **Tablet**: Elementos condensados con iconos
- **Mobile**: Header minimalista con menú hamburguesa

### 3. Widget de Subida de Archivos (FileUploadWidget)

#### Zona de Drag & Drop
```css
.upload-zone {
  border: 2px dashed #007bff;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  transition: all 0.3s ease;
}

.upload-zone.dragover {
  border-color: #28a745;
  background-color: #f8f9fa;
}
```

#### Estados Visuales
- **Estado inicial**: Zona de arrastre con instrucciones
- **Hover**: Cambio de color y animación sutil
- **Drag over**: Resaltado verde indicando zona válida
- **Uploading**: Barra de progreso animada
- **Success**: Checkmark verde con animación
- **Error**: Indicador rojo con mensaje de error

#### Validación Visual
- **Archivos válidos**: Borde verde y icono de éxito
- **Archivos inválidos**: Borde rojo y mensaje de error
- **Tamaño excedido**: Advertencia naranja con detalles

### 4. Flujo de Preguntas (QuestionFlow)

#### Diseño de Conversación
```typescript
interface QuestionBubble {
  type: 'question' | 'answer' | 'system';
  content: string;
  timestamp: Date;
  status: 'sending' | 'sent' | 'error';
}
```

#### Elementos Visuales
- **Burbujas de pregunta**: Fondo azul, alineadas a la izquierda
- **Burbujas de respuesta**: Fondo gris, alineadas a la derecha
- **Mensajes del sistema**: Fondo amarillo claro, centrados
- **Indicador de escritura**: Animación de puntos cuando el sistema "piensa"

#### Ayuda Contextual
- **Tooltips**: Información adicional en hover
- **Ejemplos**: Texto de ayuda debajo de cada pregunta
- **Validación en tiempo real**: Feedback inmediato sobre la entrada

### 5. Vista de Mensajes (MessageViewport)

#### Scroll Automático
- **Auto-scroll**: Se desplaza automáticamente a nuevos mensajes
- **Scroll suave**: Animaciones fluidas entre mensajes
- **Indicador de nuevos mensajes**: Badge cuando hay mensajes no vistos

#### Tipos de Mensaje
```css
.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 18px;
  margin: 8px 0;
  word-wrap: break-word;
}

.message-question {
  background: #007bff;
  color: white;
  align-self: flex-start;
}

.message-answer {
  background: #e9ecef;
  color: #333;
  align-self: flex-end;
}
```

### 6. Previsualización de Archivos (FilePreviewCard)

#### Información del Archivo
- **Icono del tipo**: Iconos específicos para PDF, DOC, IMG, etc.
- **Nombre del archivo**: Truncado con tooltip completo
- **Tamaño**: Formato legible (KB, MB)
- **Fecha de subida**: Timestamp formateado
- **Estado**: Indicador visual del estado de procesamiento

#### Acciones Disponibles
- **Vista previa**: Modal con contenido del archivo (si es posible)
- **Descargar**: Descarga directa del archivo
- **Eliminar**: Confirmación antes de eliminar
- **Reemplazar**: Opción para subir nueva versión

### 7. Sistema de Notificaciones

#### Tipos de Notificación
```typescript
type NotificationType = 'success' | 'error' | 'warning' | 'info';

interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  duration: number;
  actions?: NotificationAction[];
}
```

#### Posicionamiento y Animaciones
- **Posición**: Esquina superior derecha
- **Entrada**: Slide-in desde la derecha
- **Salida**: Fade-out con slide hacia arriba
- **Stack**: Múltiples notificaciones se apilan verticalmente

#### Estilos por Tipo
- **Success**: Verde con icono de checkmark
- **Error**: Rojo con icono de X
- **Warning**: Naranja con icono de exclamación
- **Info**: Azul con icono de información

### 8. Pantalla de Login (LoginScreen)

#### Diseño Centrado
```css
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  max-width: 400px;
  width: 100%;
}
```

#### Elementos de la Pantalla
- **Logo principal**: Logo de URSALL centrado
- **Título**: "Dropbox AI Organizer URSALL"
- **Descripción**: Breve explicación del sistema
- **Botón de login**: Botón prominente para conectar con Dropbox
- **Información legal**: Enlaces a términos y privacidad

### 9. Indicadores de Estado

#### Indicador de Escritura (TypingIndicator)
```css
.typing-indicator {
  display: flex;
  align-items: center;
  padding: 8px 16px;
}

.typing-dots {
  display: flex;
  gap: 4px;
}

.typing-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #007bff;
  animation: typing 1.4s infinite ease-in-out;
}
```

#### Estados de Conexión
- **Conectado**: Indicador verde con "Conectado a Dropbox"
- **Desconectado**: Indicador rojo con "Sin conexión"
- **Sincronizando**: Indicador amarillo con spinner
- **Error**: Indicador rojo con mensaje de error específico

### 10. Responsive Design

#### Breakpoints
```css
/* Mobile First */
.container {
  padding: 16px;
}

/* Tablet */
@media (min-width: 768px) {
  .container {
    padding: 24px;
    max-width: 1200px;
    margin: 0 auto;
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .container {
    padding: 32px;
    display: grid;
    grid-template-columns: 300px 1fr;
    gap: 24px;
  }
}
```

#### Adaptaciones por Dispositivo
- **Mobile (< 768px)**: Layout vertical, menús colapsables
- **Tablet (768px - 1024px)**: Layout híbrido, elementos condensados
- **Desktop (> 1024px)**: Layout completo con sidebar

## Flujo de Usuario Completo

### 1. Autenticación
1. **Acceso inicial**: Usuario accede a la aplicación
2. **Pantalla de login**: Se muestra la pantalla de autenticación
3. **Conexión Dropbox**: Usuario hace clic en "Conectar con Dropbox"
4. **OAuth2**: Redirección a Dropbox para autorización
5. **Callback**: Retorno a la aplicación con token de acceso
6. **Dashboard**: Acceso a la funcionalidad principal

### 2. Subida de Archivo
1. **Drag & Drop**: Usuario arrastra archivo a la zona de subida
2. **Validación**: Sistema valida tipo, tamaño y contenido
3. **Upload temporal**: Archivo se sube al servidor temporalmente
4. **Confirmación**: Previsualización del archivo subido

### 3. Flujo URSALL
1. **Inicio**: Sistema inicia flujo de preguntas URSALL
2. **Tipo de trabajo**: ¿Procedimiento judicial o proyecto jurídico?
3. **Preguntas específicas**: 11 preguntas para procedimientos, 7 para proyectos
4. **Extracción NLP**: Procesamiento inteligente de cada respuesta
5. **Validación**: Verificación de datos extraídos
6. **Generación de ruta**: Cálculo de la estructura de carpetas

### 4. Organización Final
1. **Creación de estructura**: Todas las carpetas se crean en Dropbox
2. **Clasificación**: Archivo se coloca en la subcarpeta correcta
3. **Confirmación**: Notificación de éxito con enlace a Dropbox
4. **Limpieza**: Archivos temporales se eliminan del servidor

## Tecnologías Utilizadas

### Backend
- **FastAPI**: Framework web moderno y rápido
- **Pydantic**: Validación de datos y serialización
- **Uvicorn**: Servidor ASGI de alto rendimiento
- **httpx**: Cliente HTTP asíncrono
- **python-multipart**: Manejo de uploads de archivos
- **Google Gemini**: IA para análisis de documentos

### Frontend
- **React 18**: Biblioteca de UI con hooks modernos
- **TypeScript**: Tipado estático para JavaScript
- **Vite**: Build tool rápido y moderno
- **CSS Modules**: Estilos encapsulados por componente
- **Fetch API**: Comunicación con el backend

### Infraestructura
- **Dropbox API**: Almacenamiento y organización de archivos
- **OAuth2**: Autenticación segura
- **HTTPS**: Comunicación encriptada
- **SSL/TLS**: Certificados de seguridad

## Beneficios del Sistema

### Para Abogados
- **Automatización completa**: Sin intervención manual en la organización
- **Estructura consistente**: Todos los casos siguen el mismo formato
- **Búsqueda eficiente**: Estructura predecible facilita encontrar documentos
- **Ahorro de tiempo**: Eliminación de tareas repetitivas de organización

### Para el Despacho
- **Estandarización**: Todos los abogados usan la misma estructura
- **Escalabilidad**: Maneja cientos de casos simultáneamente
- **Trazabilidad**: Registro completo de todas las acciones
- **Integración**: Se conecta directamente con Dropbox existente

### Técnicos
- **Inteligencia artificial**: NLP extrae información automáticamente
- **Validación robusta**: Múltiples capas de validación de datos
- **Arquitectura moderna**: Tecnologías actuales y mantenibles
- **Seguridad**: Cumple con estándares de seguridad legal

## Configuración y Despliegue

### Requisitos del Sistema
- **Python 3.8+**: Para el backend
- **Node.js 16+**: Para el frontend
- **Dropbox App**: Configurada con permisos de escritura
- **Certificados SSL**: Para HTTPS en producción

### Variables de Entorno
```bash
# Backend
DROPBOX_APP_KEY=your_app_key
DROPBOX_APP_SECRET=your_app_secret
DROPBOX_REDIRECT_URI=https://your-domain.com/auth/dropbox/callback
GEMINI_API_KEY=your_gemini_key

# Frontend
VITE_API_BASE_URL=https://your-api-domain.com
VITE_DROPBOX_APP_KEY=your_app_key
```

### Comandos de Despliegue
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --ssl-keyfile=key.pem --ssl-certfile=cert.pem

# Frontend
cd frontend
npm install
npm run build
npm run preview
```

## Soporte y Mantenimiento

### Logs y Monitoreo
- **Logging estructurado**: Todos los eventos se registran
- **Health checks**: Endpoints de salud para monitoreo
- **Error tracking**: Captura y reporte de errores
- **Performance metrics**: Métricas de rendimiento

### Actualizaciones
- **Versionado semántico**: Control de versiones claro
- **Migraciones**: Scripts para actualizar estructuras
- **Rollback**: Capacidad de revertir cambios
- **Testing**: Suite completa de pruebas automatizadas

---

*Este documento describe la estructura completa del Dropbox AI Organizer URSALL, incluyendo todas sus funcionalidades, aspectos visuales y técnicos. Para más información técnica, consulte la documentación en `/docs/`.*