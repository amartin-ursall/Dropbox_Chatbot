# Script para diagnosticar el certificado SSL
Write-Host "Diagnosticando certificado SSL..." -ForegroundColor Cyan
Write-Host ""

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Ejecuta como Administrador" -ForegroundColor Red
    exit 1
}

# 1. Verificar certificados en Personal (My)
Write-Host "=== Certificados en Personal (My) ===" -ForegroundColor Yellow
$myCerts = Get-ChildItem -Path Cert:\LocalMachine\My | Where-Object { $_.Subject -like "*dropbox*" -or $_.FriendlyName -like "*dropbox*" }
if ($myCerts) {
    foreach ($cert in $myCerts) {
        Write-Host "  Subject: $($cert.Subject)" -ForegroundColor Cyan
        Write-Host "  Thumbprint: $($cert.Thumbprint)" -ForegroundColor Gray
        Write-Host "  NotAfter: $($cert.NotAfter)" -ForegroundColor Gray
        Write-Host "  Issuer: $($cert.Issuer)" -ForegroundColor Gray
        Write-Host ""
    }
} else {
    Write-Host "  No se encontraron certificados" -ForegroundColor Red
}

# 2. Verificar certificados en Trusted Root
Write-Host "=== Certificados en Trusted Root ===" -ForegroundColor Yellow
$rootCerts = Get-ChildItem -Path Cert:\LocalMachine\Root | Where-Object { $_.Subject -like "*dropbox*" -or $_.FriendlyName -like "*dropbox*" }
if ($rootCerts) {
    foreach ($cert in $rootCerts) {
        Write-Host "  Subject: $($cert.Subject)" -ForegroundColor Green
        Write-Host "  Thumbprint: $($cert.Thumbprint)" -ForegroundColor Gray
        Write-Host ""
    }
} else {
    Write-Host "  No se encontraron certificados en Trusted Root" -ForegroundColor Red
    Write-Host "  ESTE ES EL PROBLEMA!" -ForegroundColor Red
}

# 3. Verificar binding de IIS
Write-Host "=== Binding de IIS ===" -ForegroundColor Yellow
Import-Module WebAdministration
$binding = Get-WebBinding -Name "DropboxOrganizer" -Protocol "https"
if ($binding) {
    Write-Host "  HostName: $($binding.bindingInformation)" -ForegroundColor Cyan
    $certHash = $binding.certificateHash
    Write-Host "  Certificate Hash: $certHash" -ForegroundColor Gray

    # Buscar el certificado
    $cert = Get-ChildItem -Path Cert:\LocalMachine\My | Where-Object { $_.Thumbprint -eq $certHash }
    if ($cert) {
        Write-Host "  Certificate Subject: $($cert.Subject)" -ForegroundColor Green
        Write-Host "  Certificate Issuer: $($cert.Issuer)" -ForegroundColor Gray
    }
} else {
    Write-Host "  No se encontro binding HTTPS" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Recomendaciones ===" -ForegroundColor Yellow

if (-not $rootCerts) {
    Write-Host "1. El certificado NO esta en Trusted Root" -ForegroundColor Red
    Write-Host "   Solucion: Ejecuta .\trust-certificate.ps1" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "2. Verifica que cerraste COMPLETAMENTE el navegador" -ForegroundColor Yellow
Write-Host "   - Cierra todas las ventanas y pestanas" -ForegroundColor Gray
Write-Host "   - Abre el Administrador de Tareas" -ForegroundColor Gray
Write-Host "   - Busca Chrome/Edge/Firefox y finaliza el proceso" -ForegroundColor Gray
Write-Host "   - Reabre el navegador" -ForegroundColor Gray
Write-Host ""
