# Guía de Despliegue en IIS con HTTPS - Windows Server

Esta guía te llevará paso a paso para desplegar la aplicación Dropbox AI Organizer (URSALL) en Windows Server usando IIS como reverse proxy con certificado SSL.

## 📋 Requisitos Previos

- Windows Server 2016 o superior
- Acceso de administrador al servidor
- Dominio configurado apuntando al servidor (ej: `dropboxorganizer.com`)
- Python 3.8+ instalado
- Node.js 16+ instalado (para compilar el frontend)

---

## 🎯 Arquitectura Final

```
Internet (HTTPS:443)
    ↓
IIS (Reverse Proxy en puerto 443)
    ├─→ Backend API: http://localhost:8000 (FastAPI/Uvicorn)
    └─→ Frontend: archivos estáticos desde C:\inetpub\wwwroot\dropbox-organizer\frontend
```

---

## 📦 PASO 1: Instalar Componentes de IIS

### 1.1. Instalar IIS con PowerShell (como Administrador)

```powershell
# Instalar IIS con características necesarias
Install-WindowsFeature -name Web-Server -IncludeManagementTools

# Instalar características adicionales
Install-WindowsFeature Web-WebSockets
Install-WindowsFeature Web-App-Dev
Install-WindowsFeature Web-Net-Ext45
Install-WindowsFeature Web-Asp-Net45
```

### 1.2. Instalar URL Rewrite Module

1. Descargar desde: https://www.iis.net/downloads/microsoft/url-rewrite
2. Ejecutar el instalador: `rewrite_amd64_en-US.msi`
3. Reiniciar IIS: `iisreset`

### 1.3. Instalar Application Request Routing (ARR)

1. Descargar desde: https://www.iis.net/downloads/microsoft/application-request-routing
2. Ejecutar el instalador: `ARRv3_setup_amd64_en-us.exe`
3. Reiniciar IIS: `iisreset`

### 1.4. Habilitar Proxy en ARR

1. Abrir IIS Manager
2. Seleccionar el servidor (nivel raíz)
3. Doble clic en "Application Request Routing Cache"
4. En el panel derecho → "Server Proxy Settings"
5. Marcar "Enable proxy" → Apply

---

## 📁 PASO 2: Preparar Archivos de la Aplicación

### 2.1. Crear estructura de directorios

```powershell
# Crear directorios
New-Item -ItemType Directory -Path "C:\inetpub\wwwroot\dropbox-organizer" -Force
New-Item -ItemType Directory -Path "C:\inetpub\wwwroot\dropbox-organizer\frontend" -Force
New-Item -ItemType Directory -Path "C:\inetpub\wwwroot\dropbox-organizer\backend" -Force
New-Item -ItemType Directory -Path "C:\inetpub\wwwroot\dropbox-organizer\logs" -Force
```

### 2.2. Copiar archivos del backend

```powershell
# Copiar todo el código del backend
Copy-Item "C:\Users\amartin\Documents\Aplicativos\Dropbox_Chatbot\backend\*" `
          -Destination "C:\inetpub\wwwroot\dropbox-organizer\backend\" `
          -Recurse -Force -Exclude "venv","__pycache__",".pytest_cache"
```

### 2.3. Compilar y copiar frontend

```powershell
# Navegar al directorio frontend
cd "C:\Users\amartin\Documents\Aplicativos\Dropbox_Chatbot\frontend"

# Instalar dependencias (si no están instaladas)
npm install

# Compilar para producción
npm run build

# Copiar archivos compilados
Copy-Item ".\dist\*" `
          -Destination "C:\inetpub\wwwroot\dropbox-organizer\frontend\" `
          -Recurse -Force
```

---

## 🔐 PASO 3: Configurar Certificado SSL

### Opción A: Let's Encrypt con win-acme (RECOMENDADO - Gratuito)

#### 3.1. Instalar win-acme

```powershell
# Descargar win-acme
cd C:\
Invoke-WebRequest -Uri "https://github.com/win-acme/win-acme/releases/latest/download/win-acme.v2.2.9.1701.x64.pluggable.zip" `
                  -OutFile "win-acme.zip"

# Extraer
Expand-Archive -Path "win-acme.zip" -DestinationPath "C:\win-acme" -Force

# Crear tarea programada para renovación automática
cd C:\win-acme
.\wacs.exe
```

