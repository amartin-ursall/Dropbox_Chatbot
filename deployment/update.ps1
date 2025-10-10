# ============================================================================
# Script de Actualización en Producción
# Dropbox AI Organizer - URSALL System
# ============================================================================
# Este script actualiza la aplicación en producción:
# 1. Hace backup de la versión actual
# 2. Actualiza código desde Git
# 3. Actualiza backend y frontend
# 4. Reinicia servicios
# 5. Verifica que funcione correctamente
# ============================================================================

param(
    [string]$InstallPath = "C:\inetpub\wwwroot\dropbox-organizer",
    [string]$BackupPath = "C:\backups\dropbox-organizer",
    [string]$ProjectPath = "C:\Users\amartin\Documents\Aplicativos\Dropbox_Chatbot",
    [switch]$SkipBackup = $false,
    [switch]$SkipGitPull = $false,
    [switch]$BackendOnly = $false,
    [switch]$FrontendOnly = $false
)

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Actualización - Dropbox AI Organizer" -ForegroundColor Cyan
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

# Verificar que existe instalación
if (-not (Test-Path $InstallPath)) {
    Write-Host "ERROR: No se encontró instalación en: $InstallPath" -ForegroundColor Red
    Write-Host "Ejecuta primero el script de deployment: .\deploy.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "Configuración:" -ForegroundColor White
Write-Host "  - Instalación: $InstallPath" -ForegroundColor Gray
Write-Host "  - Backups: $BackupPath" -ForegroundColor Gray
Write-Host "  - Proyecto: $ProjectPath" -ForegroundColor Gray
if ($BackendOnly) { Write-Host "  - Modo: SOLO BACKEND" -ForegroundColor Yellow }
if ($FrontendOnly) { Write-Host "  - Modo: SOLO FRONTEND" -ForegroundColor Yellow }
Write-Host ""

# ============================================================================
# PASO 1: Backup de la versión actual
# ============================================================================

if (-not $SkipBackup) {
    Write-Host "[1/7] Creando backup de la versión actual..." -ForegroundColor Green

    $timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
    $backupDir = "$BackupPath\$timestamp"

    try {
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

        # Backup del backend
        Write-Host "  Respaldando backend..." -ForegroundColor Gray
        Copy-Item "$InstallPath\backend" `
                  -Destination "$backupDir\backend" `
                  -Recurse -Force `
                  -Exclude "venv","__pycache__","logs"

        # Backup del frontend
        if (-not $BackendOnly) {
            Write-Host "  Respaldando frontend..." -ForegroundColor Gray
            Copy-Item "$InstallPath\frontend" `
                      -Destination "$backupDir\frontend" `
                      -Recurse -Force
        }

        # Backup del .env (importante!)
        Write-Host "  Respaldando .env..." -ForegroundColor Gray
        Copy-Item "$InstallPath\backend\.env" `
                  -Destination "$backupDir\.env" `
                  -Force

        Write-Host "  ✓ Backup creado en: $backupDir" -ForegroundColor Green

    } catch {
        Write-Host "  ⚠ Error creando backup: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host "  Continuando sin backup..." -ForegroundColor Yellow
    }
} else {
    Write-Host "[1/7] Omitiendo backup (--SkipBackup)" -ForegroundColor Yellow
}

# ============================================================================
# PASO 2: Actualizar código desde Git
# ============================================================================

if (-not $SkipGitPull) {
    Write-Host ""
    Write-Host "[2/7] Actualizando código desde Git..." -ForegroundColor Green

    Push-Location $ProjectPath

    try {
        # Verificar estado de Git
        Write-Host "  Verificando repositorio..." -ForegroundColor Gray
        git status --short

        # Ver última versión actual
        $currentCommit = git rev-parse --short HEAD
        Write-Host "  Versión actual: $currentCommit" -ForegroundColor Gray

        # Actualizar desde remoto
        Write-Host "  Descargando cambios..." -ForegroundColor Gray
        git pull origin master

        # Ver nueva versión
        $newCommit = git rev-parse --short HEAD
        Write-Host "  Nueva versión: $newCommit" -ForegroundColor Gray

        if ($currentCommit -eq $newCommit) {
            Write-Host "  ℹ Ya estás en la última versión" -ForegroundColor Cyan
        } else {
            Write-Host "  ✓ Código actualizado correctamente" -ForegroundColor Green

            # Mostrar cambios
            Write-Host ""
            Write-Host "  Cambios aplicados:" -ForegroundColor White
            git log --oneline "$currentCommit..$newCommit" | ForEach-Object {
                Write-Host "    - $_" -ForegroundColor Gray
            }
        }

    } catch {
        Write-Host "  ✗ Error actualizando desde Git: $($_.Exception.Message)" -ForegroundColor Red
        Pop-Location
        exit 1
    }

    Pop-Location
} else {
    Write-Host ""
    Write-Host "[2/7] Omitiendo actualización de Git (--SkipGitPull)" -ForegroundColor Yellow
}

# ============================================================================
# PASO 3: Detener servicio backend
# ============================================================================

Write-Host ""
Write-Host "[3/7] Deteniendo servicio backend..." -ForegroundColor Green

$backendService = Get-Service -Name "DropboxBackend" -ErrorAction SilentlyContinue

if ($backendService -and $backendService.Status -eq "Running") {
    Stop-Service -Name "DropboxBackend" -Force
    Start-Sleep -Seconds 2
    Write-Host "  ✓ Backend detenido" -ForegroundColor Green
} else {
    Write-Host "  Backend ya estaba detenido" -ForegroundColor Gray
}

# ============================================================================
# PASO 4: Actualizar Backend
# ============================================================================

if (-not $FrontendOnly) {
    Write-Host ""
    Write-Host "[4/7] Actualizando backend..." -ForegroundColor Green

    try {
        # Copiar archivos (preservar .env)
        Write-Host "  Copiando archivos..." -ForegroundColor Gray
        $excludeDirs = @("venv", "__pycache__", ".pytest_cache", "tests", "logs")

        Get-ChildItem -Path "$ProjectPath\backend" -Exclude $excludeDirs | ForEach-Object {
            Copy-Item $_.FullName `
                      -Destination "$InstallPath\backend\" `
                      -Recurse -Force `
                      -Exclude ".env"
        }

        # Verificar si hay nuevas dependencias
        $reqFile = "$InstallPath\backend\requirements.txt"
        if (Test-Path $reqFile) {
            Write-Host "  Verificando dependencias..." -ForegroundColor Gray

            Push-Location "$InstallPath\backend"

            & ".\venv\Scripts\activate.ps1"
            pip install -r requirements.txt --quiet
            deactivate

            Pop-Location

            Write-Host "  ✓ Dependencias actualizadas" -ForegroundColor Green
        }

        Write-Host "  ✓ Backend actualizado" -ForegroundColor Green

    } catch {
        Write-Host "  ✗ Error actualizando backend: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host ""
    Write-Host "[4/7] Omitiendo actualización de backend (--FrontendOnly)" -ForegroundColor Yellow
}

# ============================================================================
# PASO 5: Actualizar Frontend
# ============================================================================

if (-not $BackendOnly) {
    Write-Host ""
    Write-Host "[5/7] Actualizando frontend..." -ForegroundColor Green

    Push-Location "$ProjectPath\frontend"

    try {
        # Verificar si hay nuevas dependencias
        Write-Host "  Verificando dependencias..." -ForegroundColor Gray
        npm install --silent

        # Compilar para producción
        Write-Host "  Compilando para producción..." -ForegroundColor Gray
        npm run build

        if ($LASTEXITCODE -ne 0) {
            throw "Error compilando frontend"
        }

        # Copiar archivos compilados
        Write-Host "  Copiando archivos..." -ForegroundColor Gray
        Copy-Item ".\dist\*" `
                  -Destination "$InstallPath\frontend\" `
                  -Recurse -Force

        # Copiar web.config
        Copy-Item "$ProjectPath\deployment\web.config" `
                  -Destination "$InstallPath\frontend\web.config" `
                  -Force

        Write-Host "  ✓ Frontend actualizado" -ForegroundColor Green

    } catch {
        Write-Host "  ✗ Error actualizando frontend: $($_.Exception.Message)" -ForegroundColor Red
        Pop-Location
        exit 1
    }

    Pop-Location
} else {
    Write-Host ""
    Write-Host "[5/7] Omitiendo actualización de frontend (--BackendOnly)" -ForegroundColor Yellow
}

# ============================================================================
# PASO 6: Reiniciar servicios
# ============================================================================

Write-Host ""
Write-Host "[6/7] Reiniciando servicios..." -ForegroundColor Green

# Reiniciar backend
if ($backendService) {
    Write-Host "  Iniciando backend..." -ForegroundColor Gray
    Start-Service -Name "DropboxBackend"
    Start-Sleep -Seconds 3

    $service = Get-Service -Name "DropboxBackend"
    if ($service.Status -eq "Running") {
        Write-Host "  ✓ Backend iniciado" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Backend no se inició" -ForegroundColor Red
        Write-Host "  Ver logs: Get-Content '$InstallPath\logs\backend-stderr.log' -Tail 50" -ForegroundColor Yellow
    }
}

# Reiniciar IIS
if (-not $BackendOnly) {
    Write-Host "  Reiniciando IIS..." -ForegroundColor Gray
    iisreset /noforce | Out-Null
    Write-Host "  ✓ IIS reiniciado" -ForegroundColor Green
}

# ============================================================================
# PASO 7: Verificación
# ============================================================================

Write-Host ""
Write-Host "[7/7] Verificando funcionamiento..." -ForegroundColor Green

$allOk = $true

# Verificar backend
if (-not $FrontendOnly) {
    Start-Sleep -Seconds 2  # Dar tiempo a que inicie

    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✓ Backend funcionando" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ✗ Backend no responde" -ForegroundColor Red
        Write-Host "    URL: http://localhost:8000/health" -ForegroundColor Gray
        Write-Host "    Ver logs: Get-Content '$InstallPath\logs\backend-stderr.log' -Tail 50" -ForegroundColor Yellow
        $allOk = $false
    }
}

