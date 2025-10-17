# Script de diagnostico de prerequisitos para deployment
Write-Host "=== VERIFICACION DE PREREQUISITOS ===" -ForegroundColor Cyan
Write-Host ""

# 1. Permisos de administrador
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if ($isAdmin) {
    Write-Host "[OK] Ejecutando como Administrador" -ForegroundColor Green
} else {
    Write-Host "[ERROR] NO ejecutando como Administrador" -ForegroundColor Red
}

# 2. Python
try {
    $pythonVersion = & python --version 2>&1
    Write-Host "[OK] Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python no encontrado" -ForegroundColor Red
}

# 3. Node.js
try {
    $nodeVersion = & node --version 2>&1
    Write-Host "[OK] Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Node.js no encontrado" -ForegroundColor Red
}

# 4. IIS
try {
    $iis = Get-WindowsFeature -Name Web-Server -ErrorAction Stop
    if ($iis.Installed) {
        Write-Host "[OK] IIS instalado" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] IIS NO instalado" -ForegroundColor Red
    }
} catch {
    Write-Host "[WARN] No se puede verificar IIS (puede ser Windows 10/11)" -ForegroundColor Yellow
    try {
        Import-Module WebAdministration -ErrorAction Stop
        Write-Host "[OK] Modulo WebAdministration disponible" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] IIS no disponible" -ForegroundColor Red
    }
}

# 5. Certificado
$certPath = "$env:USERPROFILE\Desktop\cert.pfx"
if (Test-Path $certPath) {
    Write-Host "[OK] Certificado encontrado: $certPath" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Certificado NO encontrado: $certPath" -ForegroundColor Red
}

# 6. Espacio en disco
$drive = Get-PSDrive C
$freeGB = [math]::Round($drive.Free / 1GB, 2)
Write-Host "[OK] Espacio libre en C: $freeGB GB" -ForegroundColor Green

# 7. Verificar archivos fuente
$backendPath = "$PSScriptRoot\..\backend"
$frontendPath = "$PSScriptRoot\..\frontend"

if (Test-Path $backendPath) {
    Write-Host "[OK] Directorio backend encontrado" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Directorio backend NO encontrado: $backendPath" -ForegroundColor Red
}

if (Test-Path $frontendPath) {
    Write-Host "[OK] Directorio frontend encontrado" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Directorio frontend NO encontrado: $frontendPath" -ForegroundColor Red
}

# 8. Web.config
$webConfigPath = "$PSScriptRoot\web.config"
if (Test-Path $webConfigPath) {
    Write-Host "[OK] web.config encontrado" -ForegroundColor Green
} else {
    Write-Host "[ERROR] web.config NO encontrado: $webConfigPath" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== FIN DE VERIFICACION ===" -ForegroundColor Cyan
