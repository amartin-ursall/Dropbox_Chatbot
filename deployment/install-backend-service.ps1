# ============================================================================
# Script de Instalación del Backend como Servicio Windows
# Dropbox AI Organizer - URSALL System
# ============================================================================
# Este script:
# 1. Descarga e instala NSSM (Non-Sucking Service Manager)
# 2. Crea entorno virtual de Python
# 3. Instala dependencias del backend
# 4. Configura el backend como servicio Windows
# 5. Inicia el servicio
# ============================================================================

param(
    [string]$InstallPath = "C:\inetpub\wwwroot\dropbox-organizer",
    [string]$ServiceName = "DropboxBackend",
    [int]$Port = 8000
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Instalación Backend como Servicio" -ForegroundColor Cyan
Write-Host "  Dropbox AI Organizer - URSALL" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que se ejecuta como administrador
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: Este script debe ejecutarse como Administrador" -ForegroundColor Red
    Write-Host "Haz click derecho en PowerShell y selecciona 'Ejecutar como administrador'" -ForegroundColor Yellow
    exit 1
}

# ============================================================================
# PASO 1: Verificar/Instalar NSSM
# ============================================================================

Write-Host "[1/7] Verificando NSSM (Non-Sucking Service Manager)..." -ForegroundColor Green

$nssmPath = "C:\Program Files\nssm\nssm.exe"
$nssmInstalled = Test-Path $nssmPath

