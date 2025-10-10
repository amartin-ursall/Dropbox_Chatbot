# Guía de Actualización en Producción

Esta guía explica cómo realizar cambios y actualizaciones en la aplicación Dropbox AI Organizer una vez desplegada en producción en Windows Server con IIS.

---

## 📋 Flujo de Actualización Recomendado

```
1. Desarrollo Local
   ↓
2. Pruebas Locales
   ↓
3. Commit a Git
   ↓
4. Desplegar en Producción
   ↓
5. Verificar Funcionamiento
```

---

## 🔧 Opción 1: Actualización Manual (Recomendado para empezar)

### Paso 1: Realizar cambios en tu máquina local

```powershell
# En tu máquina de desarrollo
cd "C:\Users\amartin\Documents\Aplicativos\Dropbox_Chatbot"

# Hacer tus cambios en el código...
# - Editar archivos backend (Python)
# - Editar archivos frontend (React/TypeScript)
```

### Paso 2: Probar cambios localmente

```powershell
# Probar backend
cd backend
py -m uvicorn app.main:app --reload

# Probar frontend (en otra terminal)
cd frontend
npm run dev
```

### Paso 3: Guardar cambios en Git

```powershell
# Hacer commit de los cambios
git add .
git commit -m "Descripción de los cambios realizados"
git push origin master
```

### Paso 4: Desplegar en producción

**Conectarse al servidor Windows:**
- Via RDP (Escritorio Remoto)
- O via PowerShell remoto

**En el servidor de producción:**

```powershell
# 1. DETENER SERVICIO BACKEND
Stop-Service DropboxBackend

# 2. NAVEGAR AL DIRECTORIO DEL PROYECTO
cd "C:\Users\amartin\Documents\Aplicativos\Dropbox_Chatbot"

# 3. ACTUALIZAR CÓDIGO DESDE GIT
git pull origin master

# 4. ACTUALIZAR BACKEND

# Copiar nuevos archivos (preservando .env)
Copy-Item ".\backend\*" `
          -Destination "C:\inetpub\wwwroot\dropbox-organizer\backend\" `
          -Recurse -Force `
          -Exclude "venv","__pycache__",".pytest_cache",".env","logs"

# Si hay nuevas dependencias de Python
cd "C:\inetpub\wwwroot\dropbox-organizer\backend"
.\venv\Scripts\activate
pip install -r requirements.txt
deactivate

# 5. ACTUALIZAR FRONTEND

cd "C:\Users\amartin\Documents\Aplicativos\Dropbox_Chatbot\frontend"

# Instalar nuevas dependencias si las hay
npm install

# Compilar para producción
npm run build

# Copiar archivos compilados
Copy-Item ".\dist\*" `
          -Destination "C:\inetpub\wwwroot\dropbox-organizer\frontend\" `
          -Recurse -Force

# 6. REINICIAR SERVICIOS
Start-Service DropboxBackend
iisreset

# 7. VERIFICAR
# Esperar 10 segundos para que el servicio inicie
Start-Sleep -Seconds 10

# Verificar backend
curl http://localhost:8000/health

# Verificar frontend (desde navegador)
# Abrir: https://dropboxorganizer.com
```

### Paso 5: Verificar en producción

1. Abrir navegador: `https://dropboxorganizer.com`
2. Probar funcionalidad modificada
3. Verificar logs si hay errores:
   ```powershell
   Get-Content "C:\inetpub\wwwroot\dropbox-organizer\logs\backend-stdout.log" -Tail 50
   ```

---

## 🚀 Opción 2: Script de Actualización Automática

He creado un script que automatiza todo el proceso:

### Usar el script de deployment

```powershell
# En el servidor de producción
cd "C:\Users\amartin\Documents\Aplicativos\Dropbox_Chatbot\deployment"
.\deploy.ps1
```

El script hace automáticamente:
- ✅ Detiene el backend
- ✅ Actualiza código desde Git
- ✅ Copia archivos del backend
- ✅ Compila el frontend
- ✅ Copia archivos del frontend
- ✅ Reinicia servicios
- ✅ Verifica que todo funcione

