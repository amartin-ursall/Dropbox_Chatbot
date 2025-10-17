# =============================================================================
# Dropbox AI Organizer - Start Background Services
# =============================================================================
# Este script inicia el backend y frontend en segundo plano para acceso por IP
# No se requiere dominio, acceso directo por IP:Puerto

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Dropbox AI Organizer - Background Start" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Obtener directorio del script
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $SCRIPT_DIR

# Directorios
$BACKEND_DIR = Join-Path (Split-Path -Parent $SCRIPT_DIR) "backend"
$FRONTEND_DIR = Join-Path (Split-Path -Parent $SCRIPT_DIR) "frontend"
$LOGS_DIR = Join-Path (Split-Path -Parent $SCRIPT_DIR) "logs"

# Crear directorio de logs si no existe
if (-not (Test-Path $LOGS_DIR)) {
    New-Item -ItemType Directory -Path $LOGS_DIR | Out-Null
}

# Archivos de log con timestamp
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$BACKEND_LOG = Join-Path $LOGS_DIR "backend_$TIMESTAMP.log"
$FRONTEND_LOG = Join-Path $LOGS_DIR "frontend_$TIMESTAMP.log"

# Archivos PID para control de procesos
$PROJECT_ROOT = Split-Path -Parent $SCRIPT_DIR
$BACKEND_PID_FILE = Join-Path $PROJECT_ROOT ".backend.pid"
$FRONTEND_PID_FILE = Join-Path $PROJECT_ROOT ".frontend.pid"

# =============================================================================
# FUNCIONES
# =============================================================================

function Test-Port {
    param([int]$Port)
    $connection = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue -InformationLevel Quiet
    return $connection
}

function Get-LocalIPs {
    try {
        $ips = Get-NetIPAddress -AddressFamily IPv4 | Where-Object {
            $_.InterfaceAlias -notlike "*Loopback*" -and
            $_.IPAddress -ne "127.0.0.1" -and
            ($_.PrefixOrigin -eq "Dhcp" -or $_.PrefixOrigin -eq "Manual")
        } | Select-Object IPAddress, InterfaceAlias | Sort-Object InterfaceAlias

        return $ips
    } catch {
        return @()
    }
}

function Get-PrimaryIP {
    $ips = Get-LocalIPs
    if ($ips.Count -gt 0) {
        return $ips[0].IPAddress
    }
    return "127.0.0.1"
}

# =============================================================================
# VERIFICAR SI YA ESTÁ EJECUTÁNDOSE
# =============================================================================

Write-Host "[1/5] Verificando estado de servicios..." -ForegroundColor Yellow

if (Test-Path $BACKEND_PID_FILE) {
    $backend_pid = Get-Content $BACKEND_PID_FILE
    $backend_process = Get-Process -Id $backend_pid -ErrorAction SilentlyContinue
    if ($backend_process) {
        Write-Host "  [!] Backend ya está ejecutándose (PID: $backend_pid)" -ForegroundColor Red
        Write-Host "  [!] Use 'stop-background.ps1' para detenerlo primero" -ForegroundColor Red
        exit 1
    } else {
        Remove-Item $BACKEND_PID_FILE -Force
    }
}

if (Test-Path $FRONTEND_PID_FILE) {
    $frontend_pid = Get-Content $FRONTEND_PID_FILE
    $frontend_process = Get-Process -Id $frontend_pid -ErrorAction SilentlyContinue
    if ($frontend_process) {
        Write-Host "  [!] Frontend ya está ejecutándose (PID: $frontend_pid)" -ForegroundColor Red
        Write-Host "  [!] Use 'stop-background.ps1' para detenerlo primero" -ForegroundColor Red
        exit 1
    } else {
        Remove-Item $FRONTEND_PID_FILE -Force
    }
}

Write-Host "  [OK] Servicios no están ejecutándose" -ForegroundColor Green

# =============================================================================
# INSTALAR DEPENDENCIAS SI ES NECESARIO
# =============================================================================

