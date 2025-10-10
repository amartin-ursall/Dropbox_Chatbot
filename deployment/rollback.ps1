# ============================================================================
# Script de Rollback
# Dropbox AI Organizer - URSALL System
# ============================================================================
# Este script restaura una versión anterior de la aplicación desde un backup
# ============================================================================

param(
    [Parameter(Mandatory=$false)]
    [string]$BackupPath = "",
    [string]$InstallPath = "C:\inetpub\wwwroot\dropbox-organizer",
    [string]$BackupsRoot = "C:\backups\dropbox-organizer"
)

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Rollback - Dropbox AI Organizer" -ForegroundColor Cyan
Write-Host "  URSALL Legal System" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que se ejecuta como administrador
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: Este script debe ejecutarse como Administrador" -ForegroundColor Red
    exit 1
}

# Si no se especificó backup, listar disponibles
if (-not $BackupPath) {
    Write-Host "Backups disponibles:" -ForegroundColor White
    Write-Host ""

    if (Test-Path $BackupsRoot) {
        $backups = Get-ChildItem -Path $BackupsRoot -Directory | Sort-Object Name -Descending

        if ($backups.Count -eq 0) {
            Write-Host "  No hay backups disponibles en: $BackupsRoot" -ForegroundColor Yellow
            exit 1
        }

        for ($i = 0; $i -lt $backups.Count; $i++) {
            $backup = $backups[$i]
            $size = (Get-ChildItem -Path $backup.FullName -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
            Write-Host "  [$i] $($backup.Name) - $([math]::Round($size, 2)) MB" -ForegroundColor Gray
        }

        Write-Host ""
        $selection = Read-Host "Selecciona el número de backup a restaurar (o 'q' para cancelar)"

        if ($selection -eq 'q') {
            Write-Host "Rollback cancelado" -ForegroundColor Yellow
            exit 0
        }

        $selectedIndex = [int]$selection
        if ($selectedIndex -lt 0 -or $selectedIndex -ge $backups.Count) {
            Write-Host "ERROR: Selección inválida" -ForegroundColor Red
            exit 1
        }

        $BackupPath = $backups[$selectedIndex].FullName
    } else {
        Write-Host "  No se encontró directorio de backups: $BackupsRoot" -ForegroundColor Red
        exit 1
    }
}

# Verificar que existe el backup
if (-not (Test-Path $BackupPath)) {
    Write-Host "ERROR: No se encontró el backup: $BackupPath" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Configuración de Rollback:" -ForegroundColor White
Write-Host "  - Backup: $BackupPath" -ForegroundColor Gray
Write-Host "  - Destino: $InstallPath" -ForegroundColor Gray
Write-Host ""

# Advertencia
Write-Host "⚠ ADVERTENCIA: Esta operación sobrescribirá la versión actual" -ForegroundColor Yellow
Write-Host ""
$confirm = Read-Host "¿Continuar con el rollback? (escribe 'SI' para confirmar)"

if ($confirm -ne 'SI') {
    Write-Host "Rollback cancelado" -ForegroundColor Yellow
    exit 0
}

# ============================================================================
# PASO 1: Detener servicios
# ============================================================================

Write-Host ""
Write-Host "[1/4] Deteniendo servicios..." -ForegroundColor Green

$backendService = Get-Service -Name "DropboxBackend" -ErrorAction SilentlyContinue

if ($backendService -and $backendService.Status -eq "Running") {
    Stop-Service -Name "DropboxBackend" -Force
    Start-Sleep -Seconds 2
    Write-Host "  ✓ Backend detenido" -ForegroundColor Green
}

# ============================================================================
# PASO 2: Crear backup de la versión actual (por si acaso)
# ============================================================================

Write-Host ""
Write-Host "[2/4] Creando backup de la versión actual..." -ForegroundColor Green

$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$preRollbackBackup = "$BackupsRoot\pre-rollback_$timestamp"

try {
    New-Item -ItemType Directory -Path $preRollbackBackup -Force | Out-Null

    Copy-Item "$InstallPath\backend" `
              -Destination "$preRollbackBackup\backend" `
              -Recurse -Force `
              -Exclude "venv","__pycache__","logs"

    Copy-Item "$InstallPath\frontend" `
              -Destination "$preRollbackBackup\frontend" `
              -Recurse -Force

    Write-Host "  ✓ Backup pre-rollback creado: $preRollbackBackup" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Error creando backup pre-rollback: $($_.Exception.Message)" -ForegroundColor Yellow
}

# ============================================================================
# PASO 3: Restaurar archivos desde backup
# ============================================================================

Write-Host ""
Write-Host "[3/4] Restaurando archivos desde backup..." -ForegroundColor Green

try {
    # Restaurar backend
    if (Test-Path "$BackupPath\backend") {
        Write-Host "  Restaurando backend..." -ForegroundColor Gray
        Remove-Item "$InstallPath\backend\*" -Recurse -Force -Exclude "venv",".env","logs"
        Copy-Item "$BackupPath\backend\*" `
                  -Destination "$InstallPath\backend\" `
                  -Recurse -Force
        Write-Host "  ✓ Backend restaurado" -ForegroundColor Green
    }

    # Restaurar frontend
    if (Test-Path "$BackupPath\frontend") {
        Write-Host "  Restaurando frontend..." -ForegroundColor Gray
        Remove-Item "$InstallPath\frontend\*" -Recurse -Force
        Copy-Item "$BackupPath\frontend\*" `
                  -Destination "$InstallPath\frontend\" `
                  -Recurse -Force
        Write-Host "  ✓ Frontend restaurado" -ForegroundColor Green
    }

    # Restaurar .env (preguntar antes)
    if (Test-Path "$BackupPath\.env") {
        $restoreEnv = Read-Host "  ¿Restaurar también el archivo .env? (s/n)"
        if ($restoreEnv -eq 's' -or $restoreEnv -eq 'S') {
            Copy-Item "$BackupPath\.env" `
                      -Destination "$InstallPath\backend\.env" `
                      -Force
            Write-Host "  ✓ .env restaurado" -ForegroundColor Green
        } else {
            Write-Host "  ℹ .env NO restaurado (se mantiene el actual)" -ForegroundColor Cyan
        }
    }

    Write-Host "  ✓ Archivos restaurados correctamente" -ForegroundColor Green

} catch {
    Write-Host "  ✗ Error restaurando archivos: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# ============================================================================
# PASO 4: Reiniciar servicios
# ============================================================================

Write-Host ""
Write-Host "[4/4] Reiniciando servicios..." -ForegroundColor Green

# Reiniciar backend
if ($backendService) {
    Start-Service -Name "DropboxBackend"
    Start-Sleep -Seconds 3

    $service = Get-Service -Name "DropboxBackend"
    if ($service.Status -eq "Running") {
        Write-Host "  ✓ Backend iniciado" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Backend no se inició" -ForegroundColor Red
    }
}

# Reiniciar IIS
iisreset /noforce | Out-Null
Write-Host "  ✓ IIS reiniciado" -ForegroundColor Green

# ============================================================================
# VERIFICACIÓN
# ============================================================================

Write-Host ""
Write-Host "Verificando funcionamiento..." -ForegroundColor White

Start-Sleep -Seconds 3

# Verificar backend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✓ Backend funcionando" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✗ Backend no responde" -ForegroundColor Red
}

# Verificar frontend
try {
    $response = Invoke-WebRequest -Uri "http://localhost" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✓ Frontend funcionando" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✗ Frontend no responde" -ForegroundColor Red
}

# ============================================================================
# RESUMEN
# ============================================================================

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  ✓ Rollback Completado" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Información:" -ForegroundColor White
Write-Host "  - Versión restaurada desde: $BackupPath" -ForegroundColor Gray
Write-Host "  - Backup de versión anterior: $preRollbackBackup" -ForegroundColor Gray
Write-Host ""

Write-Host "Si el rollback causó problemas, puedes volver a la versión anterior con:" -ForegroundColor Yellow
Write-Host "  .\rollback.ps1 -BackupPath '$preRollbackBackup'" -ForegroundColor Gray
Write-Host ""

Write-Host "Rollback completado en: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host ""
