# ====================================================================================================
# DEPLOYMENT SIMPLIFICADO PARA IIS - Dropbox AI Organizer
# ====================================================================================================

param(
    [string]$Domain = "dropboxaiorganizer.com",
    [string]$CertPath = "$env:USERPROFILE\Desktop\cert.pfx",
    [string]$CertPassword = "MGS-SSL"
)

Write-Host "Iniciando deployment..." -ForegroundColor Cyan
Write-Host "Dominio: $Domain"
Write-Host "Certificado: $CertPath"
Write-Host ""

# Verificar permisos de administrador
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Ejecuta como Administrador" -ForegroundColor Red
    exit 1
}

# ==========================
# 1. IMPORTAR CERTIFICADO
# ==========================
Write-Host "[1/7] Importando certificado SSL..." -ForegroundColor Green

try {
    $securePwd = ConvertTo-SecureString -String $CertPassword -Force -AsPlainText
    $cert = Import-PfxCertificate -FilePath $CertPath -CertStoreLocation Cert:\LocalMachine\My -Password $securePwd -Exportable
    $certThumbprint = $cert.Thumbprint
    Write-Host "OK - Certificado importado: $certThumbprint" -ForegroundColor Green
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# ==========================
# 2. INSTALAR IIS
# ==========================
Write-Host "[2/7] Verificando IIS..." -ForegroundColor Green

Import-Module ServerManager -ErrorAction SilentlyContinue

$iisInstalled = (Get-WindowsFeature -Name Web-Server -ErrorAction SilentlyContinue).Installed
if ($iisInstalled) {
    Write-Host "OK - IIS ya instalado" -ForegroundColor Green
} else {
    Write-Host "Instalando IIS..."
    Install-WindowsFeature -Name Web-Server -IncludeManagementTools | Out-Null
    Write-Host "OK - IIS instalado" -ForegroundColor Green
}

Import-Module WebAdministration -ErrorAction Stop

# ==========================
# 3. CREAR CARPETAS
# ==========================
Write-Host "[3/7] Creando estructura de carpetas..." -ForegroundColor Green

$deployPath = "C:\inetpub\wwwroot\dropbox-organizer"
$frontendPath = "$deployPath\frontend"
$backendPath = "$deployPath\backend"
$logsPath = "$deployPath\logs"

New-Item -ItemType Directory -Path $deployPath -Force | Out-Null
New-Item -ItemType Directory -Path $frontendPath -Force | Out-Null
New-Item -ItemType Directory -Path $backendPath -Force | Out-Null
New-Item -ItemType Directory -Path $logsPath -Force | Out-Null

Write-Host "OK - Carpetas creadas en: $deployPath" -ForegroundColor Green

# ==========================
# 4. COPIAR BACKEND
# ==========================
Write-Host "[4/7] Desplegando backend..." -ForegroundColor Green

$sourceBackend = "$PSScriptRoot\..\backend"

# Copiar archivos (excepto venv, pycache)
Get-ChildItem -Path $sourceBackend -Recurse | Where-Object {
    $_.FullName -notmatch "\\venv\\" -and
    $_.FullName -notmatch "\\__pycache__\\" -and
    $_.FullName -notmatch "\\.pytest_cache\\"
} | ForEach-Object {
    $dest = $_.FullName.Replace($sourceBackend, $backendPath)
    if ($_.PSIsContainer) {
        New-Item -ItemType Directory -Path $dest -Force | Out-Null
    } else {
        if ($_.Name -ne ".env" -or -not (Test-Path "$backendPath\.env")) {
            Copy-Item -Path $_.FullName -Destination $dest -Force
        }
    }
}

Write-Host "Archivos copiados" -ForegroundColor Gray

# Crear entorno virtual
Set-Location $backendPath
& python -m venv venv | Out-Null
& ".\venv\Scripts\pip.exe" install -r requirements.txt --quiet

Write-Host "Python venv creado e instalado" -ForegroundColor Gray

# Configurar .env
if (-not (Test-Path "$backendPath\.env")) {
    if (Test-Path "$backendPath\.env.example") {
        Copy-Item "$backendPath\.env.example" "$backendPath\.env"
    }
    # Actualizar valores
    $envLines = Get-Content "$backendPath\.env"
    $newLines = @()
    foreach ($line in $envLines) {
        if ($line -match "^FRONTEND_URL=") {
            $newLines += "FRONTEND_URL=https://$Domain"
        } elseif ($line -match "^DROPBOX_REDIRECT_URI=") {
            $newLines += "DROPBOX_REDIRECT_URI=https://$Domain/auth/dropbox/callback"
        } else {
            $newLines += $line
        }
    }
    $newLines | Set-Content "$backendPath\.env"
}

Write-Host "OK - Backend desplegado" -ForegroundColor Green

# ==========================
# 5. COPIAR FRONTEND
# ==========================
Write-Host "[5/7] Desplegando frontend..." -ForegroundColor Green

$sourceFrontend = "$PSScriptRoot\..\frontend"

Set-Location $sourceFrontend

# Build produccion
if (-not (Test-Path "$sourceFrontend\node_modules")) {
    & npm install | Out-Null
}
& npm run build | Out-Null

# Copiar dist
Copy-Item -Path "$sourceFrontend\dist\*" -Destination $frontendPath -Recurse -Force

# Copiar web.config
Copy-Item "$PSScriptRoot\web.config" -Destination "$frontendPath\web.config" -Force

Write-Host "OK - Frontend desplegado" -ForegroundColor Green

# ==========================
# 6. INSTALAR SERVICIO BACKEND
# ==========================
Write-Host "[6/7] Configurando servicio backend..." -ForegroundColor Green

# Descargar NSSM si no existe
$nssmPath = "C:\Windows\System32\nssm.exe"
if (-not (Test-Path $nssmPath)) {
    Write-Host "Descargando NSSM..." -ForegroundColor Gray
    $nssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
    $nssmZip = "$env:TEMP\nssm.zip"
    Invoke-WebRequest -Uri $nssmUrl -OutFile $nssmZip -UseBasicParsing
    Expand-Archive -Path $nssmZip -DestinationPath "$env:TEMP\nssm" -Force
    Copy-Item "$env:TEMP\nssm\nssm-2.24\win64\nssm.exe" -Destination $nssmPath -Force
    Remove-Item $nssmZip, "$env:TEMP\nssm" -Recurse -Force -ErrorAction SilentlyContinue
}

# Remover servicio si existe
$service = Get-Service -Name "DropboxBackend" -ErrorAction SilentlyContinue
if ($service) {
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
& nssm set DropboxBackend Start SERVICE_AUTO_START

# Iniciar servicio
Start-Service -Name "DropboxBackend"
Start-Sleep -Seconds 3

Write-Host "OK - Servicio backend configurado" -ForegroundColor Green

# ==========================
# 7. CONFIGURAR SITIO IIS
# ==========================
Write-Host "[7/7] Configurando sitio IIS..." -ForegroundColor Green

$siteName = "DropboxOrganizer"

# Remover sitio si existe
$existingSite = Get-Website -Name $siteName -ErrorAction SilentlyContinue
if ($existingSite) {
    Remove-Website -Name $siteName
}

# Crear sitio
New-Website -Name $siteName -PhysicalPath $frontendPath -Port 80 -HostHeader $Domain -Force | Out-Null

# Agregar binding HTTPS
$httpsBinding = Get-WebBinding -Name $siteName -Protocol "https" -Port 443 -ErrorAction SilentlyContinue
if ($httpsBinding) {
    Remove-WebBinding -Name $siteName -Protocol "https" -Port 443
}

New-WebBinding -Name $siteName -Protocol "https" -Port 443 -HostHeader $Domain -SslFlags 0

# Asociar certificado
$binding = Get-WebBinding -Name $siteName -Protocol "https" -Port 443
$binding.AddSslCertificate($certThumbprint, "my")

# Permisos
& icacls $deployPath /grant "IIS_IUSRS:(OI)(CI)RX" /T | Out-Null

# Iniciar sitio
Start-Website -Name $siteName

Write-Host "OK - Sitio IIS configurado" -ForegroundColor Green

# ====================================================================================================
# RESUMEN
# ====================================================================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "DEPLOYMENT COMPLETADO" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "URLs:" -ForegroundColor White
Write-Host "  - Frontend: https://$Domain" -ForegroundColor Cyan
Write-Host "  - Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  - API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Archivos:" -ForegroundColor White
Write-Host "  - $deployPath" -ForegroundColor Gray
Write-Host ""
Write-Host "Logs:" -ForegroundColor White
Write-Host "  - $logsPath\backend-stdout.log" -ForegroundColor Gray
Write-Host "  - $logsPath\backend-stderr.log" -ForegroundColor Gray
Write-Host ""
Write-Host "IMPORTANTE:" -ForegroundColor Yellow
Write-Host "1. Edita el archivo .env con tus credenciales:" -ForegroundColor White
Write-Host "   notepad $backendPath\.env" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Reinicia el backend:" -ForegroundColor White
Write-Host "   Restart-Service DropboxBackend" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Configurar Dropbox App Console:" -ForegroundColor White
Write-Host "   https://www.dropbox.com/developers/apps" -ForegroundColor Cyan
Write-Host "   Redirect URI: https://$Domain/auth/dropbox/callback" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Agregar al archivo hosts:" -ForegroundColor White
Write-Host "   C:\Windows\System32\drivers\etc\hosts" -ForegroundColor Cyan
Write-Host "   127.0.0.1 $Domain" -ForegroundColor Gray
Write-Host ""
