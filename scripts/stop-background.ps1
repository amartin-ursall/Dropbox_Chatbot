# =============================================================================
# Dropbox AI Organizer - Stop Background Services
# =============================================================================

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Dropbox AI Organizer - Stop Services" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Obtener directorio del script
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $SCRIPT_DIR

# Directorios
$PROJECT_ROOT = Split-Path -Parent $SCRIPT_DIR

# Archivos PID
$BACKEND_PID_FILE = Join-Path $PROJECT_ROOT ".backend.pid"
$FRONTEND_PID_FILE = Join-Path $PROJECT_ROOT ".frontend.pid"

$stopped = $false

# =============================================================================
# DETENER BACKEND
# =============================================================================

Write-Host "[1/2] Deteniendo Backend..." -ForegroundColor Yellow

if (Test-Path $BACKEND_PID_FILE) {
    $backend_pid = Get-Content $BACKEND_PID_FILE
    $backend_process = Get-Process -Id $backend_pid -ErrorAction SilentlyContinue

    if ($backend_process) {
        Write-Host "  [*] Deteniendo proceso Backend (PID: $backend_pid)..." -ForegroundColor Gray

        # Intentar detener el proceso y sus hijos
        try {
            # Obtener procesos hijos
            $children = Get-CimInstance Win32_Process | Where-Object { $_.ParentProcessId -eq $backend_pid }

            # Detener proceso principal
            Stop-Process -Id $backend_pid -Force -ErrorAction Stop

            # Detener procesos hijos
            foreach ($child in $children) {
                Stop-Process -Id $child.ProcessId -Force -ErrorAction SilentlyContinue
            }

            Write-Host "  [OK] Backend detenido" -ForegroundColor Green
            $stopped = $true
        } catch {
            Write-Host "  [!] Error deteniendo Backend: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "  [!] Proceso Backend no encontrado (ya estaba detenido)" -ForegroundColor Yellow
    }

    Remove-Item $BACKEND_PID_FILE -Force -ErrorAction SilentlyContinue
} else {
    Write-Host "  [!] Backend no está ejecutándose" -ForegroundColor Yellow
}

# =============================================================================
# DETENER FRONTEND
# =============================================================================

Write-Host ""
Write-Host "[2/2] Deteniendo Frontend..." -ForegroundColor Yellow

if (Test-Path $FRONTEND_PID_FILE) {
    $frontend_pid = Get-Content $FRONTEND_PID_FILE
    $frontend_process = Get-Process -Id $frontend_pid -ErrorAction SilentlyContinue

    if ($frontend_process) {
        Write-Host "  [*] Deteniendo proceso Frontend (PID: $frontend_pid)..." -ForegroundColor Gray

        try {
            # Obtener procesos hijos
            $children = Get-CimInstance Win32_Process | Where-Object { $_.ParentProcessId -eq $frontend_pid }

            # Detener proceso principal
            Stop-Process -Id $frontend_pid -Force -ErrorAction Stop

            # Detener procesos hijos (incluye Vite y Node)
            foreach ($child in $children) {
                Stop-Process -Id $child.ProcessId -Force -ErrorAction SilentlyContinue
            }

            Write-Host "  [OK] Frontend detenido" -ForegroundColor Green
            $stopped = $true
        } catch {
            Write-Host "  [!] Error deteniendo Frontend: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "  [!] Proceso Frontend no encontrado (ya estaba detenido)" -ForegroundColor Yellow
    }

    Remove-Item $FRONTEND_PID_FILE -Force -ErrorAction SilentlyContinue
} else {
    Write-Host "  [!] Frontend no está ejecutándose" -ForegroundColor Yellow
}

# =============================================================================
# LIMPIEZA ADICIONAL
# =============================================================================

Write-Host ""
Write-Host "Limpiando procesos residuales..." -ForegroundColor Gray

# Buscar y matar procesos de uvicorn en puerto 8000
$uvicorn_processes = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($pid in $uvicorn_processes) {
    if ($pid) {
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        Write-Host "  [*] Proceso uvicorn detenido (PID: $pid)" -ForegroundColor Gray
        $stopped = $true
    }
}

# Buscar y matar procesos de vite/node en puerto 5173
$vite_processes = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($pid in $vite_processes) {
    if ($pid) {
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        Write-Host "  [*] Proceso vite/node detenido (PID: $pid)" -ForegroundColor Gray
        $stopped = $true
    }
}

# Eliminar scripts temporales
$temp_backend_script = Join-Path $PROJECT_ROOT "backend\run_backend.ps1"
$temp_frontend_script = Join-Path $PROJECT_ROOT "frontend\run_frontend.ps1"

if (Test-Path $temp_backend_script) {
    Remove-Item $temp_backend_script -Force -ErrorAction SilentlyContinue
}

if (Test-Path $temp_frontend_script) {
    Remove-Item $temp_frontend_script -Force -ErrorAction SilentlyContinue
}

# =============================================================================
# RESUMEN
# =============================================================================

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
if ($stopped) {
    Write-Host "  SERVICIOS DETENIDOS" -ForegroundColor Green
} else {
    Write-Host "  NO HAY SERVICIOS EJECUTÁNDOSE" -ForegroundColor Yellow
}
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
