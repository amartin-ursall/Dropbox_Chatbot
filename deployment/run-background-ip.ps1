# Script para ejecutar la aplicación en segundo plano con acceso por IP
Write-Host "Configurando aplicación para acceso por IP..." -ForegroundColor Cyan

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Ejecuta como Administrador" -ForegroundColor Red
    exit 1
}

$backendPath = "C:\inetpub\wwwroot\dropbox-organizer\backend"
$frontendPath = "C:\inetpub\wwwroot\dropbox-organizer\frontend"
$port = 8000

# 1. Detener servicios actuales
Write-Host ""
Write-Host "=== Deteniendo servicios ===" -ForegroundColor Yellow
Stop-Service DropboxBackend -ErrorAction SilentlyContinue
Write-Host "  Backend service detenido" -ForegroundColor Gray

Import-Module WebAdministration
Stop-Website -Name "DropboxOrganizer" -ErrorAction SilentlyContinue
Write-Host "  IIS detenido" -ForegroundColor Gray

# 2. Actualizar .env para aceptar conexiones desde cualquier IP
Write-Host ""
Write-Host "=== Configurando backend ===" -ForegroundColor Yellow
$envFile = "$backendPath\.env"

if (Test-Path $envFile) {
    $content = Get-Content $envFile -Raw

    # Obtener IP del servidor
    $ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" -and $_.IPAddress -notlike "169.254.*" } | Select-Object -First 1).IPAddress

    # Actualizar FRONTEND_URL para que sea accesible por IP
    $content = $content -replace 'FRONTEND_URL=.*', "FRONTEND_URL=http://${ip}:${port}"
    $content = $content -replace 'DROPBOX_REDIRECT_URI=.*', "DROPBOX_REDIRECT_URI=http://${ip}:${port}/auth/dropbox/callback"

    $content | Set-Content $envFile
    Write-Host "  .env actualizado con IP: $ip" -ForegroundColor Green
}

# 3. Verificar que el frontend esté compilado
Write-Host ""
Write-Host "=== Verificando frontend compilado ===" -ForegroundColor Yellow

$frontendDist = "$PSScriptRoot\..\frontend\dist"
$frontendIndex = "$frontendDist\index.html"

