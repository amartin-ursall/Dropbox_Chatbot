# ============================================================================
# Script de Deployment Completo
# Dropbox AI Organizer - URSALL System
# ============================================================================
# Este script automatiza todo el proceso de deployment:
# 1. Compila el frontend
# 2. Copia archivos al servidor de producción
# 3. Actualiza configuración
# 4. Reinicia servicios
# ============================================================================

param(
    [string]$Domain = "",
    [string]$InstallPath = "C:\inetpub\wwwroot\dropbox-organizer",
    [switch]$SkipBuild = $false,
    [switch]$SkipRestart = $false
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Deployment - Dropbox AI Organizer" -ForegroundColor Cyan
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

# Obtener rutas
$scriptPath = Split-Path -Parent $PSScriptRoot
$frontendPath = "$scriptPath\frontend"
$backendPath = "$scriptPath\backend"

# Solicitar dominio si no se especificó
if (-not $Domain) {
    $Domain = Read-Host "Ingresa tu dominio de producción (ej: dropboxorganizer.com)"
}

Write-Host "Configuración:" -ForegroundColor White
Write-Host "  - Dominio: $Domain" -ForegroundColor Gray
Write-Host "  - Ruta de instalación: $InstallPath" -ForegroundColor Gray
Write-Host ""

$confirm = Read-Host "¿Continuar con el deployment? (s/n)"
if ($confirm -ne 's' -and $confirm -ne 'S') {
    Write-Host "Deployment cancelado" -ForegroundColor Yellow
    exit 0
}

# ============================================================================
# PASO 1: Actualizar variables de entorno
# ============================================================================

Write-Host ""
Write-Host "[1/6] Actualizando variables de entorno..." -ForegroundColor Green

# Actualizar frontend .env.production
$frontendEnv = "$frontendPath\.env.production"
if (Test-Path $frontendEnv) {
    $content = Get-Content $frontendEnv
    $content = $content -replace 'VITE_BACKEND_URL=.*', "VITE_BACKEND_URL=https://$Domain"
    $content | Set-Content $frontendEnv
    Write-Host "  ✓ Frontend .env.production actualizado" -ForegroundColor Green
}

# ============================================================================
# PASO 2: Compilar frontend
# ============================================================================

if (-not $SkipBuild) {
    Write-Host ""
    Write-Host "[2/6] Compilando frontend..." -ForegroundColor Green

    Push-Location $frontendPath

    try {
        # Verificar que node está instalado
        $nodeCmd = Get-Command node -ErrorAction SilentlyContinue
        if (-not $nodeCmd) {
            throw "Node.js no encontrado. Instala desde https://nodejs.org/"
        }

        Write-Host "  Instalando dependencias..." -ForegroundColor Gray
        npm install

        if ($LASTEXITCODE -ne 0) {
            throw "Error instalando dependencias de frontend"
        }

        Write-Host "  Compilando para producción..." -ForegroundColor Gray
        npm run build

        if ($LASTEXITCODE -ne 0) {
            throw "Error compilando frontend"
        }

        Write-Host "  ✓ Frontend compilado correctamente" -ForegroundColor Green

    } catch {
        Write-Host "  ✗ Error compilando frontend: $($_.Exception.Message)" -ForegroundColor Red
        Pop-Location
        exit 1
    }

    Pop-Location
} else {
    Write-Host ""
    Write-Host "[2/6] Omitiendo compilación de frontend (--SkipBuild)" -ForegroundColor Yellow
}

# ============================================================================
# PASO 3: Detener servicios
# ============================================================================

Write-Host ""
Write-Host "[3/6] Deteniendo servicios..." -ForegroundColor Green

$backendService = Get-Service -Name "DropboxBackend" -ErrorAction SilentlyContinue

if ($backendService) {
    if ($backendService.Status -eq "Running") {
        Write-Host "  Deteniendo backend..." -ForegroundColor Gray
        Stop-Service -Name "DropboxBackend" -Force
        Start-Sleep -Seconds 2
        Write-Host "  ✓ Backend detenido" -ForegroundColor Green
    } else {
        Write-Host "  Backend ya estaba detenido" -ForegroundColor Gray
    }
} else {
    Write-Host "  ⚠ Servicio backend no encontrado (se instalará)" -ForegroundColor Yellow
}

# ============================================================================
# PASO 4: Copiar archivos
# ============================================================================

Write-Host ""
Write-Host "[4/6] Copiando archivos..." -ForegroundColor Green

# Crear directorios
New-Item -ItemType Directory -Path "$InstallPath\frontend" -Force | Out-Null
New-Item -ItemType Directory -Path "$InstallPath\backend" -Force | Out-Null
New-Item -ItemType Directory -Path "$InstallPath\logs" -Force | Out-Null

# Copiar frontend
Write-Host "  Copiando frontend..." -ForegroundColor Gray
$frontendDist = "$frontendPath\dist"

if (-not (Test-Path $frontendDist)) {
    Write-Host "  ✗ No se encontró carpeta dist/. Ejecuta: npm run build" -ForegroundColor Red
    exit 1
}

Copy-Item "$frontendDist\*" -Destination "$InstallPath\frontend\" -Recurse -Force
Write-Host "  ✓ Frontend copiado" -ForegroundColor Green

# Copiar web.config
Write-Host "  Copiando web.config..." -ForegroundColor Gray
Copy-Item "$scriptPath\deployment\web.config" -Destination "$InstallPath\frontend\web.config" -Force
Write-Host "  ✓ web.config copiado" -ForegroundColor Green

# Copiar backend (excluyendo venv, cache, etc.)
Write-Host "  Copiando backend..." -ForegroundColor Gray
$excludeDirs = @("venv", "__pycache__", ".pytest_cache", "tests")

Get-ChildItem -Path $backendPath -Exclude $excludeDirs | ForEach-Object {
    Copy-Item $_.FullName -Destination "$InstallPath\backend\" -Recurse -Force -Exclude ".env"
}
Write-Host "  ✓ Backend copiado" -ForegroundColor Green

# Copiar .env.production como .env si no existe
$prodEnv = "$InstallPath\backend\.env"
if (-not (Test-Path $prodEnv)) {
    Write-Host "  Copiando .env.production..." -ForegroundColor Gray
    Copy-Item "$backendPath\.env.production" -Destination $prodEnv -Force

    # Actualizar dominio en .env
    $envContent = Get-Content $prodEnv
    $envContent = $envContent -replace 'tudominio\.com', $Domain
    $envContent | Set-Content $prodEnv

    Write-Host "  ⚠ Archivo .env creado. DEBES CONFIGURAR LAS CREDENCIALES:" -ForegroundColor Yellow
    Write-Host "    - DROPBOX_APP_KEY" -ForegroundColor Gray
    Write-Host "    - DROPBOX_APP_SECRET" -ForegroundColor Gray
    Write-Host "    - GEMINI_API_KEY" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Editar con: notepad '$prodEnv'" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ .env ya existe (no se sobrescribe)" -ForegroundColor Green
}

# ============================================================================
# PASO 5: Configurar permisos
# ============================================================================

Write-Host ""
Write-Host "[5/6] Configurando permisos..." -ForegroundColor Green

try {
    icacls "$InstallPath" /grant "IIS_IUSRS:(OI)(CI)RX" /T /Q
    Write-Host "  ✓ Permisos configurados" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ No se pudieron configurar permisos automáticamente" -ForegroundColor Yellow
}

# ============================================================================
# PASO 6: Reiniciar servicios
# ============================================================================

Write-Host ""
Write-Host "[6/6] Reiniciando servicios..." -ForegroundColor Green

if (-not $SkipRestart) {
    # Iniciar backend
    if ($backendService) {
        Write-Host "  Iniciando backend..." -ForegroundColor Gray
        Start-Service -Name "DropboxBackend"
        Start-Sleep -Seconds 3

        $service = Get-Service -Name "DropboxBackend"
        if ($service.Status -eq "Running") {
            Write-Host "  ✓ Backend iniciado" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ Backend no se inició correctamente" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  ⚠ Servicio backend no instalado. Ejecuta: .\install-backend-service.ps1" -ForegroundColor Yellow
    }

    # Reiniciar IIS
    Write-Host "  Reiniciando IIS..." -ForegroundColor Gray
    iisreset /noforce
    Write-Host "  ✓ IIS reiniciado" -ForegroundColor Green
} else {
    Write-Host "  Omitiendo reinicio de servicios (--SkipRestart)" -ForegroundColor Yellow
}

# ============================================================================
# RESUMEN Y VERIFICACIÓN
# ============================================================================

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  ✓ Deployment Completado" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar health check
Write-Host "Verificando servicios..." -ForegroundColor White
Write-Host ""

# Backend
try {
    $healthUrl = "http://localhost:8000/health"
    $response = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✓ Backend funcionando (http://localhost:8000/health)" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✗ Backend no responde en http://localhost:8000/health" -ForegroundColor Red
    Write-Host "    Verifica logs: Get-Content '$InstallPath\logs\backend-stderr.log' -Tail 50" -ForegroundColor Gray
}

# Frontend
try {
    $frontendUrl = "http://localhost"
    $response = Invoke-WebRequest -Uri $frontendUrl -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✓ Frontend funcionando (http://localhost)" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✗ Frontend no responde en http://localhost" -ForegroundColor Red
}

Write-Host ""
Write-Host "Próximos pasos:" -ForegroundColor Yellow
Write-Host "  1. Configurar credenciales en: $InstallPath\backend\.env" -ForegroundColor Gray
Write-Host "  2. Reiniciar backend: Restart-Service DropboxBackend" -ForegroundColor Gray
Write-Host "  3. Instalar certificado SSL: .\install-ssl-certificate.ps1 -Domain $Domain" -ForegroundColor Gray
Write-Host "  4. Verificar HTTPS: https://$Domain" -ForegroundColor Gray
Write-Host "  5. Probar OAuth: https://$Domain → Iniciar sesión con Dropbox" -ForegroundColor Gray
Write-Host ""
Write-Host "URLs importantes:" -ForegroundColor White
Write-Host "  - Frontend:  https://$Domain" -ForegroundColor Gray
Write-Host "  - API Docs:  https://$Domain/docs" -ForegroundColor Gray
Write-Host "  - Health:    https://$Domain/health" -ForegroundColor Gray
Write-Host ""
