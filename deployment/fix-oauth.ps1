# Script para corregir URLs de OAuth en .env
Write-Host "Corrigiendo configuración OAuth..." -ForegroundColor Cyan

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Ejecuta como Administrador" -ForegroundColor Red
    exit 1
}

$envFile = "C:\inetpub\wwwroot\dropbox-organizer\backend\.env"

if (-not (Test-Path $envFile)) {
    Write-Host "ERROR: No se encuentra .env" -ForegroundColor Red
    exit 1
}

Write-Host "Actualizando URLs en .env..." -ForegroundColor Gray

# Leer archivo
$content = Get-Content $envFile

# Reemplazar URLs (dropboxorganizer.com → dropboxaiorganizer.com)
$newContent = $content -replace 'dropboxorganizer\.com', 'dropboxaiorganizer.com'

# Guardar
$newContent | Set-Content $envFile

Write-Host "OK - URLs actualizadas" -ForegroundColor Green

# Mostrar las líneas relevantes
Write-Host ""
Write-Host "Configuración actual:" -ForegroundColor White
Get-Content $envFile | Select-String -Pattern "FRONTEND_URL|DROPBOX_REDIRECT_URI" | ForEach-Object {
    if ($_ -notmatch "^#") {
        Write-Host "  $_" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "Reiniciando servicio backend..." -ForegroundColor Gray
Restart-Service DropboxBackend

Start-Sleep -Seconds 3

$serviceStatus = Get-Service DropboxBackend
if ($serviceStatus.Status -eq "Running") {
    Write-Host "OK - Backend reiniciado" -ForegroundColor Green
} else {
    Write-Host "ERROR: Backend no se reinició correctamente" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SIGUIENTE PASO:" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configura Dropbox App Console:" -ForegroundColor White
Write-Host "  1. Ve a: https://www.dropbox.com/developers/apps" -ForegroundColor Gray
Write-Host "  2. Selecciona tu app" -ForegroundColor Gray
Write-Host "  3. En OAuth 2 → Redirect URIs, agrega:" -ForegroundColor Gray
Write-Host "     https://dropboxaiorganizer.com/auth/dropbox/callback" -ForegroundColor Cyan
Write-Host "  4. Guarda los cambios" -ForegroundColor Gray
Write-Host ""
Write-Host "Luego prueba: https://dropboxaiorganizer.com" -ForegroundColor Cyan
Write-Host ""
