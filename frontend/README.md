# Frontend - Dropbox Chatbot Organizer

Aplicación web React moderna con TypeScript para interactuar con el asistente de organización de archivos de Dropbox.

## Tecnologías

- **React 18**: Biblioteca de interfaz de usuario
- **TypeScript**: Tipado estático para JavaScript
- **Vite**: Build tool rápido con HMR
- **CSS3**: Estilos personalizados con variables CSS
- **Fetch API**: Cliente HTTP nativo del navegador

## Estructura del proyecto

```
frontend/
├── src/
│   ├── components/          # Componentes de React
│   │   ├── ChatMessage.tsx  # Mensajes del chat
│   │   ├── UserInfo.tsx     # Panel de información del usuario
│   │   └── *.css           # Estilos de componentes
│   ├── contexts/           # Contextos de React
│   │   └── UserContext.tsx # Contexto de usuario
│   ├── App.tsx             # Componente principal
│   ├── App.css             # Estilos globales
│   └── main.tsx            # Punto de entrada
├── index.html              # HTML base
├── package.json            # Dependencias y scripts
├── tsconfig.json           # Configuración de TypeScript
├── vite.config.ts          # Configuración de Vite
└── README.md              # Este archivo
```

## Requisitos previos

- **Node.js 16+**
- **npm 7+** o **pnpm**

## Instalación

### 1. Instalar dependencias

```bash
cd frontend
npm install
```

### 2. Configurar variables de entorno (opcional)

Si necesitas cambiar la URL del backend, edita el archivo relevante o crea un `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Scripts disponibles

### Desarrollo

```bash
npm run dev
```

Inicia el servidor de desarrollo con HMR en `http://localhost:5173`

### Build para producción

```bash
npm run build
```

Compila el proyecto en la carpeta `dist/`

### Preview de producción

```bash
npm run preview
```

Previsualiza la build de producción localmente

### Lint

```bash
npm run lint
```

Ejecuta ESLint para verificar el código

## Componentes principales

### `App.tsx`
Componente raíz de la aplicación:
- Gestiona el estado global de autenticación
- Renderiza la pantalla de login o el chat
- Maneja el flujo de conversación con el chatbot

### `components/ChatMessage.tsx`
Renderiza mensajes individuales del chat:
- Mensajes del usuario
- Mensajes del chatbot
- Indicador de escritura
- Formato de código y texto enriquecido

### `components/UserInfo.tsx`
Panel de información del usuario:
- Datos de la cuenta de Dropbox
- Espacio utilizado y disponible
- Foto de perfil
- Botón de cerrar sesión
- **Sistema de caché inteligente (5 minutos)**

**Características del caché:**
- Almacenamiento en `localStorage`
- Carga instantánea desde caché
- Actualización automática al abrir el panel
- Limpieza automática al cerrar sesión

### `contexts/UserContext.tsx`
Contexto de React para compartir información del usuario:
- Estado de autenticación
- Datos del usuario
- Funciones de login/logout

## Características principales

### Sistema de caché

El componente `UserInfo` implementa un sistema de caché inteligente:

```typescript
// Duración del caché: 5 minutos
const CACHE_DURATION = 5 * 60 * 1000

// Al abrir el panel:
// 1. Verifica si hay datos en caché
// 2. Si son válidos (< 5 min), los muestra instantáneamente
// 3. Si no, hace petición al backend
// 4. Guarda los nuevos datos en caché
```

### Gestión de estado

La aplicación usa React Hooks para la gestión de estado:
- `useState`: Estado local de componentes
- `useEffect`: Efectos secundarios y lifecycle
- `useContext`: Estado compartido entre componentes

### Flujo de autenticación

1. Usuario hace clic en "Iniciar sesión con Dropbox"
2. Redirige a `http://localhost:8000/auth/dropbox/login`
3. Dropbox autentica al usuario
4. Callback regresa al frontend
5. Frontend verifica el estado de autenticación
6. Muestra la interfaz del chat

### Flujo de subida de archivos

1. **Subir archivo**: Drag & drop o selección manual
2. **Pregunta 1 - Tipo de documento**: factura, contrato, etc.
3. **Pregunta 2 - Cliente**: Nombre del cliente
4. **Pregunta 3 - Fecha**: Fecha del documento
5. **Confirmación**: Muestra nombre sugerido y ruta
6. **Subida**: Envía el archivo a Dropbox

## Estilos

### Variables CSS

El proyecto usa variables CSS para mantener consistencia:

```css
:root {
  /* Espaciado */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.5rem;
  --space-6: 2rem;
  --space-8: 3rem;

  /* Colores */
  --text-primary: #ffffff;
  --text-secondary: #b0b0b0;
  --text-tertiary: #808080;
  --text-inverse: #1a1a1a;
  --accent-primary: #4fc3f7;

  /* Radios */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --radius-full: 9999px;
}
```

