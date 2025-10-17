# Actualizar web.config con version simplificada
Write-Host "Actualizando web.config..." -ForegroundColor Cyan

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Ejecuta como Administrador" -ForegroundColor Red
    exit 1
}

$source = "$PSScriptRoot\web-simple.config"
$dest = "C:\inetpub\wwwroot\dropbox-organizer\frontend\web.config"

Write-Host "Deteniendo sitio IIS..." -ForegroundColor Gray
Import-Module WebAdministration
Stop-Website -Name "DropboxOrganizer" -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host "Reemplazando web.config..." -ForegroundColor Gray
Copy-Item $source $dest -Force

Write-Host "Iniciando sitio IIS..." -ForegroundColor Gray
Start-Website -Name "DropboxOrganizer"
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "OK - web.config actualizado (version simplificada)" -ForegroundColor Green
Write-Host ""
Write-Host "Prueba ahora: https://dropboxaiorganizer.com" -ForegroundColor Cyan