#### 3.2. Solicitar certificado

1. Ejecutar: `.\wacs.exe` como Administrador
2. Seleccionar opción `N` (Create certificate - simple mode)
3. Ingresar dominio: `dropboxorganizer.com` (o tu dominio)
4. Seleccionar IIS como destino de instalación
5. El certificado se instalará automáticamente en IIS

**Resultado:** Certificado instalado en `C:\ProgramData\win-acme\` y configurado en IIS

#### 3.3. Verificar renovación automática

El instalador crea una tarea programada que renueva automáticamente cada 60 días.

```powershell
# Verificar tarea programada
Get-ScheduledTask -TaskName "win-acme*"
```

### Opción B: Certificado Autofirmado (Solo para Testing/Desarrollo)

⚠️ **IMPORTANTE:** Dropbox OAuth NO funcionará con certificados autofirmados desde navegadores externos.

```powershell
# Crear certificado autofirmado
$cert = New-SelfSignedCertificate `
    -DnsName "dropboxorganizer.com" `
    -CertStoreLocation "cert:\LocalMachine\My" `
    -KeyLength 2048 `
    -KeyAlgorithm RSA `
    -HashAlgorithm SHA256 `
    -KeyUsage DigitalSignature, KeyEncipherment `
    -NotAfter (Get-Date).AddYears(2)

# Ver thumbprint del certificado
$cert.Thumbprint
```

Luego vincular en IIS Manager → Site Bindings → Add → HTTPS (puerto 443) → Seleccionar certificado

### Opción C: Certificado Comercial

1. Comprar certificado de DigiCert, GoDaddy, etc.
2. Generar CSR en IIS
3. Instalar certificado recibido
4. Vincular en IIS Manager

---

## 🌐 PASO 4: Configurar Sitio en IIS

### 4.1. Crear nuevo sitio web

1. Abrir **IIS Manager**
2. Click derecho en **Sites** → **Add Website**
3. Configurar:
   - **Site name:** `DropboxOrganizer`
   - **Physical path:** `C:\inetpub\wwwroot\dropbox-organizer\frontend`
   - **Binding:**
     - Type: `http`
     - Port: `80`
     - Host name: `dropboxorganizer.com` (tu dominio)
4. Click **OK**

### 4.2. Agregar binding HTTPS

1. Click derecho en el sitio `DropboxOrganizer` → **Edit Bindings**
2. Click **Add**
3. Configurar:
   - Type: `https`
   - Port: `443`
   - Host name: `dropboxorganizer.com`
   - SSL certificate: Seleccionar tu certificado
4. Click **OK**

### 4.3. Copiar archivo web.config

El archivo `web.config` ya está preparado en `deployment/web.config`. Copiarlo:

```powershell
Copy-Item "C:\Users\amartin\Documents\Aplicativos\Dropbox_Chatbot\deployment\web.config" `
          -Destination "C:\inetpub\wwwroot\dropbox-organizer\frontend\web.config" `
          -Force
```

### 4.4. Configurar permisos

```powershell
# Dar permisos a IIS_IUSRS
icacls "C:\inetpub\wwwroot\dropbox-organizer" /grant "IIS_IUSRS:(OI)(CI)RX" /T
```

---

## ⚙️ PASO 5: Configurar Backend como Servicio Windows

### 5.1. Instalar NSSM (Non-Sucking Service Manager)

```powershell
# Descargar NSSM
Invoke-WebRequest -Uri "https://nssm.cc/release/nssm-2.24.zip" `
                  -OutFile "C:\nssm.zip"

# Extraer
Expand-Archive -Path "C:\nssm.zip" -DestinationPath "C:\nssm" -Force

# Copiar ejecutable a PATH
Copy-Item "C:\nssm\nssm-2.24\win64\nssm.exe" -Destination "C:\Windows\System32\" -Force
```

### 5.2. Crear entorno virtual de Python

```powershell
cd C:\inetpub\wwwroot\dropbox-organizer\backend