Write-Host ""
Write-Host "[2/5] Verificando dependencias..." -ForegroundColor Yellow

# Detectar Python disponible
$PYTHON_CMD = $null
$pythonCommands = @("python", "python3", "py")

foreach ($cmd in $pythonCommands) {
    try {
        $version = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $PYTHON_CMD = $cmd
            Write-Host "  [*] Python detectado: $version" -ForegroundColor Gray
            break
        }
    } catch {
        continue
    }
}

if (-not $PYTHON_CMD) {
    Write-Host "  [!] ERROR: Python no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host "  [!] Instala Python desde https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host "  [!] O ejecuta: winget install Python.Python.3.12" -ForegroundColor Yellow
    exit 1
}

# Backend - Python
Set-Location $BACKEND_DIR
if (-not (Test-Path "venv")) {
    Write-Host "  [!] Creando entorno virtual de Python..." -ForegroundColor Yellow
    & $PYTHON_CMD -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [!] ERROR: No se pudo crear el entorno virtual" -ForegroundColor Red
        exit 1
    }
}

$PYTHON_PATH = Join-Path $BACKEND_DIR "venv\Scripts\python.exe"
$PIP_PATH = Join-Path $BACKEND_DIR "venv\Scripts\pip.exe"

if (-not (Test-Path $PYTHON_PATH)) {
    Write-Host "  [!] ERROR: No se pudo crear el entorno virtual correctamente" -ForegroundColor Red
    exit 1
}

Write-Host "  [*] Verificando paquetes Python..." -ForegroundColor Gray
& $PIP_PATH install -q -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [!] ADVERTENCIA: Algunos paquetes podrían no haberse instalado correctamente" -ForegroundColor Yellow
}

# Frontend - Node
Set-Location $FRONTEND_DIR

# Verificar que Node.js esté instalado
try {
    $nodeVersion = & node --version 2>&1
    $npmVersion = & npm --version 2>&1
    Write-Host "  [*] Node.js detectado: $nodeVersion (npm: $npmVersion)" -ForegroundColor Gray
} catch {
    Write-Host "  [!] ERROR: Node.js no está instalado" -ForegroundColor Red
    Write-Host "  [!] Instala Node.js desde https://nodejs.org/" -ForegroundColor Red
    Write-Host "  [!] O ejecuta: winget install OpenJS.NodeJS" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path "node_modules")) {
    Write-Host "  [!] Instalando dependencias de Node.js..." -ForegroundColor Yellow
    npm install --silent
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [!] ERROR: No se pudieron instalar las dependencias de Node.js" -ForegroundColor Red
        exit 1
    }
}

Write-Host "  [OK] Dependencias verificadas" -ForegroundColor Green

# =============================================================================
# VERIFICAR CONFIGURACIÓN DE DOLPHIN (OPCIONAL)
# =============================================================================

Write-Host ""
Write-Host "[2.5/5] Verificando configuración de Dolphin..." -ForegroundColor Yellow

$DOLPHIN_DIR = Join-Path $BACKEND_DIR "Dolphin"
$DOLPHIN_CHECKPOINTS = Join-Path $DOLPHIN_DIR "checkpoints"
$DOLPHIN_MODEL = Join-Path $DOLPHIN_CHECKPOINTS "dolphin_model.bin"
$DOLPHIN_TOKENIZER = Join-Path $DOLPHIN_CHECKPOINTS "dolphin_tokenizer.json"

