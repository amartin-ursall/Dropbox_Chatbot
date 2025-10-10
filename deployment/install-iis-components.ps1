# ============================================================================
# Script de Instalación de Componentes IIS
# Dropbox AI Organizer - URSALL System
# ============================================================================
# Este script instala todos los componentes necesarios de IIS para el deployment
# Debe ejecutarse como Administrador en Windows Server
# ============================================================================

param(
    [switch]$SkipRestart
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Instalación de Componentes IIS" -ForegroundColor Cyan
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

Write-Host "[1/6] Instalando IIS (Web Server)..." -ForegroundColor Green
try {
    Install-WindowsFeature -name Web-Server -IncludeManagementTools -ErrorAction Stop
    Write-Host "  ✓ IIS instalado correctamente" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Error instalando IIS: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/6] Instalando características adicionales de IIS..." -ForegroundColor Green
$features = @(
    "Web-WebSockets",
    "Web-App-Dev",
    "Web-Net-Ext45",
    "Web-Asp-Net45",
    "Web-ISAPI-Ext",
    "Web-ISAPI-Filter"
)

foreach ($feature in $features) {
    try {
        Install-WindowsFeature -name $feature -ErrorAction Stop
        Write-Host "  ✓ $feature instalado" -ForegroundColor Gray
    } catch {
        Write-Host "  ⚠ Advertencia instalando $feature" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "[3/6] Descargando e instalando URL Rewrite Module..." -ForegroundColor Green

$urlRewriteUrl = "https://download.microsoft.com/download/1/2/8/128E2E22-C1B9-44A4-BE2A-5859ED1D4592/rewrite_amd64_en-US.msi"
$urlRewritePath = "$env:TEMP\rewrite_amd64_en-US.msi"

try {
    # Verificar si ya está instalado
    $installed = Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* |
                 Where-Object { $_.DisplayName -like "*URL Rewrite*" }

    if ($installed) {
        Write-Host "  ✓ URL Rewrite Module ya está instalado" -ForegroundColor Green
    } else {
        Write-Host "  Descargando URL Rewrite Module..." -ForegroundColor Gray
        Invoke-WebRequest -Uri $urlRewriteUrl -OutFile $urlRewritePath -UseBasicParsing

        Write-Host "  Instalando URL Rewrite Module..." -ForegroundColor Gray
        Start-Process msiexec.exe -ArgumentList "/i `"$urlRewritePath`" /quiet /norestart" -Wait -NoNewWindow

        Write-Host "  ✓ URL Rewrite Module instalado correctamente" -ForegroundColor Green
        Remove-Item $urlRewritePath -Force -ErrorAction SilentlyContinue
    }
} catch {
    Write-Host "  ✗ Error instalando URL Rewrite: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  Puedes instalarlo manualmente desde: https://www.iis.net/downloads/microsoft/url-rewrite" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[4/6] Descargando e instalando Application Request Routing (ARR)..." -ForegroundColor Green

$arrUrl = "https://download.microsoft.com/download/E/9/8/E9849D6A-020E-47E4-9FD0-A023E99B54EB/requestRouter_amd64.msi"
$arrPath = "$env:TEMP\requestRouter_amd64.msi"

try {
    # Verificar si ya está instalado
    $installed = Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* |
                 Where-Object { $_.DisplayName -like "*Application Request Routing*" }

    if ($installed) {
        Write-Host "  ✓ ARR ya está instalado" -ForegroundColor Green
    } else {
        Write-Host "  Descargando ARR..." -ForegroundColor Gray
        Invoke-WebRequest -Uri $arrUrl -OutFile $arrPath -UseBasicParsing

        Write-Host "  Instalando ARR..." -ForegroundColor Gray
        Start-Process msiexec.exe -ArgumentList "/i `"$arrPath`" /quiet /norestart" -Wait -NoNewWindow

        Write-Host "  ✓ ARR instalado correctamente" -ForegroundColor Green
        Remove-Item $arrPath -Force -ErrorAction SilentlyContinue
    }
} catch {
    Write-Host "  ✗ Error instalando ARR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  Puedes instalarlo manualmente desde: https://www.iis.net/downloads/microsoft/application-request-routing" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[5/6] Habilitando proxy en ARR..." -ForegroundColor Green

try {
    # Importar módulo de IIS
    Import-Module WebAdministration -ErrorAction Stop

    # Habilitar proxy en ARR
    Set-WebConfigurationProperty -pspath 'MACHINE/WEBROOT/APPHOST' -filter "system.webServer/proxy" -name "enabled" -value "True" -ErrorAction Stop

    Write-Host "  ✓ Proxy habilitado en ARR" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ No se pudo habilitar el proxy automáticamente" -ForegroundColor Yellow
    Write-Host "  Deberás habilitarlo manualmente:" -ForegroundColor Yellow
    Write-Host "    1. Abrir IIS Manager" -ForegroundColor Gray
    Write-Host "    2. Seleccionar el servidor (nivel raíz)" -ForegroundColor Gray
    Write-Host "    3. Doble clic en 'Application Request Routing Cache'" -ForegroundColor Gray
    Write-Host "    4. Panel derecho → 'Server Proxy Settings'" -ForegroundColor Gray
    Write-Host "    5. Marcar 'Enable proxy' → Apply" -ForegroundColor Gray
}

Write-Host ""
Write-Host "[6/6] Reiniciando IIS..." -ForegroundColor Green

try {
    iisreset /restart
    Write-Host "  ✓ IIS reiniciado correctamente" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ No se pudo reiniciar IIS automáticamente" -ForegroundColor Yellow
    Write-Host "  Ejecuta manualmente: iisreset" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  ✓ Instalación Completada" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Siguiente paso: Ejecutar install-backend-service.ps1" -ForegroundColor Yellow
Write-Host ""

if (-not $SkipRestart) {
    $restart = Read-Host "¿Deseas reiniciar el servidor ahora? (s/n)"
    if ($restart -eq 's' -or $restart -eq 'S') {
        Write-Host "Reiniciando servidor en 10 segundos..." -ForegroundColor Yellow
        shutdown /r /t 10
    }
}