if (-not $nssmInstalled) {
    Write-Host "  NSSM no encontrado. Descargando..." -ForegroundColor Yellow

    $nssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
    $nssmZip = "$env:TEMP\nssm.zip"
    $nssmExtract = "$env:TEMP\nssm"

    try {
        # Descargar NSSM
        Write-Host "  Descargando desde $nssmUrl..." -ForegroundColor Gray
        Invoke-WebRequest -Uri $nssmUrl -OutFile $nssmZip -UseBasicParsing

        # Extraer
        Write-Host "  Extrayendo archivos..." -ForegroundColor Gray
        Expand-Archive -Path $nssmZip -DestinationPath $nssmExtract -Force

        # Copiar a Program Files
        Write-Host "  Instalando NSSM..." -ForegroundColor Gray
        $nssmFolder = "C:\Program Files\nssm"
        New-Item -ItemType Directory -Path $nssmFolder -Force | Out-Null
        Copy-Item "$nssmExtract\nssm-2.24\win64\nssm.exe" -Destination $nssmPath -Force

        # Limpiar temporales
        Remove-Item $nssmZip -Force -ErrorAction SilentlyContinue
        Remove-Item $nssmExtract -Recurse -Force -ErrorAction SilentlyContinue

        Write-Host "  ✓ NSSM instalado correctamente en $nssmPath" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Error descargando NSSM: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "  Descarga manualmente desde: https://nssm.cc/download" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "  ✓ NSSM ya está instalado" -ForegroundColor Green
}

# ============================================================================
# PASO 2: Verificar Python
# ============================================================================

Write-Host ""
Write-Host "[2/7] Verificando Python..." -ForegroundColor Green

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue

if (-not $pythonCmd) {
    Write-Host "  ✗ Python no encontrado en PATH" -ForegroundColor Red
    Write-Host "  Instala Python 3.8+ desde: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "  Asegúrate de marcar 'Add Python to PATH' durante la instalación" -ForegroundColor Yellow
    exit 1
}

$pythonVersion = python --version 2>&1
Write-Host "  ✓ $pythonVersion encontrado" -ForegroundColor Green

# ============================================================================
# PASO 3: Crear estructura de directorios
# ============================================================================

Write-Host ""
Write-Host "[3/7] Creando estructura de directorios..." -ForegroundColor Green

$backendPath = "$InstallPath\backend"
$logsPath = "$InstallPath\logs"

try {
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    New-Item -ItemType Directory -Path $backendPath -Force | Out-Null
    New-Item -ItemType Directory -Path $logsPath -Force | Out-Null

    Write-Host "  ✓ Directorios creados:" -ForegroundColor Green
    Write-Host "    - $InstallPath" -ForegroundColor Gray
    Write-Host "    - $backendPath" -ForegroundColor Gray
    Write-Host "    - $logsPath" -ForegroundColor Gray
} catch {
    Write-Host "  ✗ Error creando directorios: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# ============================================================================
# PASO 4: Copiar archivos del backend
# ============================================================================

Write-Host ""
Write-Host "[4/7] Copiando archivos del backend..." -ForegroundColor Green

$sourcePath = Split-Path -Parent $PSScriptRoot
$sourceBackend = "$sourcePath\backend"

if (-not (Test-Path $sourceBackend)) {
    Write-Host "  ✗ No se encontró el directorio backend en: $sourceBackend" -ForegroundColor Red
    exit 1
}

try {
    # Copiar archivos excluyendo venv, cache, etc.
    $excludeDirs = @("venv", "__pycache__", ".pytest_cache", "tests")

    Write-Host "  Copiando archivos desde $sourceBackend..." -ForegroundColor Gray

    Get-ChildItem -Path $sourceBackend -Exclude $excludeDirs | ForEach-Object {
        Copy-Item $_.FullName -Destination $backendPath -Recurse -Force
    }

    Write-Host "  ✓ Archivos copiados correctamente" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Error copiando archivos: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# ============================================================================
# PASO 5: Crear entorno virtual e instalar dependencias
# ============================================================================

Write-Host ""
Write-Host "[5/7] Creando entorno virtual de Python..." -ForegroundColor Green

$venvPath = "$backendPath\venv"

try {
    # Crear venv
    & python -m venv $venvPath

    if ($LASTEXITCODE -ne 0) {
        throw "Error creando entorno virtual"
    }

    Write-Host "  ✓ Entorno virtual creado en $venvPath" -ForegroundColor Green

    # Instalar dependencias
    Write-Host "  Instalando dependencias..." -ForegroundColor Gray
    $pipPath = "$venvPath\Scripts\pip.exe"

    & $pipPath install --upgrade pip
    & $pipPath install -r "$backendPath\requirements.txt"

    if ($LASTEXITCODE -ne 0) {
        throw "Error instalando dependencias"
    }

    Write-Host "  ✓ Dependencias instaladas correctamente" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Error configurando entorno Python: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# ============================================================================
# PASO 6: Configurar archivo .env
# ============================================================================

Write-Host ""
Write-Host "[6/7] Configurando variables de entorno..." -ForegroundColor Green

$envFile = "$backendPath\.env"
$envExample = "$backendPath\.env.example"

if (-not (Test-Path $envFile)) {
    if (Test-Path $envExample) {
        Copy-Item $envExample -Destination $envFile
        Write-Host "  ⚠ Archivo .env creado desde .env.example" -ForegroundColor Yellow
        Write-Host "  IMPORTANTE: Debes editar $envFile con tus credenciales:" -ForegroundColor Yellow
        Write-Host "    - DROPBOX_APP_KEY" -ForegroundColor Gray
        Write-Host "    - DROPBOX_APP_SECRET" -ForegroundColor Gray
        Write-Host "    - DROPBOX_REDIRECT_URI (usa tu dominio HTTPS)" -ForegroundColor Gray
        Write-Host "    - GEMINI_API_KEY" -ForegroundColor Gray
        Write-Host "    - FRONTEND_URL (usa tu dominio HTTPS)" -ForegroundColor Gray
    } else {
        Write-Host "  ✗ No se encontró .env ni .env.example" -ForegroundColor Red
        Write-Host "  Crea manualmente $envFile con las variables necesarias" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ✓ Archivo .env ya existe" -ForegroundColor Green
}

# ============================================================================
# PASO 7: Instalar y configurar servicio con NSSM
# ============================================================================

Write-Host ""
Write-Host "[7/7] Configurando servicio Windows..." -ForegroundColor Green

# Detener servicio si ya existe
$existingService = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Host "  Servicio existente encontrado. Deteniéndolo..." -ForegroundColor Yellow
    Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2

    # Eliminar servicio existente
    & $nssmPath remove $ServiceName confirm
    Start-Sleep -Seconds 2
}

try {
    $pythonExe = "$venvPath\Scripts\python.exe"
    $appParams = "-m uvicorn app.main:app --host 127.0.0.1 --port $Port --log-level info"

    Write-Host "  Instalando servicio $ServiceName..." -ForegroundColor Gray

    # Instalar servicio
    & $nssmPath install $ServiceName $pythonExe $appParams

    # Configurar directorio de trabajo
    & $nssmPath set $ServiceName AppDirectory $backendPath

    # Configurar descripción
    & $nssmPath set $ServiceName Description "Dropbox AI Organizer - URSALL Backend API (FastAPI/Uvicorn)"

    # Configurar inicio automático
    & $nssmPath set $ServiceName Start SERVICE_AUTO_START

    # Configurar logs
    $stdoutLog = "$logsPath\backend-stdout.log"
    $stderrLog = "$logsPath\backend-stderr.log"

    & $nssmPath set $ServiceName AppStdout $stdoutLog
    & $nssmPath set $ServiceName AppStderr $stderrLog

    # Configurar rotación de logs (10 MB max)
    & $nssmPath set $ServiceName AppStdoutCreationDisposition 4
    & $nssmPath set $ServiceName AppStderrCreationDisposition 4
    & $nssmPath set $ServiceName AppRotateFiles 1
    & $nssmPath set $ServiceName AppRotateBytes 10485760

    # Configurar reinicio automático en caso de fallo
    & $nssmPath set $ServiceName AppExit Default Restart
    & $nssmPath set $ServiceName AppRestartDelay 5000

    Write-Host "  ✓ Servicio instalado correctamente" -ForegroundColor Green

    # Iniciar servicio
    Write-Host "  Iniciando servicio..." -ForegroundColor Gray
    Start-Service -Name $ServiceName
    Start-Sleep -Seconds 3

    # Verificar estado
    $service = Get-Service -Name $ServiceName
    if ($service.Status -eq "Running") {
        Write-Host "  ✓ Servicio iniciado correctamente" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Servicio instalado pero no está corriendo" -ForegroundColor Yellow
        Write-Host "  Estado: $($service.Status)" -ForegroundColor Yellow
    }

} catch {
    Write-Host "  ✗ Error configurando servicio: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# ============================================================================
# RESUMEN FINAL
# ============================================================================

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  ✓ Instalación Completada" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuración:" -ForegroundColor White
Write-Host "  - Servicio: $ServiceName" -ForegroundColor Gray
Write-Host "  - Puerto: $Port" -ForegroundColor Gray
Write-Host "  - Ruta: $backendPath" -ForegroundColor Gray
Write-Host "  - Logs: $logsPath" -ForegroundColor Gray
Write-Host ""
Write-Host "Comandos útiles:" -ForegroundColor White
Write-Host "  - Ver estado:     Get-Service $ServiceName" -ForegroundColor Gray
Write-Host "  - Iniciar:        Start-Service $ServiceName" -ForegroundColor Gray
Write-Host "  - Detener:        Stop-Service $ServiceName" -ForegroundColor Gray
Write-Host "  - Reiniciar:      Restart-Service $ServiceName" -ForegroundColor Gray
Write-Host "  - Ver logs:       Get-Content '$stdoutLog' -Tail 50 -Wait" -ForegroundColor Gray
Write-Host ""
Write-Host "Próximos pasos:" -ForegroundColor Yellow
Write-Host "  1. Editar $envFile con tus credenciales" -ForegroundColor Gray
Write-Host "  2. Reiniciar el servicio: Restart-Service $ServiceName" -ForegroundColor Gray
Write-Host "  3. Verificar health check: curl http://localhost:$Port/health" -ForegroundColor Gray
Write-Host "  4. Configurar sitio en IIS con web.config" -ForegroundColor Gray
Write-Host "  5. Instalar certificado SSL" -ForegroundColor Gray
Write-Host ""
