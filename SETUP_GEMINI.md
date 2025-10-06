# Configuración de Gemini API (GRATIS)

Este proyecto ahora utiliza Google Gemini API para extraer información de manera inteligente de las respuestas del usuario.

## ✅ Ventajas

- **100% GRATIS** - Sin tarjeta de crédito requerida
- **15 consultas por minuto** - Suficiente para uso normal
- **Más preciso** que regex - Entiende contexto y lenguaje natural
- **Fallback automático** - Si no está configurado, usa regex

## 📋 Pasos para configurar

### 1. Obtener tu API Key (GRATIS)

1. Ve a [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Inicia sesión con tu cuenta de Google
3. Haz clic en **"Create API Key"**
4. Copia la clave que te dan

### 2. Configurar el proyecto

1. Ve a la carpeta `backend/`
2. Copia el archivo `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```

3. Abre el archivo `.env` y pega tu API key:
   ```
   GEMINI_API_KEY=tu_api_key_aqui
   ```

### 3. Instalar dependencias

```bash
cd backend
pip install -r requirements.txt
```

### 4. Verificar que funciona

Inicia el servidor:
```bash
uvicorn app.main:app --reload
```

Visita: http://localhost:8000/health

Deberías ver:
```json
{
  "status": "ok",
  "ai": {
    "gemini_available": true,
    "api_key_configured": true,
    "fallback": null
  }
}
```

## 🎯 Cómo funciona

El sistema ahora extrae información inteligentemente:

### Antes (regex):
- Usuario: "El nombre del cliente es Juan Pérez"
- Sistema: ❌ "El nombre del cliente es Juan Pérez" (literal)

### Ahora (Gemini AI):
- Usuario: "El nombre del cliente es Juan Pérez"
- Sistema: ✅ "Juan Pérez" (extraído)

### Ejemplos:

**Cliente:**
- "El cliente es Acme Corp" → `"Acme Corp"`
- "se llama Microsoft España S.L." → `"Microsoft España S.L."`

**Tipo de documento:**
- "Es una factura" → `"factura"`
- "son presupuestos" → `"presupuestos"`

**Fecha:**
- "La fecha es 15/01/2025" → `"2025-01-15"`
- "15-01-2025" → `"2025-01-15"`

## ⚠️ API Key REQUERIDA

**IMPORTANTE**: La API key de Gemini es **OBLIGATORIA** para que la aplicación funcione. Sin ella, la extracción de información fallará.

El sistema ya no usa fallback a regex - requiere Gemini AI para funcionar correctamente.

## 🔒 Seguridad

- **NUNCA** compartas tu API key
- El archivo `.env` está en `.gitignore` (no se sube a GitHub)
- Solo usa `.env.example` como plantilla

## 📊 Límites del tier gratuito

- **15 consultas/minuto**
- **1500 consultas/día**
- **1 millón de tokens/mes**

Para este proyecto, es más que suficiente.

## 🐛 Troubleshooting

### "Gemini API not available"
- Verifica que tu API key esté en el archivo `.env`
- Verifica que el archivo `.env` esté en `backend/`
- Reinicia el servidor

### "Rate limit exceeded"
- Espera 1 minuto (límite de 15 consultas/minuto)
- El sistema automáticamente usa fallback (regex)

## 📚 Más información

- [Google AI Studio](https://aistudio.google.com/)
- [Documentación Gemini API](https://ai.google.dev/docs)