---

## 📝 Opción 3: Actualización Remota desde tu PC

Si tienes PowerShell Remoting configurado, puedes actualizar desde tu PC local:

### Configurar PowerShell Remoting (una sola vez)

**En el servidor Windows:**
```powershell
# Habilitar PowerShell Remoting
Enable-PSRemoting -Force

# Permitir acceso desde tu PC (reemplaza con la IP de tu PC)
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "192.168.0.98" -Force
```

### Actualizar desde tu PC local

```powershell
# Desde tu PC de desarrollo
$serverIP = "IP_DEL_SERVIDOR"  # Ejemplo: "192.168.1.100"
$credential = Get-Credential   # Usuario y contraseña del servidor

# Conectar al servidor y ejecutar actualización
Invoke-Command -ComputerName $serverIP -Credential $credential -ScriptBlock {
    cd "C:\Users\amartin\Documents\Aplicativos\Dropbox_Chatbot\deployment"
    .\deploy.ps1
}
```

---

## 🔄 Tipos de Actualizaciones y Procedimientos

### 1. Cambios solo en Backend (Python)

```powershell
# Servidor de producción
Stop-Service DropboxBackend

cd "C:\Users\amartin\Documents\Aplicativos\Dropbox_Chatbot"
git pull

Copy-Item ".\backend\*" `
          -Destination "C:\inetpub\wwwroot\dropbox-organizer\backend\" `
          -Recurse -Force `
          -Exclude "venv","__pycache__",".env"

Start-Service DropboxBackend
```

**Casos:**
- Cambios en lógica de negocio
- Nuevos endpoints API
- Mejoras en extractores NLP
- Corrección de bugs

### 2. Cambios solo en Frontend (React)

```powershell
# Servidor de producción
cd "C:\Users\amartin\Documents\Aplicativos\Dropbox_Chatbot"
git pull

cd frontend
npm install  # Solo si hay nuevas dependencias
npm run build

Copy-Item ".\dist\*" `
          -Destination "C:\inetpub\wwwroot\dropbox-organizer\frontend\" `
          -Recurse -Force

# NO necesitas reiniciar backend, solo IIS
iisreset
```

**Casos:**
- Cambios en UI/diseño
- Nuevos componentes visuales
- Corrección de bugs de interfaz
- Mejoras de UX

### 3. Cambios en Variables de Entorno

```powershell
# Editar .env en producción
notepad "C:\inetpub\wwwroot\dropbox-organizer\backend\.env"

# Cambiar valores necesarios...
# Guardar y cerrar

# Reiniciar backend para que tome los cambios
Restart-Service DropboxBackend
```

**Casos:**
- Cambiar API keys
- Actualizar URLs
- Modificar configuración OAuth

### 4. Actualizar Dependencias de Python

```powershell
# Si agregaste nuevas librerías en requirements.txt
cd "C:\inetpub\wwwroot\dropbox-organizer\backend"
.\venv\Scripts\activate
pip install -r requirements.txt
deactivate

Restart-Service DropboxBackend
```

### 5. Actualizar Dependencias de Node.js

```powershell
cd "C:\Users\amartin\Documents\Aplicativos\Dropbox_Chatbot\frontend"
npm install  # Instala nuevas dependencias
npm run build
Copy-Item ".\dist\*" -Destination "C:\inetpub\wwwroot\dropbox-organizer\frontend\" -Recurse -Force
iisreset
```

---

## 🛡️ Buenas Prácticas

### 1. Siempre hacer backup antes de actualizar

```powershell
# Crear backup de la versión actual
$fecha = Get-Date -Format "yyyy-MM-dd_HH-mm"
$backupPath = "C:\backups\dropbox-organizer\$fecha"

New-Item -ItemType Directory -Path $backupPath -Force

# Backup del backend
Copy-Item "C:\inetpub\wwwroot\dropbox-organizer\backend" `
          -Destination "$backupPath\backend" `
          -Recurse -Force -Exclude "venv","__pycache__"

