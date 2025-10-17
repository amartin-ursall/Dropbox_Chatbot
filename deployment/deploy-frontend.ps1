# Script para desplegar frontend compilado a IIS
Write-Host "Desplegando frontend a IIS..." -ForegroundColor Cyan

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Ejecuta como Administrador" -ForegroundColor Red
    exit 1
}

$source = "$PSScriptRoot\..\frontend\dist"
$dest = "C:\inetpub\wwwroot\dropbox-organizer\frontend"

if (-not (Test-Path $source)) {
    Write-Host "ERROR: No se encuentra el build del frontend" -ForegroundColor Red
    Write-Host "Ejecuta primero: cd frontend && npx vite build" -ForegroundColor Yellow
    exit 1
}

Write-Host "Deteniendo sitio IIS..." -ForegroundColor Gray
Import-Module WebAdministration
Stop-Website -Name "DropboxOrganizer" -ErrorAction SilentlyContinue

Start-Sleep -Seconds 2

Write-Host "Limpiando carpeta destino..." -ForegroundColor Gray
Get-ChildItem $dest -Exclude web.config | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Copiando archivos compilados..." -ForegroundColor Gray
Copy-Item "$source\*" -Destination $dest -Recurse -Force

Write-Host "Verificando archivos..." -ForegroundColor Gray
if (Test-Path "$dest\index.html") {
    Write-Host "OK - index.html copiado" -ForegroundColor Green
} else {
    Write-Host "ERROR: index.html no se copió" -ForegroundColor Red
}

if (Test-Path "$dest\assets") {
    Write-Host "OK - carpeta assets copiada" -ForegroundColor Green
} else {
    Write-Host "ERROR: carpeta assets no se copió" -ForegroundColor Red
}

Write-Host "Iniciando sitio IIS..." -ForegroundColor Gray
Start-Website -Name "DropboxOrganizer"

Write-Host ""
Write-Host "OK - Frontend desplegado" -ForegroundColor Green
Write-Host ""
Write-Host "Prueba ahora: https://dropboxaiorganizer.com" -ForegroundColor Cyan
