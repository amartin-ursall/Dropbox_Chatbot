# 🚀 Deployment en Windows Server con IIS y HTTPS

Esta carpeta contiene todos los scripts y configuraciones necesarios para desplegar la aplicación **Dropbox AI Organizer (URSALL)** en producción con Windows Server, IIS y certificados SSL.

---

## 📁 Archivos en esta carpeta

| Archivo | Descripción |
|---------|-------------|
| `install-iis-components.ps1` | Instala IIS, URL Rewrite Module y ARR |
| `install-backend-service.ps1` | Instala el backend como servicio Windows con NSSM |
| `install-ssl-certificate.ps1` | Configura certificado SSL (Let's Encrypt o autofirmado) |
| `web.config` | Configuración de IIS para reverse proxy y SPA |
| `deploy.ps1` | Script completo de deployment automatizado |

---

## 🎯 Deployment Rápido (Opción Recomendada)

Si es tu **primera instalación**, ejecuta los scripts en este orden:

### 1️⃣ Instalar componentes de IIS

```powershell
# Ejecutar como Administrador
cd deployment
.\install-iis-components.ps1
```

**Qué hace:**
- Instala IIS con todas las características necesarias
- Descarga e instala URL Rewrite Module
- Descarga e instala Application Request Routing (ARR)
- Habilita proxy en ARR
- Reinicia IIS

⏱️ **Tiempo estimado:** 10-15 minutos

---

### 2️⃣ Instalar backend como servicio

```powershell
# Ejecutar como Administrador
.\install-backend-service.ps1
```

**Qué hace:**
- Descarga e instala NSSM
- Crea estructura de carpetas en `C:\inetpub\wwwroot\dropbox-organizer`
- Copia archivos del backend
- Crea entorno virtual de Python
- Instala dependencias
- Configura backend como servicio Windows
- Inicia el servicio

⏱️ **Tiempo estimado:** 5-10 minutos

**⚠️ IMPORTANTE:** Después de este paso, debes editar el archivo `.env` con tus credenciales:

```powershell
notepad C:\inetpub\wwwroot\dropbox-organizer\backend\.env
```

Configura:
- `DROPBOX_APP_KEY`
- `DROPBOX_APP_SECRET`
- `DROPBOX_REDIRECT_URI` (con tu dominio HTTPS)
- `GEMINI_API_KEY`
- `FRONTEND_URL` (con tu dominio HTTPS)

Luego reinicia el servicio:

```powershell
Restart-Service DropboxBackend
```

---

### 3️⃣ Instalar certificado SSL

**Opción A: Let's Encrypt (PRODUCCIÓN - Recomendado)**

```powershell
# Ejecutar como Administrador
.\install-ssl-certificate.ps1 -Domain tudominio.com
```

**Opción B: Certificado Autofirmado (SOLO TESTING)**

```powershell
.\install-ssl-certificate.ps1 -Domain tudominio.com -SelfSigned
```

⚠️ **Nota:** Los certificados autofirmados NO funcionan para OAuth de Dropbox desde navegadores externos.

⏱️ **Tiempo estimado:** 5 minutos (Let's Encrypt), 2 minutos (autofirmado)

---

### 4️⃣ Deployment completo

```powershell
# Ejecutar como Administrador
.\deploy.ps1 -Domain tudominio.com
```

**Qué hace:**
- Actualiza variables de entorno con tu dominio
- Compila el frontend para producción
- Copia todos los archivos a `C:\inetpub\wwwroot\dropbox-organizer`
- Configura permisos
- Reinicia servicios
- Verifica que todo funciona

⏱️ **Tiempo estimado:** 5-10 minutos

---

## 🔄 Actualización de la Aplicación

Para actualizar una instalación existente:

```powershell
# Ejecutar como Administrador
cd deployment
.\deploy.ps1 -Domain tudominio.com
```

Esto recompilará el frontend, copiará los nuevos archivos y reiniciará los servicios.

---

## 📋 Checklist de Deployment

Usa este checklist para verificar que todo está correctamente configurado:

### Previo al Deployment

- [ ] Windows Server 2016+ con acceso de administrador
- [ ] Python 3.8+ instalado
- [ ] Node.js 16+ instalado
- [ ] Dominio registrado (ej: `dropboxorganizer.com`)
- [ ] DNS configurado apuntando al servidor
- [ ] Firewall permite tráfico en puerto 443 (HTTPS)
- [ ] Credenciales de Dropbox App Console
- [ ] API Key de Google Gemini

### Instalación

- [ ] IIS instalado con URL Rewrite y ARR
- [ ] Backend instalado como servicio Windows
- [ ] Frontend compilado y copiado a IIS
- [ ] web.config configurado
- [ ] Certificado SSL instalado (Let's Encrypt recomendado)
- [ ] Variables de entorno configuradas en `.env`
- [ ] Redirect URI configurado en Dropbox App Console

### Verificación

- [ ] Backend responde: `http://localhost:8000/health`
- [ ] Frontend carga: `https://tudominio.com`
- [ ] API docs accesibles: `https://tudominio.com/docs`
- [ ] Certificado SSL válido (sin advertencias en navegador)
- [ ] OAuth de Dropbox funciona correctamente
- [ ] Logs del backend no muestran errores

---

## 🛠️ Comandos Útiles

### Gestión del servicio backend

```powershell
# Ver estado
Get-Service DropboxBackend

# Iniciar
Start-Service DropboxBackend

# Detener
Stop-Service DropboxBackend

# Reiniciar
Restart-Service DropboxBackend

# Ver logs en tiempo real
Get-Content "C:\inetpub\wwwroot\dropbox-organizer\logs\backend-stdout.log" -Wait -Tail 50
```

### Gestión de IIS

```powershell
# Reiniciar IIS
iisreset

# Ver sitios
Get-Website

# Ver estado del sitio
Get-Website -Name "DropboxOrganizer"

# Iniciar/Detener sitio
Start-Website -Name "DropboxOrganizer"
Stop-Website -Name "DropboxOrganizer"
```

### Verificación de configuración

```powershell
# Probar health check del backend
curl http://localhost:8000/health

# Probar frontend
curl https://tudominio.com

# Ver certificados SSL instalados
Get-ChildItem Cert:\LocalMachine\My

# Verificar DNS
nslookup tudominio.com

# Verificar puerto 443 abierto
Test-NetConnection -ComputerName tudominio.com -Port 443
```

---

## 🔐 Configuración de Dropbox App Console

1. Ve a https://www.dropbox.com/developers/apps
2. Selecciona tu app (o crea una nueva)
3. En la sección **OAuth 2** → **Redirect URIs**, agrega:
   ```
   https://tudominio.com/auth/dropbox/callback
   ```
4. Guarda los cambios
5. Copia el **App key** y **App secret** a tu archivo `.env`

---

## 🚨 Solución de Problemas

### Error: "502 Bad Gateway"

**Causa:** Backend no está corriendo o no responde

**Solución:**
```powershell
# Verificar servicio
Get-Service DropboxBackend

# Ver logs
Get-Content "C:\inetpub\wwwroot\dropbox-organizer\logs\backend-stderr.log" -Tail 50

# Reiniciar servicio
Restart-Service DropboxBackend
```

---

### Error: "OAuth de Dropbox no funciona"

**Causas posibles:**
1. `DROPBOX_REDIRECT_URI` no coincide con Dropbox App Console
2. Certificado SSL no válido o autofirmado
3. Dominio no resuelve correctamente

**Solución:**
```powershell
# 1. Verificar .env
notepad C:\inetpub\wwwroot\dropbox-organizer\backend\.env

# 2. Verificar dominio
nslookup tudominio.com

# 3. Verificar certificado
# Navegar a: https://www.ssllabs.com/ssltest/
# Analizar: tudominio.com
```

---

### Error: "403 Forbidden" en IIS

**Causa:** Permisos incorrectos

**Solución:**
```powershell
icacls "C:\inetpub\wwwroot\dropbox-organizer" /grant "IIS_IUSRS:(OI)(CI)RX" /T
iisreset
```

---

### Error: "Certificado no confiable"

**Causa:** Certificado autofirmado o no válido

**Solución:**
- Instalar certificado Let's Encrypt:
  ```powershell
  .\install-ssl-certificate.ps1 -Domain tudominio.com
  ```

---

## 📖 Documentación Adicional

- [Guía completa de IIS](../docs/IIS_PRODUCTION_SETUP.md)
- [Configuración OAuth de Dropbox](../docs/OAUTH_PRODUCTION_SETUP.md)
- [README del Backend](../backend/README.md)
- [README del Frontend](../frontend/README.md)

---

## 🆘 Soporte

Si encuentras problemas:

1. Revisa los logs del backend
2. Verifica que todos los servicios estén corriendo
3. Consulta la sección de "Solución de Problemas"
4. Revisa la documentación completa en `docs/IIS_PRODUCTION_SETUP.md`

---

## ✅ Resumen del Proceso

```
1. install-iis-components.ps1
   ↓
2. install-backend-service.ps1
   ↓
3. Editar .env con credenciales
   ↓
4. install-ssl-certificate.ps1
   ↓
5. deploy.ps1
   ↓
6. Configurar Dropbox App Console
   ↓
7. ✓ ¡Listo! Aplicación en producción
```

⏱️ **Tiempo total estimado:** 30-40 minutos

---

**¡Buena suerte con tu deployment!** 🚀