# Backup del frontend
Copy-Item "C:\inetpub\wwwroot\dropbox-organizer\frontend" `
          -Destination "$backupPath\frontend" `
          -Recurse -Force

# Backup del .env (importante!)
Copy-Item "C:\inetpub\wwwroot\dropbox-organizer\backend\.env" `
          -Destination "$backupPath\.env"

Write-Host "Backup creado en: $backupPath"
```

### 2. Probar en entorno de prueba primero

Si es posible, crea un entorno de staging:
- Usar un subdominio: `staging.dropboxorganizer.com`
- Probar cambios ahí primero
- Si funciona, desplegar a producción

### 3. Monitorear después de actualizar

```powershell
# Ver logs en tiempo real
Get-Content "C:\inetpub\wwwroot\dropbox-organizer\logs\backend-stdout.log" -Wait

# Verificar estado del servicio
Get-Service DropboxBackend

# Verificar que responda
curl http://localhost:8000/health
```

### 4. Tener plan de rollback

Si algo sale mal, restaurar desde backup:

```powershell
# Detener servicios
Stop-Service DropboxBackend

# Restaurar desde backup (usar la fecha del backup)
$backupPath = "C:\backups\dropbox-organizer\2025-10-10_14-30"

Copy-Item "$backupPath\backend\*" `
          -Destination "C:\inetpub\wwwroot\dropbox-organizer\backend\" `
          -Recurse -Force

Copy-Item "$backupPath\frontend\*" `
          -Destination "C:\inetpub\wwwroot\dropbox-organizer\frontend\" `
          -Recurse -Force

Copy-Item "$backupPath\.env" `
          -Destination "C:\inetpub\wwwroot\dropbox-organizer\backend\.env"

# Reiniciar servicios
Start-Service DropboxBackend
iisreset

Write-Host "Rollback completado"
```

---

## 🔍 Troubleshooting de Actualizaciones

### Problema: Backend no arranca después de actualizar

**Diagnóstico:**
```powershell
# Ver logs de error
Get-Content "C:\inetpub\wwwroot\dropbox-organizer\logs\backend-stderr.log" -Tail 50

# Ver estado del servicio
Get-Service DropboxBackend | Format-List *
```

**Posibles causas:**
1. **Dependencias faltantes**: Ejecutar `pip install -r requirements.txt`
2. **Error de sintaxis en código**: Revisar logs, corregir código
3. **Variables de entorno incorrectas**: Verificar `.env`
4. **Puerto ocupado**: Verificar que nada más use el puerto 8000

### Problema: Frontend muestra página en blanco

**Posibles causas:**
1. **Build incompleto**: Volver a compilar `npm run build`
2. **Archivos no copiados**: Verificar que `dist\*` se copió a `frontend\`
3. **Rutas incorrectas**: Verificar `web.config` en el frontend

**Solución:**
```powershell
# Recompilar frontend
cd "C:\Users\amartin\Documents\Aplicativos\Dropbox_Chatbot\frontend"
Remove-Item .\dist -Recurse -Force  # Limpiar build anterior
npm run build

# Copiar de nuevo
Copy-Item ".\dist\*" `
          -Destination "C:\inetpub\wwwroot\dropbox-organizer\frontend\" `
          -Recurse -Force

iisreset
```

### Problema: Cambios no se reflejan

**Causa:** Caché del navegador o IIS

**Solución:**
```powershell
# Limpiar caché de IIS
iisreset /restart

# En el navegador: Ctrl + Shift + R (hard reload)
# O abrir en modo incógnito
```

---

## 📊 Monitoreo Post-Actualización

### Checklist de verificación

Después de cada actualización, verificar:

```powershell
# 1. Backend responde
$response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
Write-Host "Backend Health: $($response.StatusCode)"

# 2. Frontend accesible
$response = Invoke-WebRequest -Uri "https://dropboxorganizer.com" -UseBasicParsing
Write-Host "Frontend Status: $($response.StatusCode)"

