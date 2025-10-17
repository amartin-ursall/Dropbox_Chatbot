# Script para reemplazar web.config con version corregida
Write-Host "Actualizando web.config..." -ForegroundColor Cyan

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Ejecuta como Administrador" -ForegroundColor Red
    exit 1
}

$source = "$PSScriptRoot\web.config"
$dest = "C:\inetpub\wwwroot\dropbox-organizer\frontend\web.config"

if (-not (Test-Path $source)) {
    Write-Host "ERROR: No se encuentra web.config en deployment/" -ForegroundColor Red
    exit 1
}

Write-Host "Deteniendo sitio IIS..." -ForegroundColor Gray
Import-Module WebAdministration
Stop-Website -Name "DropboxOrganizer"

Start-Sleep -Seconds 2

Write-Host "Reemplazando web.config..." -ForegroundColor Gray
Copy-Item $source $dest -Force

Write-Host "Iniciando sitio IIS..." -ForegroundColor Gray
Start-Website -Name "DropboxOrganizer"

Write-Host ""
Write-Host "OK - web.config actualizado" -ForegroundColor Green
Write-Host ""
Write-Host "Prueba ahora: https://dropboxaiorganizer.com" -ForegroundColor Cyan