# Verificar frontend
if (-not $BackendOnly) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✓ Frontend funcionando" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ✗ Frontend no responde" -ForegroundColor Red
        Write-Host "    URL: http://localhost" -ForegroundColor Gray
        $allOk = $false
    }
}

# ============================================================================
# RESUMEN
# ============================================================================

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan

if ($allOk) {
    Write-Host "  ✓ Actualización Completada Exitosamente" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Actualización con Advertencias" -ForegroundColor Yellow
}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Información de rollback
if (-not $SkipBackup) {
    Write-Host "Información de Rollback:" -ForegroundColor White
    Write-Host "  Si algo salió mal, puedes restaurar con:" -ForegroundColor Gray
    Write-Host "  .\rollback.ps1 -BackupPath '$backupDir'" -ForegroundColor Yellow
    Write-Host ""
}

# Mostrar logs útiles
Write-Host "Comandos útiles:" -ForegroundColor White
Write-Host "  Ver logs backend:  Get-Content '$InstallPath\logs\backend-stdout.log' -Tail 50 -Wait" -ForegroundColor Gray
Write-Host "  Ver errores:       Get-Content '$InstallPath\logs\backend-stderr.log' -Tail 50" -ForegroundColor Gray
Write-Host "  Reiniciar backend: Restart-Service DropboxBackend" -ForegroundColor Gray
Write-Host "  Reiniciar IIS:     iisreset" -ForegroundColor Gray
Write-Host ""

# Leer dominio del .env para mostrar URL
$envFile = "$InstallPath\backend\.env"
if (Test-Path $envFile) {
    $envContent = Get-Content $envFile
    $frontendUrl = ($envContent | Select-String "^FRONTEND_URL=(.+)$").Matches.Groups[1].Value

    if ($frontendUrl) {
        Write-Host "Aplicación disponible en:" -ForegroundColor White
        Write-Host "  $frontendUrl" -ForegroundColor Cyan
        Write-Host ""
    }
}

Write-Host "Actualización completada en: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host ""