# 3. OAuth funciona (manual - abrir navegador)
Start-Process "https://dropboxorganizer.com"

# 4. No hay errores en logs
$errores = Get-Content "C:\inetpub\wwwroot\dropbox-organizer\logs\backend-stderr.log" -Tail 20
if ($errores) {
    Write-Host "ADVERTENCIA: Hay errores en logs:" -ForegroundColor Yellow
    Write-Host $errores
}

# 5. Servicio está corriendo
$servicio = Get-Service DropboxBackend
Write-Host "Servicio Backend: $($servicio.Status)"
```

---

## 🔐 Consideraciones de Seguridad

### 1. No exponer credenciales

```powershell
# NUNCA hacer esto en producción:
# git add .env  ❌ MALO

# El archivo .env ya está en .gitignore
# Verificar:
Get-Content ".gitignore" | Select-String ".env"
```

### 2. Mantener backups del .env

```powershell
# Backup encriptado del .env (opcional)
$envPath = "C:\inetpub\wwwroot\dropbox-organizer\backend\.env"
$backupPath = "C:\backups\secrets\.env.backup"

# Crear directorio seguro
New-Item -ItemType Directory -Path "C:\backups\secrets" -Force
Copy-Item $envPath -Destination $backupPath

# Aplicar permisos restrictivos
icacls "C:\backups\secrets" /inheritance:r
icacls "C:\backups\secrets" /grant:r "${env:USERNAME}:(OI)(CI)F"
```

### 3. Auditar cambios

```powershell
# Ver últimos commits antes de actualizar
git log --oneline -10

# Ver qué archivos cambiaron
git diff HEAD~1 --name-only
```

---

## 📅 Mantenimiento Programado

### Script de actualización semanal (opcional)

Crear tarea programada para actualizaciones automáticas:

```powershell
# Crear script de actualización automática
$scriptContent = @'
# Actualización automática semanal
cd "C:\Users\amartin\Documents\Aplicativos\Dropbox_Chatbot\deployment"
.\deploy.ps1 >> "C:\backups\update-logs\update_$(Get-Date -Format 'yyyy-MM-dd').log" 2>&1
'@

$scriptPath = "C:\scripts\auto-update.ps1"
New-Item -ItemType Directory -Path "C:\scripts" -Force
Set-Content -Path $scriptPath -Value $scriptContent

# Crear tarea programada (ejecutar domingos a las 3am)
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File $scriptPath"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 3am
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName "DropboxOrganizerUpdate" `
                       -Action $action `
                       -Trigger $trigger `
                       -Principal $principal `
                       -Description "Actualización automática semanal"
```

---

## ✅ Resumen de Comandos Rápidos

### Actualización completa
```powershell
cd "C:\Users\amartin\Documents\Aplicativos\Dropbox_Chatbot\deployment"
.\deploy.ps1
```

### Solo backend
```powershell
Stop-Service DropboxBackend
git pull
Copy-Item ".\backend\*" -Destination "C:\inetpub\wwwroot\dropbox-organizer\backend\" -Recurse -Force -Exclude "venv","__pycache__",".env"
Start-Service DropboxBackend
```

### Solo frontend
```powershell
git pull
cd frontend
npm run build
Copy-Item ".\dist\*" -Destination "C:\inetpub\wwwroot\dropbox-organizer\frontend\" -Recurse -Force
iisreset
```

### Rollback rápido
```powershell
Stop-Service DropboxBackend
Copy-Item "C:\backups\dropbox-organizer\[FECHA]\*" -Destination "C:\inetpub\wwwroot\dropbox-organizer\" -Recurse -Force
Start-Service DropboxBackend
iisreset
```

---

## 📞 Contacto y Soporte

En caso de problemas durante una actualización:

1. **Revisar logs**: `C:\inetpub\wwwroot\dropbox-organizer\logs\`
2. **Hacer rollback** si es crítico
3. **Consultar esta documentación**
4. **Revisar commits recientes**: `git log`

---

**Última actualización:** 2025-10-10
**Versión:** 1.0