# Crear entorno virtual
python -m venv venv

# Activar entorno
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 5.3. Configurar variables de entorno

Copiar y editar archivo `.env`:

```powershell
Copy-Item "C:\inetpub\wwwroot\dropbox-organizer\backend\.env.example" `
          -Destination "C:\inetpub\wwwroot\dropbox-organizer\backend\.env"

# Editar con Notepad
notepad "C:\inetpub\wwwroot\dropbox-organizer\backend\.env"
```

**Configuración en `.env`:**
```env
# Producción con dominio real
FRONTEND_URL=https://dropboxorganizer.com
FRONTEND_URLS=https://dropboxorganizer.com

# Dropbox OAuth (configurar con TUS credenciales)
DROPBOX_APP_KEY=tu_app_key_aqui
DROPBOX_APP_SECRET=tu_app_secret_aqui
DROPBOX_REDIRECT_URI=https://dropboxorganizer.com/auth/dropbox/callback

# Gemini API
GEMINI_API_KEY=tu_gemini_key_aqui
```

### 5.4. Instalar backend como servicio con NSSM

Usar el script automatizado:

```powershell
cd C:\Users\amartin\Documents\Aplicativos\Dropbox_Chatbot\deployment
.\install-backend-service.ps1
```

O manualmente:

```powershell
nssm install DropboxBackend `
    "C:\inetpub\wwwroot\dropbox-organizer\backend\venv\Scripts\python.exe" `
    "-m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info"

# Configurar directorio de trabajo
nssm set DropboxBackend AppDirectory "C:\inetpub\wwwroot\dropbox-organizer\backend"

# Configurar salida de logs
nssm set DropboxBackend AppStdout "C:\inetpub\wwwroot\dropbox-organizer\logs\backend-stdout.log"
nssm set DropboxBackend AppStderr "C:\inetpub\wwwroot\dropbox-organizer\logs\backend-stderr.log"

# Iniciar servicio
nssm start DropboxBackend
```

### 5.5. Verificar que el servicio está corriendo

```powershell
# Ver estado del servicio
Get-Service DropboxBackend

# Ver logs
Get-Content "C:\inetpub\wwwroot\dropbox-organizer\logs\backend-stdout.log" -Tail 50

# Probar endpoint
curl http://localhost:8000/health
```

---

## 🔧 PASO 6: Configurar Dropbox App Console

1. Ir a https://www.dropbox.com/developers/apps
2. Seleccionar tu app o crear una nueva
3. En **OAuth 2** → **Redirect URIs**, agregar:
   ```
   https://dropboxorganizer.com/auth/dropbox/callback
   ```
4. Guardar cambios

---

## ✅ PASO 7: Verificación Final

### 7.1. Verificar componentes

```powershell
# 1. Verificar IIS está corriendo
Get-Service W3SVC

# 2. Verificar backend está corriendo
Get-Service DropboxBackend
curl http://localhost:8000/health

# 3. Verificar sitio web IIS
curl http://localhost

# 4. Verificar HTTPS (desde navegador externo)
# Abrir: https://dropboxorganizer.com
```

### 7.2. Probar flujo completo

1. Abrir navegador: `https://dropboxorganizer.com`
2. Click en "Iniciar sesión con Dropbox"
3. Autorizar en Dropbox
4. Debe redirigir de vuelta a la aplicación autenticado
5. Probar subir un archivo

### 7.3. Revisar logs si hay errores

```powershell
# Logs del backend
Get-Content "C:\inetpub\wwwroot\dropbox-organizer\logs\backend-stdout.log" -Tail 100

# Logs de IIS
Get-Content "C:\inetpub\logs\LogFiles\W3SVC1\*.log" | Select -Last 50

# Event Viewer de Windows
eventvwr.msc
```

---

## 🔄 Gestión del Servicio

### Comandos útiles