if (Test-Path $DOLPHIN_MODEL) {
    $modelSize = (Get-Item $DOLPHIN_MODEL).Length / 1MB
    Write-Host "  [OK] Dolphin modelo encontrado ($([math]::Round($modelSize, 1)) MB)" -ForegroundColor Green

    if (Test-Path $DOLPHIN_TOKENIZER) {
        Write-Host "  [OK] Dolphin tokenizer encontrado" -ForegroundColor Green
        Write-Host "  [*] Preview de documentos HABILITADO" -ForegroundColor Cyan
    } else {
        Write-Host "  [!] Dolphin tokenizer no encontrado" -ForegroundColor Yellow
        Write-Host "  [*] Preview de documentos DESHABILITADO" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [!] Dolphin no configurado (opcional)" -ForegroundColor Yellow
    Write-Host "      Para habilitar preview de documentos:" -ForegroundColor Gray
    Write-Host "      1. Descarga el modelo desde Google Drive o Baidu Yun" -ForegroundColor Gray
    Write-Host "      2. Coloca los archivos en: $DOLPHIN_CHECKPOINTS" -ForegroundColor Gray
    Write-Host "      Ver docs/DOLPHIN_INTEGRATION.md para más información" -ForegroundColor Gray
}

# =============================================================================
# OBTENER IP LOCAL
# =============================================================================

Write-Host ""
Write-Host "[3/5] Configurando acceso de red..." -ForegroundColor Yellow

$LOCAL_IPS = Get-LocalIPs
$PRIMARY_IP = Get-PrimaryIP

if ($LOCAL_IPS.Count -gt 0) {
    Write-Host "  [*] Interfaces de red detectadas:" -ForegroundColor Cyan
    foreach ($ip in $LOCAL_IPS) {
        Write-Host "      - $($ip.IPAddress) ($($ip.InterfaceAlias))" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "  [*] IP Principal: $PRIMARY_IP" -ForegroundColor Cyan
} else {
    Write-Host "  [!] No se detectaron IPs de red, usando localhost" -ForegroundColor Yellow
    $PRIMARY_IP = "127.0.0.1"
}

# =============================================================================
# INICIAR BACKEND
# =============================================================================

Write-Host ""
Write-Host "[4/5] Iniciando Backend (FastAPI)..." -ForegroundColor Yellow

Set-Location $BACKEND_DIR

# Crear script temporal para ejecutar backend
$BACKEND_SCRIPT = @"
`$env:PYTHONUNBUFFERED = "1"
Set-Location "$BACKEND_DIR"
& "$PYTHON_PATH" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > "$BACKEND_LOG" 2>&1
"@

$BACKEND_SCRIPT_FILE = Join-Path $BACKEND_DIR "run_backend.ps1"
$BACKEND_SCRIPT | Out-File -FilePath $BACKEND_SCRIPT_FILE -Encoding UTF8

# Iniciar backend en segundo plano
$backend_process = Start-Process -FilePath "powershell.exe" `
    -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $BACKEND_SCRIPT_FILE `
    -WindowStyle Hidden `
    -PassThru

$backend_process.Id | Out-File -FilePath $BACKEND_PID_FILE

Write-Host "  [*] Backend iniciado (PID: $($backend_process.Id))" -ForegroundColor Green
Write-Host "  [*] Log: $BACKEND_LOG" -ForegroundColor Gray

# Esperar a que el backend esté listo
Write-Host "  [*] Esperando a que el backend esté listo..." -ForegroundColor Gray
$attempts = 0
$max_attempts = 30
while (-not (Test-Port -Port 8000) -and $attempts -lt $max_attempts) {
    Start-Sleep -Seconds 1
    $attempts++
    Write-Host "." -NoNewline -ForegroundColor Gray
}
Write-Host ""

if (Test-Port -Port 8000) {
    Write-Host "  [OK] Backend listo en http://$PRIMARY_IP:8000" -ForegroundColor Green
} else {
    Write-Host "  [!] Backend no responde. Revisa el log." -ForegroundColor Red
    exit 1
}

# =============================================================================
# INICIAR FRONTEND
# =============================================================================

Write-Host ""
Write-Host "[5/5] Iniciando Frontend (Vite + React)..." -ForegroundColor Yellow

Set-Location $FRONTEND_DIR

# Configurar variables de entorno para frontend
# Usar localhost porque el proxy de Vite manejará las peticiones
$env:VITE_USE_HTTPS = "false"
$env:VITE_BACKEND_URL = "http://localhost:8000"

# Crear script temporal para ejecutar frontend
$FRONTEND_SCRIPT = @"
`$env:VITE_USE_HTTPS = "false"
`$env:VITE_BACKEND_URL = "http://localhost:8000"
Set-Location "$FRONTEND_DIR"
npm run dev > "$FRONTEND_LOG" 2>&1
"@

$FRONTEND_SCRIPT_FILE = Join-Path $FRONTEND_DIR "run_frontend.ps1"
$FRONTEND_SCRIPT | Out-File -FilePath $FRONTEND_SCRIPT_FILE -Encoding UTF8

# Iniciar frontend en segundo plano
$frontend_process = Start-Process -FilePath "powershell.exe" `
    -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $FRONTEND_SCRIPT_FILE `
    -WindowStyle Hidden `
    -PassThru

$frontend_process.Id | Out-File -FilePath $FRONTEND_PID_FILE

Write-Host "  [*] Frontend iniciado (PID: $($frontend_process.Id))" -ForegroundColor Green
Write-Host "  [*] Log: $FRONTEND_LOG" -ForegroundColor Gray

# Esperar a que el frontend esté listo
Write-Host "  [*] Esperando a que el frontend esté listo..." -ForegroundColor Gray
$attempts = 0
$max_attempts = 45
while (-not (Test-Port -Port 5173) -and $attempts -lt $max_attempts) {
    Start-Sleep -Seconds 1
    $attempts++
    Write-Host "." -NoNewline -ForegroundColor Gray
}
Write-Host ""

if (Test-Port -Port 5173) {
    Write-Host "  [OK] Frontend listo en http://$PRIMARY_IP:5173" -ForegroundColor Green
} else {
    Write-Host "  [!] Frontend no responde. Revisa el log." -ForegroundColor Red
}

# =============================================================================
# RESUMEN
# =============================================================================

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  SERVICIOS INICIADOS CORRECTAMENTE" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Accede a la aplicación desde este equipo:" -ForegroundColor White
Write-Host "  http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Accede desde otros dispositivos en la red:" -ForegroundColor White
if ($LOCAL_IPS.Count -gt 0) {
    foreach ($ip in $LOCAL_IPS) {
        Write-Host "  http://$($ip.IPAddress):5173" -ForegroundColor Yellow
        Write-Host "    Interfaz: $($ip.InterfaceAlias)" -ForegroundColor Gray
    }
} else {
    Write-Host "  http://127.0.0.1:5173" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "Endpoints del backend:" -ForegroundColor White
Write-Host "  API Docs:     http://$PRIMARY_IP:8000/docs" -ForegroundColor Cyan
Write-Host "  Health Check: http://$PRIMARY_IP:8000/health" -ForegroundColor Cyan
Write-Host "  Preview Status: http://$PRIMARY_IP:8000/api/document/preview/status" -ForegroundColor Cyan
Write-Host ""
Write-Host "Nota: El frontend usa proxy de Vite para comunicarse con el backend." -ForegroundColor Gray
Write-Host "      No necesitas acceder directamente al backend desde el navegador." -ForegroundColor Gray
Write-Host ""
Write-Host "Control de servicios:" -ForegroundColor White
Write-Host "  Detener:  .\stop-background.ps1" -ForegroundColor Gray
Write-Host "  Estado:   .\status-background.ps1" -ForegroundColor Gray
Write-Host "  Logs:     $LOGS_DIR" -ForegroundColor Gray
Write-Host ""
Write-Host "Procesos en segundo plano:" -ForegroundColor White
Write-Host "  Backend PID:  $($backend_process.Id)" -ForegroundColor Gray
Write-Host "  Frontend PID: $($frontend_process.Id)" -ForegroundColor Gray
Write-Host ""

# Volver al directorio original
Set-Location $SCRIPT_DIR
