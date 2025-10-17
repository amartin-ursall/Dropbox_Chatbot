# ============================================================================
# SCRIPT DE DEPLOYMENT COMPLETO PARA IIS
# Dropbox AI Organizer - URSALL System
# ============================================================================
# Este script realiza un deployment completo:
# - Importa certificado SSL desde el Escritorio
# - Instala componentes de IIS
# - Despliega backend como servicio Windows
# - Despliega frontend en IIS
# - Configura bindings SSL
# ============================================================================

param(
    [string]$Domain = "dropboxaiorganizer.com",
    [string]$CertPath = "$env:USERPROFILE\Desktop\cert.pfx",
    [string]$CertPassword = "MGS-SSL"
)

# Colores
function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "  $Message" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
}

function Write-Info {
    param([string]$Message)
    Write-Host "  $Message" -ForegroundColor Gray
}

function Write-Success {
    param([string]$Message)
    Write-Host "  ✓ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "  ⚠ $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "  ✗ $Message" -ForegroundColor Red
}

# Banner
Clear-Host
Write-Host ""
Write-Host "██████╗ ██████╗  ██████╗ ██████╗ ██████╗  ██████╗ ██╗  ██╗" -ForegroundColor Cyan
Write-Host "██╔══██╗██╔══██╗██╔═══██╗██╔══██╗██╔══██╗██╔═══██╗╚██╗██╔╝" -ForegroundColor Cyan
Write-Host "██║  ██║██████╔╝██║   ██║██████╔╝██████╔╝██║   ██║ ╚███╔╝ " -ForegroundColor Cyan
Write-Host "██║  ██║██╔══██╗██║   ██║██╔═══╝ ██╔══██╗██║   ██║ ██╔██╗ " -ForegroundColor Cyan
Write-Host "██████╔╝██║  ██║╚██████╔╝██║     ██████╔╝╚██████╔╝██╔╝ ██╗" -ForegroundColor Cyan
Write-Host "╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═════╝  ╚═════╝ ╚═╝  ╚═╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "           AI ORGANIZER - DEPLOYMENT COMPLETO" -ForegroundColor White
Write-Host "                URSALL Legal System" -ForegroundColor Gray
Write-Host ""

# Verificar permisos de administrador
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Error-Custom "Este script DEBE ejecutarse como Administrador"
    Write-Host ""
    Write-Host "Click derecho en PowerShell → Ejecutar como Administrador" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Success "Ejecutando como Administrador"
Write-Info "Dominio: $Domain"
Write-Info "Certificado: $CertPath"
Write-Host ""

# Verificar que existe el certificado
if (-not (Test-Path $CertPath)) {
    Write-Error-Custom "No se encuentra el certificado en: $CertPath"
    Write-Host ""
    $customPath = Read-Host "Ingresa la ruta completa del certificado .pfx"
    if (-not (Test-Path $customPath)) {
        Write-Error-Custom "Ruta invalida. Abortando."
        exit 1
    }
    $CertPath = $customPath
}

Write-Success "Certificado encontrado"

# ============================================================================
# PASO 1: IMPORTAR CERTIFICADO SSL
# ============================================================================

Write-Step "PASO 1/7: Importando Certificado SSL"