if (-not (Test-Path $frontendIndex)) {
    Write-Host "  Frontend no esta compilado" -ForegroundColor Red
    Write-Host "  Compilando frontend..." -ForegroundColor Gray

    Push-Location "$PSScriptRoot\..\frontend"
    & npx vite build 2>&1 | Out-Null
    Pop-Location

    if (Test-Path $frontendIndex) {
        Write-Host "  OK - Frontend compilado" -ForegroundColor Green
    } else {
        Write-Host "  ERROR - No se pudo compilar el frontend" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  Frontend ya esta compilado" -ForegroundColor Green
}

# 4. Copiar frontend compilado a carpeta backend
Write-Host ""
Write-Host "=== Copiando frontend a carpeta backend ===" -ForegroundColor Yellow

$backendFrontend = "$backendPath\frontend_static"
if (Test-Path $backendFrontend) {
    Remove-Item $backendFrontend -Recurse -Force
}

Copy-Item $frontendDist $backendFrontend -Recurse
Write-Host "  Frontend copiado a: $backendFrontend" -ForegroundColor Green

# 5. Modificar main.py para servir frontend estático
Write-Host ""
Write-Host "=== Configurando FastAPI para servir frontend ===" -ForegroundColor Yellow

$mainPy = "$backendPath\app\main.py"
$mainPyBackup = "$backendPath\app\main.py.backup"

# Hacer backup si no existe
if (-not (Test-Path $mainPyBackup)) {
    Copy-Item $mainPy $mainPyBackup
    Write-Host "  Backup creado: main.py.backup" -ForegroundColor Gray
}

# Leer contenido actual
$mainContent = Get-Content $mainPy -Raw

# Actualizar CORS para permitir cualquier IP
Write-Host "  Actualizando CORS..." -ForegroundColor Gray
if ($mainContent -match "allow_origins=FRONTEND_URLS") {
    $mainContent = $mainContent -replace 'allow_origins=FRONTEND_URLS', 'allow_origins=["*"]  # Permitir acceso desde cualquier IP'
    Write-Host "  OK - CORS configurado para cualquier IP" -ForegroundColor Green
}

# Verificar si ya tiene configuración de static files
if ($mainContent -notmatch "StaticFiles") {
    Write-Host "  Agregando soporte para archivos estaticos..." -ForegroundColor Gray

    # Agregar import después de las otras importaciones de fastapi
    $importLine = "from fastapi.staticfiles import StaticFiles"
    $mainContent = $mainContent -replace '(from fastapi.responses import.*)', "`$1`n$importLine"

    # Agregar mount de static files al final del archivo
    $staticMount = @"


# ============================================================================
# STATIC FILES - FRONTEND
# ============================================================================

# Servir assets del frontend
app.mount("/assets", StaticFiles(directory="frontend_static/assets"), name="assets")

# Servir index.html para rutas del frontend (SPA fallback)
app.mount("/", StaticFiles(directory="frontend_static", html=True), name="frontend")
"@

    $mainContent = $mainContent + $staticMount
    Write-Host "  OK - Frontend integrado en FastAPI" -ForegroundColor Green
}

# Guardar cambios
$mainContent | Set-Content $mainPy -Encoding UTF8
Write-Host "  main.py actualizado correctamente" -ForegroundColor Green

# 4. Configurar NSSM para escuchar en 0.0.0.0
Write-Host ""
Write-Host "=== Reconfigurando servicio Windows ===" -ForegroundColor Yellow

$nssmPath = "C:\ProgramData\chocolatey\bin\nssm.exe"
if (-not (Test-Path $nssmPath)) {
    $nssmPath = "nssm.exe"
}

$pythonExe = "$backendPath\venv\Scripts\python.exe"
$appParams = "-m uvicorn app.main:app --host 0.0.0.0 --port $port --log-level info"

# Eliminar servicio existente
& $nssmPath stop DropboxBackend | Out-Null
Start-Sleep -Seconds 2
& $nssmPath remove DropboxBackend confirm | Out-Null

# Crear nuevo servicio
& $nssmPath install DropboxBackend $pythonExe $appParams
& $nssmPath set DropboxBackend AppDirectory $backendPath
& $nssmPath set DropboxBackend DisplayName "Dropbox AI Organizer Backend"
& $nssmPath set DropboxBackend Description "Backend FastAPI para Dropbox AI Organizer"
& $nssmPath set DropboxBackend Start SERVICE_AUTO_START
& $nssmPath set DropboxBackend AppStdout "$backendPath\..\logs\backend-stdout.log"
& $nssmPath set DropboxBackend AppStderr "$backendPath\..\logs\backend-stderr.log"

Write-Host "  Servicio reconfigurado para escuchar en 0.0.0.0:$port" -ForegroundColor Green

# 5. Abrir puerto en firewall
Write-Host ""
Write-Host "=== Configurando Firewall ===" -ForegroundColor Yellow
$ruleName = "DropboxAIOrganizer Backend"

# Eliminar regla existente
Remove-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue

# Crear nueva regla
New-NetFirewallRule -DisplayName $ruleName `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort $port `
    -Action Allow `
    -Profile Any `
    -Enabled True | Out-Null

Write-Host "  Puerto $port abierto en firewall" -ForegroundColor Green

# 6. Iniciar servicio
Write-Host ""
Write-Host "=== Iniciando servicio ===" -ForegroundColor Yellow
Start-Service DropboxBackend
Start-Sleep -Seconds 5

$serviceStatus = Get-Service DropboxBackend
if ($serviceStatus.Status -eq "Running") {
    Write-Host "  OK - Servicio iniciado correctamente" -ForegroundColor Green
} else {
    Write-Host "  ERROR - Servicio no se inició" -ForegroundColor Red
    Write-Host "  Revisa los logs en: $backendPath\..\logs\" -ForegroundColor Yellow
    exit 1
}

# 7. Obtener IP del servidor
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" -and $_.IPAddress -notlike "169.254.*" } | Select-Object -First 1).IPAddress

# 8. Verificar que responde
Write-Host ""
Write-Host "=== Verificando aplicación ===" -ForegroundColor Yellow
Start-Sleep -Seconds 3

try {
    $response = Invoke-WebRequest -Uri "http://localhost:$port/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "  OK - Backend respondiendo correctamente" -ForegroundColor Green
    }
} catch {
    Write-Host "  ADVERTENCIA - Backend no responde aun, dale unos segundos" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "APLICACIÓN EJECUTÁNDOSE EN SEGUNDO PLANO" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "IP del servidor: $ip" -ForegroundColor Cyan
Write-Host "Puerto: $port" -ForegroundColor Cyan
Write-Host ""
Write-Host "Accede desde ESTE ordenador:" -ForegroundColor White
Write-Host "  http://localhost:$port" -ForegroundColor Cyan
Write-Host "  http://127.0.0.1:$port" -ForegroundColor Cyan
Write-Host ""
Write-Host "Accede desde OTRO ordenador en la red:" -ForegroundColor White
Write-Host "  http://${ip}:${port}" -ForegroundColor Cyan
Write-Host ""
Write-Host "API Docs:" -ForegroundColor White
Write-Host "  http://${ip}:${port}/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "CONFIGURAR DROPBOX APP" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Ve a: https://www.dropbox.com/developers/apps" -ForegroundColor White
Write-Host "En OAuth 2 -> Redirect URIs, agrega:" -ForegroundColor White
Write-Host "  http://${ip}:${port}/auth/dropbox/callback" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "COMANDOS ÚTILES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ver estado del servicio:" -ForegroundColor White
Write-Host "  Get-Service DropboxBackend" -ForegroundColor Gray
Write-Host ""
Write-Host "Detener servicio:" -ForegroundColor White
Write-Host "  Stop-Service DropboxBackend" -ForegroundColor Gray
Write-Host ""
Write-Host "Iniciar servicio:" -ForegroundColor White
Write-Host "  Start-Service DropboxBackend" -ForegroundColor Gray
Write-Host ""
Write-Host "Ver logs:" -ForegroundColor White
Write-Host "  Get-Content C:\inetpub\wwwroot\dropbox-organizer\logs\backend-stdout.log -Tail 50" -ForegroundColor Gray
Write-Host ""
