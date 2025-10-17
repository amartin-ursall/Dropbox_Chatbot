# Script para verificar binding de IIS
Write-Host "Verificando binding de IIS..." -ForegroundColor Cyan

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Ejecuta como Administrador" -ForegroundColor Red
    exit 1
}

Import-Module WebAdministration

Write-Host ""
Write-Host "=== Binding HTTPS de DropboxOrganizer ===" -ForegroundColor Yellow
$binding = Get-WebBinding -Name "DropboxOrganizer" -Protocol "https"

if ($binding) {
    Write-Host "  bindingInformation: $($binding.bindingInformation)" -ForegroundColor Cyan

    $certHash = $binding.certificateHash
    Write-Host "  Certificate Hash: $certHash" -ForegroundColor White

    # Buscar certificado
    $cert = Get-ChildItem -Path Cert:\LocalMachine\My | Where-Object { $_.Thumbprint -eq $certHash }
    if ($cert) {
        Write-Host "  Certificate Subject: $($cert.Subject)" -ForegroundColor Green
        Write-Host "  Certificate Issuer: $($cert.Issuer)" -ForegroundColor Gray
        Write-Host "  NotAfter: $($cert.NotAfter)" -ForegroundColor Gray
    } else {
        Write-Host "  ERROR: No se encuentra el certificado" -ForegroundColor Red
    }
} else {
    Write-Host "  No se encontro binding HTTPS" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Certificado correcto ===" -ForegroundColor Yellow
Write-Host "Thumbprint esperado: EA67AD8C9055AD910A771D76AD7FC4D045198D6A" -ForegroundColor Cyan
Write-Host "Subject: CN=dropboxaiorganizer.com" -ForegroundColor Cyan

Write-Host ""
Write-Host "=== Verificar si esta en Trusted Root ===" -ForegroundColor Yellow
$rootCert = Get-ChildItem -Path Cert:\LocalMachine\Root | Where-Object { $_.Thumbprint -eq "EA67AD8C9055AD910A771D76AD7FC4D045198D6A" }
if ($rootCert) {
    Write-Host "OK - Certificado YA esta en Trusted Root" -ForegroundColor Green
} else {
    Write-Host "NO - Certificado NO esta en Trusted Root" -ForegroundColor Red
    Write-Host "Hay que instalarlo manualmente" -ForegroundColor Yellow
}

Write-Host ""