try {
    $securePwd = ConvertTo-SecureString -String $CertPassword -Force -AsPlainText

    # Importar certificado
    $cert = Import-PfxCertificate -FilePath $CertPath `
                                   -CertStoreLocation Cert:\LocalMachine\My `
                                   -Password $securePwd `
                                   -Exportable

    Write-Success "Certificado importado exitosamente"
    Write-Info "Thumbprint: $($cert.Thumbprint)"
    Write-Info "Subject: $($cert.Subject)"
    Write-Info "Valido hasta: $($cert.NotAfter)"

    # Guardar thumbprint para uso posterior
    $certThumbprint = $cert.Thumbprint

} catch {
    Write-Error-Custom "Error al importar certificado: $($_.Exception.Message)"
    Write-Warning "Verifica que la contraseña sea correcta: $CertPassword"
    exit 1
}

# ============================================================================
# PASO 2: INSTALAR COMPONENTES DE IIS
# ============================================================================

Write-Step "PASO 2/7: Instalando Componentes de IIS"

try {
    # Verificar si IIS ya está instalado
    $iisFeature = Get-WindowsFeature -Name Web-Server -ErrorAction SilentlyContinue

    if ($iisFeature -and $iisFeature.Installed) {
        Write-Success "IIS ya está instalado"
    } else {
        Write-Info "Instalando IIS con características necesarias..."

        Install-WindowsFeature -Name Web-Server -IncludeManagementTools -ErrorAction Stop | Out-Null
        Install-WindowsFeature -Name Web-WebSockets -ErrorAction SilentlyContinue | Out-Null
        Install-WindowsFeature -Name Web-App-Dev -ErrorAction SilentlyContinue | Out-Null
        Install-WindowsFeature -Name Web-Net-Ext45 -ErrorAction SilentlyContinue | Out-Null
        Install-WindowsFeature -Name Web-Asp-Net45 -ErrorAction SilentlyContinue | Out-Null

        Write-Success "IIS instalado correctamente"
    }

    # Importar módulo de IIS
    Import-Module WebAdministration -ErrorAction Stop
    Write-Success "Módulo WebAdministration cargado"

} catch {
    Write-Error-Custom "Error instalando IIS: $($_.Exception.Message)"
    Write-Warning "Puede que necesites instalar los roles manualmente desde Server Manager"
}

# Verificar/Instalar URL Rewrite
Write-Info "Verificando URL Rewrite Module..."
$urlRewriteInstalled = Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\IIS Extensions\URL Rewrite\*" -ErrorAction SilentlyContinue

if (-not $urlRewriteInstalled) {
    Write-Warning "URL Rewrite no está instalado"
    Write-Info "Descarga e instala manualmente desde:"
    Write-Info "https://www.iis.net/downloads/microsoft/url-rewrite"
} else {
    Write-Success "URL Rewrite ya instalado"
}

# Verificar/Instalar ARR
Write-Info "Verificando Application Request Routing (ARR)..."
$arrInstalled = Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\IIS Extensions\Application Request Routing\*" -ErrorAction SilentlyContinue

if (-not $arrInstalled) {
    Write-Warning "ARR no está instalado"
    Write-Info "Descarga e instala manualmente desde:"
    Write-Info "https://www.iis.net/downloads/microsoft/application-request-routing"
} else {
    Write-Success "ARR ya instalado"
}

# ============================================================================
# PASO 3: CREAR ESTRUCTURA DE CARPETAS
# ============================================================================

Write-Step "PASO 3/7: Creando Estructura de Carpetas"

$deployPath = "C:\inetpub\wwwroot\dropbox-organizer"
$frontendPath = "$deployPath\frontend"
$backendPath = "$deployPath\backend"
$logsPath = "$deployPath\logs"

try {
    New-Item -ItemType Directory -Path $deployPath -Force | Out-Null
    New-Item -ItemType Directory -Path $frontendPath -Force | Out-Null
    New-Item -ItemType Directory -Path $backendPath -Force | Out-Null
    New-Item -ItemType Directory -Path $logsPath -Force | Out-Null

    Write-Success "Estructura de carpetas creada en: $deployPath"

} catch {
    Write-Error-Custom "Error creando carpetas: $($_.Exception.Message)"
    exit 1
}

# ============================================================================
# PASO 4: DESPLEGAR BACKEND
# ============================================================================

Write-Step "PASO 4/7: Desplegando Backend"

$sourceBackend = "$PSScriptRoot\..\backend"

if (-not (Test-Path $sourceBackend)) {
    Write-Error-Custom "No se encuentra el directorio backend en: $sourceBackend"
    exit 1
}

try {
    Write-Info "Copiando archivos del backend..."

    # Copiar archivos excluyendo venv, pycache, etc.
    $excludeDirs = @("venv", "__pycache__", ".pytest_cache", "tests")

    Get-ChildItem -Path $sourceBackend -Recurse | Where-Object {
        $exclude = $false
        foreach ($dir in $excludeDirs) {
            if ($_.FullName -like "*\$dir\*") {
                $exclude = $true
                break
            }
        }
        -not $exclude
    } | ForEach-Object {
        $dest = $_.FullName.Replace($sourceBackend, $backendPath)
        if ($_.PSIsContainer) {
            New-Item -ItemType Directory -Path $dest -Force | Out-Null
        } else {
            if ($_.Name -ne ".env") {  # No sobrescribir .env si ya existe
                Copy-Item -Path $_.FullName -Destination $dest -Force
            } elseif (-not (Test-Path "$backendPath\.env")) {
                Copy-Item -Path $_.FullName -Destination $dest -Force
            }
        }
    }

    Write-Success "Archivos del backend copiados"

    # Crear entorno virtual
    Write-Info "Creando entorno virtual de Python..."

    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCmd) {
        Write-Error-Custom "Python no está instalado o no está en PATH"
        exit 1
    }

    Set-Location $backendPath
    & python -m venv venv | Out-Null

    Write-Success "Entorno virtual creado"

    # Instalar dependencias
    Write-Info "Instalando dependencias de Python..."
    & ".\venv\Scripts\pip.exe" install -r requirements.txt --quiet

    Write-Success "Dependencias instaladas"

    # Configurar archivo .env
    if (Test-Path "$backendPath\.env") {
        Write-Success "Archivo .env ya existe"
        Write-Warning "Verifica que contenga las credenciales correctas"
        Write-Info "FRONTEND_URL=https://$Domain"
        Write-Info "DROPBOX_REDIRECT_URI=https://$Domain/auth/dropbox/callback"
    } else {
        Write-Warning "Creando archivo .env desde plantilla..."

        if (Test-Path "$backendPath\.env.example") {
            Copy-Item "$backendPath\.env.example" "$backendPath\.env"
        }

        # Actualizar valores en .env
        $envLines = Get-Content "$backendPath\.env"
        $newEnvLines = @()
        foreach ($line in $envLines) {
            if ($line -match "^FRONTEND_URL=") {
                $newEnvLines += "FRONTEND_URL=https://$Domain"
            } elseif ($line -match "^DROPBOX_REDIRECT_URI=") {
                $newEnvLines += "DROPBOX_REDIRECT_URI=https://$Domain/auth/dropbox/callback"
            } else {
                $newEnvLines += $line
            }
        }
        $newEnvLines | Set-Content "$backendPath\.env"

        Write-Warning "IMPORTANTE: Edita $backendPath\.env con tus credenciales:"
        Write-Info "- DROPBOX_APP_KEY"
        Write-Info "- DROPBOX_APP_SECRET"
        Write-Info "- GEMINI_API_KEY"
    }

} catch {
    Write-Error-Custom "Error desplegando backend: $($_.Exception.Message)"
    exit 1
}

# Instalar backend como servicio con NSSM
Write-Info "Instalando backend como servicio Windows..."

try {
    # Verificar si NSSM está instalado
    $nssmPath = "C:\Windows\System32\nssm.exe"

    if (-not (Test-Path $nssmPath)) {
        Write-Info "Descargando NSSM..."

        $nssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
        $nssmZip = "$env:TEMP\nssm.zip"
        $nssmExtract = "$env:TEMP\nssm"

        Invoke-WebRequest -Uri $nssmUrl -OutFile $nssmZip -UseBasicParsing
        Expand-Archive -Path $nssmZip -DestinationPath $nssmExtract -Force

        Copy-Item "$nssmExtract\nssm-2.24\win64\nssm.exe" -Destination $nssmPath -Force

        Remove-Item $nssmZip -Force -ErrorAction SilentlyContinue
        Remove-Item $nssmExtract -Recurse -Force -ErrorAction SilentlyContinue

        Write-Success "NSSM instalado"
    } else {
        Write-Success "NSSM ya está instalado"
    }

    # Verificar si el servicio ya existe
    $service = Get-Service -Name "DropboxBackend" -ErrorAction SilentlyContinue

    if ($service) {
        Write-Info "Servicio DropboxBackend ya existe, recreando..."
        Stop-Service -Name "DropboxBackend" -Force -ErrorAction SilentlyContinue
        & nssm remove DropboxBackend confirm
        Start-Sleep -Seconds 2
    }

    # Instalar servicio
    $pythonExe = "$backendPath\venv\Scripts\python.exe"
    $appParams = "-m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info"

    & nssm install DropboxBackend $pythonExe $appParams
    & nssm set DropboxBackend AppDirectory $backendPath
    & nssm set DropboxBackend AppStdout "$logsPath\backend-stdout.log"
    & nssm set DropboxBackend AppStderr "$logsPath\backend-stderr.log"
    & nssm set DropboxBackend DisplayName "Dropbox AI Organizer - Backend"
    & nssm set DropboxBackend Description "Backend API para Dropbox AI Organizer (URSALL Legal System)"
    & nssm set DropboxBackend Start SERVICE_AUTO_START

    # Iniciar servicio
    Start-Service -Name "DropboxBackend"

    Write-Success "Servicio DropboxBackend instalado e iniciado"

    # Esperar un momento para que inicie
    Start-Sleep -Seconds 3

    # Verificar que está corriendo
    $serviceStatus = Get-Service -Name "DropboxBackend"
    if ($serviceStatus.Status -eq "Running") {
        Write-Success "Backend está corriendo correctamente"
    } else {
        Write-Warning "Backend no está corriendo. Verifica los logs en: $logsPath"
    }

} catch {
    Write-Error-Custom "Error instalando servicio backend: $($_.Exception.Message)"
}

# ============================================================================
# PASO 5: DESPLEGAR FRONTEND
# ============================================================================

Write-Step "PASO 5/7: Desplegando Frontend"

$sourceFrontend = "$PSScriptRoot\..\frontend"

if (-not (Test-Path $sourceFrontend)) {
    Write-Error-Custom "No se encuentra el directorio frontend en: $sourceFrontend"
    exit 1
}

try {
    Write-Info "Compilando frontend para producción..."

    Set-Location $sourceFrontend

    # Verificar Node.js
    $nodeCmd = Get-Command node -ErrorAction SilentlyContinue
    if (-not $nodeCmd) {
        Write-Error-Custom "Node.js no está instalado o no está en PATH"
        exit 1
    }

    # Instalar dependencias si no existen
    if (-not (Test-Path "$sourceFrontend\node_modules")) {
        Write-Info "Instalando dependencias de Node.js..."
        & npm install
    }

    # Build producción
    Write-Info "Ejecutando npm run build..."
    & npm run build

    if (-not (Test-Path "$sourceFrontend\dist")) {
        Write-Error-Custom "Error en build: no se generó carpeta dist"
        exit 1
    }

    Write-Success "Frontend compilado exitosamente"

    # Copiar archivos compilados
    Write-Info "Copiando archivos a IIS..."
    Copy-Item -Path "$sourceFrontend\dist\*" -Destination $frontendPath -Recurse -Force

    Write-Success "Archivos del frontend copiados"

    # Copiar web.config
    if (Test-Path "$PSScriptRoot\web.config") {
        Copy-Item "$PSScriptRoot\web.config" -Destination "$frontendPath\web.config" -Force
        Write-Success "web.config copiado"
    } else {
        Write-Warning "No se encontró web.config en deployment/"
    }

} catch {
    Write-Error-Custom "Error desplegando frontend: $($_.Exception.Message)"
    exit 1
}

# ============================================================================
# PASO 6: CONFIGURAR SITIO EN IIS
# ============================================================================

Write-Step "PASO 6/7: Configurando Sitio en IIS"

try {
    Import-Module WebAdministration -ErrorAction Stop

    # Verificar si el sitio ya existe
    $siteName = "DropboxOrganizer"
    $existingSite = Get-Website -Name $siteName -ErrorAction SilentlyContinue

    if ($existingSite) {
        Write-Info "Sitio $siteName ya existe, eliminando..."
        Remove-Website -Name $siteName
        Start-Sleep -Seconds 2
    }

    # Crear nuevo sitio
    Write-Info "Creando sitio web en IIS..."

    New-Website -Name $siteName `
                -PhysicalPath $frontendPath `
                -Port 80 `
                -HostHeader $Domain `
                -Force | Out-Null

    Write-Success "Sitio IIS creado"

    # Agregar binding HTTPS
    Write-Info "Configurando binding HTTPS con certificado..."

    # Remover binding HTTPS existente si existe
    $httpsBinding = Get-WebBinding -Name $siteName -Protocol "https" -Port 443 -ErrorAction SilentlyContinue
    if ($httpsBinding) {
        Remove-WebBinding -Name $siteName -Protocol "https" -Port 443
    }

    # Crear nuevo binding HTTPS
    New-WebBinding -Name $siteName -Protocol "https" -Port 443 -HostHeader $Domain -SslFlags 0

    # Asociar certificado al binding
    $binding = Get-WebBinding -Name $siteName -Protocol "https" -Port 443
    $binding.AddSslCertificate($certThumbprint, "my")

    Write-Success "Binding HTTPS configurado con certificado"

    # Configurar permisos
    Write-Info "Configurando permisos..."
    & icacls $deployPath /grant "IIS_IUSRS:(OI)(CI)RX" /T | Out-Null

    Write-Success "Permisos configurados"

    # Iniciar sitio
    Start-Website -Name $siteName
    Write-Success "Sitio web iniciado"

} catch {
    Write-Error-Custom "Error configurando IIS: $($_.Exception.Message)"
    Write-Warning "Puede que necesites configurar el sitio manualmente en IIS Manager"
}

# ============================================================================
# PASO 7: VERIFICACIÓN FINAL
# ============================================================================

Write-Step "PASO 7/7: Verificación Final"

try {
    # Verificar backend
    Write-Info "Verificando backend en http://localhost:8000/health..."

    Start-Sleep -Seconds 2

    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Success "Backend respondiendo correctamente"
        }
    } catch {
        Write-Warning "Backend no responde. Verifica logs en: $logsPath\backend-stderr.log"
    }

    # Verificar frontend
    Write-Info "Verificando sitio IIS..."

    $site = Get-Website -Name "DropboxOrganizer"
    if ($site.State -eq "Started") {
        Write-Success "Sitio IIS está corriendo"
    } else {
        Write-Warning "Sitio IIS no está iniciado"
    }

    # Verificar bindings
    Write-Info "Bindings configurados:"
    $bindings = Get-WebBinding -Name "DropboxOrganizer"
    foreach ($b in $bindings) {
        Write-Info "  - $($b.protocol)://$($b.bindingInformation)"
    }

} catch {
    Write-Warning "Error en verificación: $($_.Exception.Message)"
}

# ============================================================================
# RESUMEN FINAL
# ============================================================================

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  ✓ DEPLOYMENT COMPLETADO" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

Write-Host "Tu aplicación está desplegada en:" -ForegroundColor White
Write-Host "  • Frontend: https://$Domain" -ForegroundColor Cyan
Write-Host "  • Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  • API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

Write-Host "Archivos desplegados en:" -ForegroundColor White
Write-Host "  • $deployPath" -ForegroundColor Gray
Write-Host ""

Write-Host "Logs del backend:" -ForegroundColor White
Write-Host "  • $logsPath\backend-stdout.log" -ForegroundColor Gray
Write-Host "  • $logsPath\backend-stderr.log" -ForegroundColor Gray
Write-Host ""

Write-Host "IMPORTANTE - Pasos siguientes:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Editar archivo .env con tus credenciales:" -ForegroundColor White
Write-Host "   notepad $backendPath\.env" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Configurar Dropbox App Console:" -ForegroundColor White
Write-Host "   - https://www.dropbox.com/developers/apps" -ForegroundColor Cyan
Write-Host "   - Redirect URI: https://$Domain/auth/dropbox/callback" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Reiniciar backend después de editar .env:" -ForegroundColor White
Write-Host "   Restart-Service DropboxBackend" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Agregar $Domain al archivo hosts:" -ForegroundColor White
Write-Host "   C:\Windows\System32\drivers\etc\hosts" -ForegroundColor Cyan
Write-Host "   127.0.0.1 $Domain" -ForegroundColor Gray
Write-Host ""

Write-Host "Comandos útiles:" -ForegroundColor White
Write-Host "  • Ver servicio: Get-Service DropboxBackend" -ForegroundColor Gray
Write-Host "  • Reiniciar backend: Restart-Service DropboxBackend" -ForegroundColor Gray
Write-Host "  • Reiniciar IIS: iisreset" -ForegroundColor Gray
Write-Host "  • Ver logs: Get-Content $logsPath\backend-stdout.log -Wait" -ForegroundColor Gray
Write-Host ""

Write-Host "¡Deployment finalizado exitosamente! 🚀" -ForegroundColor Green
Write-Host ""
