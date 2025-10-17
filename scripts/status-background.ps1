# =============================================================================
# Dropbox AI Organizer - Status Check
# =============================================================================

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Dropbox AI Organizer - Service Status" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Obtener directorio del script
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $SCRIPT_DIR

# Directorios
$PROJECT_ROOT = Split-Path -Parent $SCRIPT_DIR
$BACKEND_DIR = Join-Path $PROJECT_ROOT "backend"

# Archivos PID
$BACKEND_PID_FILE = Join-Path $PROJECT_ROOT ".backend.pid"
$FRONTEND_PID_FILE = Join-Path $PROJECT_ROOT ".frontend.pid"

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

$backend_running = $false
$frontend_running = $false
$LOCAL_IPS = Get-LocalIPs
$PRIMARY_IP = Get-PrimaryIP

# =============================================================================
# VERIFICAR BACKEND
# =============================================================================

Write-Host "Backend (FastAPI):" -ForegroundColor Yellow

if (Test-Path $BACKEND_PID_FILE) {
    $backend_pid = Get-Content $BACKEND_PID_FILE
    $backend_process = Get-Process -Id $backend_pid -ErrorAction SilentlyContinue

    if ($backend_process) {
        $backend_running = $true
        Write-Host "  Estado:  " -NoNewline
        Write-Host "EJECUTÁNDOSE" -ForegroundColor Green
        Write-Host "  PID:     $backend_pid" -ForegroundColor Gray
        Write-Host "  Puerto:  8000" -ForegroundColor Gray

        if (Test-Port -Port 8000) {
            Write-Host "  URL:     http://$PRIMARY_IP:8000" -ForegroundColor Cyan
            Write-Host "  Docs:    http://$PRIMARY_IP:8000/docs" -ForegroundColor Cyan
        } else {
            Write-Host "  Estado:  " -NoNewline
            Write-Host "Puerto 8000 no responde" -ForegroundColor Red
        }
    } else {
        Write-Host "  Estado:  " -NoNewline
        Write-Host "DETENIDO" -ForegroundColor Red
        Write-Host "  Info:    Archivo PID existe pero proceso no encontrado" -ForegroundColor Gray
    }
} else {
    Write-Host "  Estado:  " -NoNewline
    Write-Host "DETENIDO" -ForegroundColor Red
}

# =============================================================================
# VERIFICAR FRONTEND
# =============================================================================

Write-Host ""
Write-Host "Frontend (Vite + React):" -ForegroundColor Yellow

if (Test-Path $FRONTEND_PID_FILE) {
    $frontend_pid = Get-Content $FRONTEND_PID_FILE
    $frontend_process = Get-Process -Id $frontend_pid -ErrorAction SilentlyContinue

    if ($frontend_process) {
        $frontend_running = $true
        Write-Host "  Estado:  " -NoNewline
        Write-Host "EJECUTÁNDOSE" -ForegroundColor Green
        Write-Host "  PID:     $frontend_pid" -ForegroundColor Gray
        Write-Host "  Puerto:  5173" -ForegroundColor Gray

        if (Test-Port -Port 5173) {
            Write-Host "  URL:     http://$PRIMARY_IP:5173" -ForegroundColor Cyan
        } else {
            Write-Host "  Estado:  " -NoNewline
            Write-Host "Puerto 5173 no responde" -ForegroundColor Red
        }
    } else {
        Write-Host "  Estado:  " -NoNewline
        Write-Host "DETENIDO" -ForegroundColor Red
        Write-Host "  Info:    Archivo PID existe pero proceso no encontrado" -ForegroundColor Gray
    }
} else {
    Write-Host "  Estado:  " -NoNewline
    Write-Host "DETENIDO" -ForegroundColor Red
}

# =============================================================================
# VERIFICAR CONFIGURACIÓN DE SERVICIOS
# =============================================================================

Write-Host ""
Write-Host "Configuración de Servicios:" -ForegroundColor Yellow

# Verificar Dolphin
$DOLPHIN_DIR = Join-Path $BACKEND_DIR "Dolphin"
$DOLPHIN_MODEL = Join-Path $DOLPHIN_DIR "checkpoints\dolphin_model.bin"

if (Test-Path $DOLPHIN_MODEL) {
    Write-Host "  Dolphin Preview:  " -NoNewline
    Write-Host "HABILITADO" -ForegroundColor Green

    if ($backend_running -and (Test-Port -Port 8000)) {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:8000/api/document/preview/status" -TimeoutSec 5 -ErrorAction SilentlyContinue
            if ($response.preview_available) {
                Write-Host "    Estado: Operacional" -ForegroundColor Gray
            } else {
                Write-Host "    Estado: Parcial ($($response.message))" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "    Estado: No verificado" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "  Dolphin Preview:  " -NoNewline
    Write-Host "DESHABILITADO" -ForegroundColor Yellow
    Write-Host "    (Ver docs/DOLPHIN_INTEGRATION.md para habilitar)" -ForegroundColor Gray
}

# Verificar Gemini
if ($backend_running -and (Test-Port -Port 8000)) {
    try {
        $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($health.ai.gemini_available) {
            Write-Host "  Gemini AI:        " -NoNewline
            Write-Host "HABILITADO" -ForegroundColor Green
        } else {
            Write-Host "  Gemini AI:        " -NoNewline
            Write-Host "DESHABILITADO" -ForegroundColor Yellow
            Write-Host "    (Configurar GEMINI_API_KEY en .env)" -ForegroundColor Gray
        }
    } catch {
        Write-Host "  Gemini AI:        No verificado" -ForegroundColor Gray
    }
}

# =============================================================================
# RESUMEN Y LOGS
# =============================================================================

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan

if ($backend_running -and $frontend_running) {
    Write-Host "  TODOS LOS SERVICIOS EJECUTÁNDOSE" -ForegroundColor Green
    Write-Host ""
    Write-Host "Acceso desde este equipo:" -ForegroundColor White
    Write-Host "  http://localhost:5173" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Acceso desde otros dispositivos en la red:" -ForegroundColor White
    if ($LOCAL_IPS.Count -gt 0) {
        foreach ($ip in $LOCAL_IPS) {
            Write-Host "  http://$($ip.IPAddress):5173" -ForegroundColor Yellow
            Write-Host "    Interfaz: $($ip.InterfaceAlias)" -ForegroundColor Gray
        }
    } else {
        Write-Host "  http://127.0.0.1:5173" -ForegroundColor Yellow
    }
} elseif ($backend_running -or $frontend_running) {
    Write-Host "  ALGUNOS SERVICIOS EJECUTÁNDOSE" -ForegroundColor Yellow
} else {
    Write-Host "  TODOS LOS SERVICIOS DETENIDOS" -ForegroundColor Red
    Write-Host ""
    Write-Host "Para iniciar los servicios:" -ForegroundColor White
    Write-Host "  .\start-background.ps1" -ForegroundColor Gray
}

Write-Host "================================================" -ForegroundColor Cyan

# Mostrar logs recientes si existen
$LOGS_DIR = Join-Path $PROJECT_ROOT "logs"
if (Test-Path $LOGS_DIR) {
    $latest_logs = Get-ChildItem $LOGS_DIR -Filter "*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 2
    if ($latest_logs) {
        Write-Host ""
        Write-Host "Logs recientes:" -ForegroundColor White
        foreach ($log in $latest_logs) {
            Write-Host "  $($log.Name)" -ForegroundColor Gray
        }
    }
}

Write-Host ""
