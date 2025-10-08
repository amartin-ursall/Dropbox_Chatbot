# 🚀 Quick Start - Dropbox AI Organizer

## ⚡ Inicio Rápido (3 pasos)

### 1️⃣ Configurar Hosts (Una sola vez)

**Windows:**
```
1. Abrir Notepad como Administrador
2. Abrir: C:\Windows\System32\drivers\etc\hosts
3. Añadir línea: 127.0.0.1 dropboxaiorganizer.com
4. Guardar
```

**Linux/Mac:**
```bash
sudo nano /etc/hosts
# Añadir: 127.0.0.1 dropboxaiorganizer.com
```

### 2️⃣ Configurar Credenciales

Crear `backend/.env`:
```bash
DROPBOX_APP_KEY=tu_app_key
DROPBOX_APP_SECRET=tu_app_secret
GEMINI_API_KEY=tu_gemini_key
FRONTEND_URL=https://dropboxaiorganizer.com
```

### 3️⃣ Iniciar Aplicación

**Windows:**
```cmd
# Desarrollo (puerto 5173)
scripts\start-dev.bat

# Producción (puerto 443 - Ejecutar como Administrador)
scripts\start-prod.bat
```

**Linux/Mac:**
```bash
# Desarrollo
./scripts/start-dev.sh

# Producción (requiere sudo)
sudo ./scripts/start-prod.sh
```

## 🌐 Acceso

### Modo Desarrollo
- **Frontend:** https://dropboxaiorganizer.com:5173
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Modo Producción
- **Frontend:** https://dropboxaiorganizer.com ← ¡SIN PUERTO!
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## ⚠️ Primera vez: Advertencia de certificado

El navegador mostrará una advertencia porque el certificado es auto-firmado (solo desarrollo).

**Cómo proceder:**
- Chrome/Edge: "Avanzado" → "Continuar a dropboxaiorganizer.com"
- Firefox: "Avanzado" → "Aceptar el riesgo y continuar"

## 📚 Más información

- **Resumen ejecutivo:** [docs/RESUMEN_CONFIGURACION.txt](./docs/RESUMEN_CONFIGURACION.txt)
- **Configuración completa:** [docs/CONFIGURACION_COMPLETADA.md](./docs/CONFIGURACION_COMPLETADA.md)
- **Setup HTTPS:** [docs/HTTPS_SETUP.md](./docs/HTTPS_SETUP.md)
- **Despliegue producción:** [docs/PRODUCTION_DEPLOYMENT.md](./docs/PRODUCTION_DEPLOYMENT.md)

---

✅ **¡Listo para usar!**