### Diseño responsivo

La interfaz se adapta a diferentes tamaños de pantalla:

```css
@media (max-width: 768px) {
  .user-info__panel {
    right: var(--space-4);
    left: var(--space-4);
    width: auto;
  }
}
```

## Integración con el backend

### Base URL

```typescript
const API_BASE_URL = 'http://localhost:8000'
```

### Endpoints utilizados

#### Autenticación
- `GET /auth/status` - Verificar autenticación
- `POST /auth/logout` - Cerrar sesión
- `GET /auth/dropbox/login` - Iniciar login (redirect)

#### Información de usuario
- `GET /api/user/info` - Obtener datos del usuario

#### Subida de archivos
- `POST /api/upload-temp` - Subir archivo temporal
- `POST /api/questions/start` - Iniciar flujo de preguntas
- `POST /api/questions/answer` - Responder pregunta
- `POST /api/questions/generate-name` - Generar nombre sugerido
- `POST /api/upload-final` - Subir a Dropbox

### Manejo de errores

```typescript
try {
  const response = await fetch(url, options)

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }

  const data = await response.json()
  return data
} catch (error) {
  console.error('Error:', error)
  // Mostrar mensaje de error al usuario
}
```

## Desarrollo

### Hot Module Replacement (HMR)

Vite proporciona HMR automático. Los cambios se reflejan instantáneamente sin recargar la página.

### TypeScript

El proyecto usa TypeScript estricto:

```json
{
  "compilerOptions": {
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

### Agregar nuevos componentes

1. Crear archivo `.tsx` en `src/components/`
2. Crear archivo `.css` correspondiente
3. Exportar el componente
4. Importar donde sea necesario

Ejemplo:

```typescript
// src/components/NewComponent.tsx
import React from 'react'
import './NewComponent.css'

interface NewComponentProps {
  title: string
}

export function NewComponent({ title }: NewComponentProps) {
  return (
    <div className="new-component">
      <h2>{title}</h2>
    </div>
  )
}
```

## Build para producción

### Optimizaciones automáticas

Vite optimiza automáticamente:
- Tree shaking
- Code splitting
- Minificación
- Asset optimization

### Despliegue

La carpeta `dist/` contiene archivos estáticos listos para desplegar:

```bash
npm run build
```

Opciones de despliegue:
- **Vercel**: `vercel deploy`
- **Netlify**: Arrastra la carpeta `dist/`
- **Servidor estático**: Copia `dist/` al servidor

### Variables de entorno

Para producción, actualiza la URL del backend:

```env
VITE_API_BASE_URL=https://api.tu-dominio.com
```

## Mejores prácticas

### Componentes

- Un componente por archivo
- Props con TypeScript interfaces
- Nombres descriptivos en PascalCase
- CSS modules para estilos encapsulados

### Estado

- Estado local cuando sea posible
- Context para estado global
- Evitar prop drilling excesivo

### Performance

- Lazy loading para rutas
- Memoización con `useMemo` y `useCallback`
- Virtualización para listas largas

### Accesibilidad

- Atributos ARIA donde sea necesario
- Navegación por teclado
- Contraste de colores adecuado
- Textos alternativos para imágenes

## Solución de problemas

### Error: "Failed to fetch"
- Verifica que el backend esté corriendo
- Comprueba la URL del backend
- Revisa CORS en el backend

### Error: "Module not found"
- Ejecuta `npm install`
- Verifica la ruta de importación
- Reinicia el servidor de desarrollo

### Estilos no se aplican
- Verifica el import del CSS
- Comprueba la jerarquía de clases
- Inspecciona con DevTools del navegador

### TypeScript errors
- Ejecuta `npm run build` para ver todos los errores
- Verifica las interfaces y tipos
- Consulta la documentación de TypeScript

## Testing

### Configurar tests (ejemplo con Vitest)

```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom
```

```typescript
// ejemplo.test.tsx
import { render, screen } from '@testing-library/react'
import { ChatMessage } from './ChatMessage'

test('renders message', () => {
  render(<ChatMessage text="Hello" sender="user" />)
  expect(screen.getByText('Hello')).toBeInTheDocument()
})
```

## Recursos

- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/)
- [Vite Documentation](https://vitejs.dev/)
- [CSS Variables](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)

## Contribución

Para contribuir al frontend:
1. Crea una rama para tu feature
2. Mantén el código limpio y tipado
3. Sigue las convenciones de nomenclatura
4. Documenta cambios significativos
5. Actualiza este README si es necesario

## Licencia

Este proyecto frontend es parte del proyecto Dropbox Chatbot Organizer y está bajo la misma licencia MIT.
