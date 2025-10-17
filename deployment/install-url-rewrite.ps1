# Script para instalar URL Rewrite Module para IIS
Write-Host "Instalando URL Rewrite Module..." -ForegroundColor Cyan

# Verificar permisos
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Ejecuta como Administrador" -ForegroundColor Red
    exit 1
}

# URL del instalador
$urlRewriteUrl = "https://download.microsoft.com/download/1/2/8/128E2E22-C1B9-44A4-BE2A-5859ED1D4592/rewrite_amd64_en-US.msi"
$installerPath = "$env:TEMP\rewrite_amd64.msi"

Write-Host "Descargando URL Rewrite Module..." -ForegroundColor Gray
try {
    Invoke-WebRequest -Uri $urlRewriteUrl -OutFile $installerPath -UseBasicParsing
    Write-Host "OK - Descargado" -ForegroundColor Green
} catch {
    Write-Host "ERROR: No se pudo descargar: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "Instalando..." -ForegroundColor Gray
try {
    Start-Process msiexec.exe -ArgumentList "/i `"$installerPath`" /quiet /norestart" -Wait -NoNewWindow
    Write-Host "OK - URL Rewrite instalado" -ForegroundColor Green
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Limpiar
Remove-Item $installerPath -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "URL Rewrite Module instalado correctamente" -ForegroundColor Green
Write-Host "Reiniciando IIS..." -ForegroundColor Gray

# Reiniciar IIS
iisreset /noforce

Write-Host ""
Write-Host "Listo! Ahora prueba acceder a: https://dropboxaiorganizer.com" -ForegroundColor Cyan
