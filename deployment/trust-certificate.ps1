# Script para instalar certificado autofirmado como confiable
Write-Host "Instalando certificado como confiable..." -ForegroundColor Cyan

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Ejecuta como Administrador" -ForegroundColor Red
    exit 1
}

$certPath = "$env:USERPROFILE\Desktop\cert.pfx"
$certPassword = "MGS-SSL"

if (-not (Test-Path $certPath)) {
    Write-Host "ERROR: No se encuentra el certificado en $certPath" -ForegroundColor Red
    exit 1
}

Write-Host "Importando certificado a Trusted Root..." -ForegroundColor Gray

$securePwd = ConvertTo-SecureString -String $certPassword -Force -AsPlainText

# Importar a Personal (My) - ya existe
Write-Host "  Certificado ya existe en Personal" -ForegroundColor Gray

# Importar a Trusted Root Certification Authorities
$cert = Import-PfxCertificate -FilePath $certPath -CertStoreLocation Cert:\LocalMachine\Root -Password $securePwd -Exportable

Write-Host ""
Write-Host "OK - Certificado instalado como confiable" -ForegroundColor Green
Write-Host ""
Write-Host "Thumbprint: $($cert.Thumbprint)" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANTE: Cierra y reabre el navegador" -ForegroundColor Yellow
Write-Host ""
Write-Host "Luego prueba: https://dropboxaiorganizer.com" -ForegroundColor Cyan
Write-Host ""