```powershell
# Detener backend
Stop-Service DropboxBackend

# Iniciar backend
Start-Service DropboxBackend

# Reiniciar backend
Restart-Service DropboxBackend

# Ver estado
Get-Service DropboxBackend

# Reiniciar IIS
iisreset

# Ver logs en tiempo real
Get-Content "C:\inetpub\wwwroot\dropbox-organizer\logs\backend-stdout.log" -Wait
```

---

## 🚨 Solución de Problemas

### Problema: "502 Bad Gateway"

**Causa:** Backend no está corriendo o no responde

**Solución:**
```powershell
# Verificar servicio
Get-Service DropboxBackend

# Ver logs
Get-Content "C:\inetpub\wwwroot\dropbox-organizer\logs\backend-stderr.log"

# Reiniciar servicio
Restart-Service DropboxBackend
```

### Problema: "403 Forbidden"

**Causa:** Permisos incorrectos en archivos

**Solución:**
```powershell
icacls "C:\inetpub\wwwroot\dropbox-organizer" /grant "IIS_IUSRS:(OI)(CI)RX" /T
iisreset
```

### Problema: "Certificado no confiable"

**Causa:** Certificado autofirmado o no instalado correctamente

**Solución:**
- Usar Let's Encrypt (win-acme) en su lugar
- O instalar certificado comercial válido

### Problema: "OAuth de Dropbox no funciona"

**Causas posibles:**
1. `DROPBOX_REDIRECT_URI` no coincide con Dropbox App Console
2. Certificado SSL no válido
3. Dominio no resuelve correctamente

**Solución:**
```powershell
# 1. Verificar .env
notepad "C:\inetpub\wwwroot\dropbox-organizer\backend\.env"

# 2. Verificar dominio resuelve
nslookup dropboxorganizer.com

# 3. Verificar certificado SSL
# Abrir navegador: https://www.ssllabs.com/ssltest/
# Analizar: dropboxorganizer.com
```

---

## 📊 Monitoreo

### Configurar Windows Performance Monitor

```powershell
# Crear colección de datos
$DataCollectorSetName = "DropboxOrganizer"
logman create counter $DataCollectorSetName -c "\Process(python)\% Processor Time" "\Process(python)\Working Set"
logman start $DataCollectorSetName
```

### Configurar alertas por email (opcional)

Usar Windows Task Scheduler para monitorear el servicio y enviar alertas.

---

## 🔄 Actualización de la Aplicación

### Script de actualización

```powershell
# 1. Detener backend
Stop-Service DropboxBackend

# 2. Actualizar código
cd "C:\Users\amartin\Documents\Aplicativos\Dropbox_Chatbot"
git pull

# 3. Copiar backend
Copy-Item ".\backend\*" `
          -Destination "C:\inetpub\wwwroot\dropbox-organizer\backend\" `
          -Recurse -Force -Exclude "venv","__pycache__",".pytest_cache",".env"

# 4. Compilar y copiar frontend
cd frontend
npm install
npm run build
Copy-Item ".\dist\*" `
          -Destination "C:\inetpub\wwwroot\dropbox-organizer\frontend\" `
          -Recurse -Force

# 5. Reiniciar servicios
Start-Service DropboxBackend
iisreset
```

---

## 📝 Checklist de Producción

- [ ] IIS instalado con URL Rewrite y ARR
- [ ] Certificado SSL instalado y válido
- [ ] Backend corriendo como servicio Windows
- [ ] Frontend compilado y desplegado en IIS
- [ ] web.config configurado correctamente
- [ ] Variables de entorno (.env) configuradas
- [ ] Redirect URI configurado en Dropbox App Console
- [ ] Firewall permite tráfico en puerto 443
- [ ] Dominio DNS apunta al servidor
- [ ] OAuth de Dropbox funciona correctamente
- [ ] Logs configurados y accesibles
- [ ] Renovación automática de certificados configurada

---

## 🔗 Referencias

- [IIS Documentation](https://docs.microsoft.com/en-us/iis/)
- [win-acme Documentation](https://www.win-acme.com/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Dropbox OAuth Guide](https://www.dropbox.com/developers/documentation/http/documentation#oauth2-authorize)

---

**¡Listo!** Tu aplicación ahora está desplegada en producción con HTTPS en Windows Server usando IIS.
