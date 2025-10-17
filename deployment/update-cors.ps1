# Script para actualizar CORS en main.py para acceso por IP
Write-Host "Actualizando configuración CORS..." -ForegroundColor Cyan

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Ejecuta como Administrador" -ForegroundColor Red
    exit 1
}

$mainPy = "C:\inetpub\wwwroot\dropbox-organizer\backend\app\main.py"

if (-not (Test-Path $mainPy)) {
    Write-Host "ERROR: No se encuentra main.py" -ForegroundColor Red
    exit 1
}

# Leer archivo
$content = Get-Content $mainPy -Raw

# Buscar la sección de CORS y reemplazarla
$oldCors = @'
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_URLS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
'@

$newCors = @'
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir acceso desde cualquier IP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
'@

if ($content -match [regex]::Escape($oldCors)) {
    $content = $content -replace [regex]::Escape($oldCors), $newCors
    $content | Set-Content $mainPy -Encoding UTF8
    Write-Host "OK - CORS actualizado para permitir cualquier IP" -ForegroundColor Green
} else {
    Write-Host "ADVERTENCIA - No se encontró la configuración CORS exacta" -ForegroundColor Yellow
    Write-Host "Verifica manualmente el archivo main.py" -ForegroundColor Yellow
}

Write-Host ""
