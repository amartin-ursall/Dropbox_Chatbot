# Script para asociar certificado SSL al binding de IIS
Write-Host "Reparando binding SSL de IIS..." -ForegroundColor Cyan

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Ejecuta como Administrador" -ForegroundColor Red
    exit 1
}

Import-Module WebAdministration

# 1. Buscar el certificado correcto
Write-Host ""
Write-Host "Buscando certificado CN=dropboxaiorganizer.com..." -ForegroundColor Gray
$cert = Get-ChildItem -Path Cert:\LocalMachine\My | Where-Object { $_.Subject -eq "CN=dropboxaiorganizer.com" }

if (-not $cert) {
    Write-Host "ERROR: No se encuentra el certificado CN=dropboxaiorganizer.com" -ForegroundColor Red
    exit 1
}

Write-Host "OK - Certificado encontrado" -ForegroundColor Green
Write-Host "  Subject: $($cert.Subject)" -ForegroundColor Cyan
Write-Host "  Thumbprint: $($cert.Thumbprint)" -ForegroundColor Gray
Write-Host "  NotAfter: $($cert.NotAfter)" -ForegroundColor Gray

# 2. Instalar certificado en Trusted Root
Write-Host ""
Write-Host "Instalando certificado en Trusted Root..." -ForegroundColor Gray
$rootCert = Get-ChildItem -Path Cert:\LocalMachine\Root | Where-Object { $_.Thumbprint -eq $cert.Thumbprint }

if ($rootCert) {
    Write-Host "  Certificado ya existe en Trusted Root" -ForegroundColor Yellow
} else {
    # Exportar e importar el certificado
    $certBytes = $cert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert)
    $newCert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2
    $newCert.Import($certBytes)

    $store = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root", "LocalMachine")
    $store.Open("ReadWrite")
    $store.Add($newCert)
    $store.Close()

    Write-Host "OK - Certificado instalado en Trusted Root" -ForegroundColor Green
}

# 3. Eliminar binding HTTPS existente
Write-Host ""
Write-Host "Eliminando binding HTTPS existente..." -ForegroundColor Gray
Remove-WebBinding -Name "DropboxOrganizer" -Protocol "https" -HostHeader "dropboxaiorganizer.com" -ErrorAction SilentlyContinue

# 4. Crear nuevo binding con certificado
Write-Host "Creando nuevo binding HTTPS con certificado..." -ForegroundColor Gray
New-WebBinding -Name "DropboxOrganizer" -Protocol "https" -Port 443 -HostHeader "dropboxaiorganizer.com" -SslFlags 1

# 5. Asociar certificado al binding
Write-Host "Asociando certificado al binding..." -ForegroundColor Gray
$binding = Get-WebBinding -Name "DropboxOrganizer" -Protocol "https"

# Método alternativo usando netsh
$certHash = $cert.Thumbprint
$appId = "{" + [guid]::NewGuid().ToString() + "}"

# Limpiar binding anterior si existe
netsh http delete sslcert hostnameport=dropboxaiorganizer.com:443 | Out-Null

# Agregar nuevo binding
$result = netsh http add sslcert hostnameport=dropboxaiorganizer.com:443 certhash=$certHash appid=$appId certstorename=MY

if ($LASTEXITCODE -eq 0) {
    Write-Host "OK - Certificado asociado correctamente" -ForegroundColor Green
} else {
    Write-Host "ERROR al asociar certificado" -ForegroundColor Red
    Write-Host $result -ForegroundColor Gray
}

# 6. Reiniciar sitio IIS
Write-Host ""
Write-Host "Reiniciando sitio IIS..." -ForegroundColor Gray
Stop-Website -Name "DropboxOrganizer" -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Start-Website -Name "DropboxOrganizer"

$siteStatus = Get-Website -Name "DropboxOrganizer"
Write-Host "  Estado: $($siteStatus.State)" -ForegroundColor Cyan

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "SSL CONFIGURADO CORRECTAMENTE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANTE:" -ForegroundColor Yellow
Write-Host "1. Cierra COMPLETAMENTE el navegador" -ForegroundColor White
Write-Host "   - Abre Administrador de Tareas (Ctrl+Shift+Esc)" -ForegroundColor Gray
Write-Host "   - Busca Chrome/Edge/Firefox" -ForegroundColor Gray
Write-Host "   - Clic derecho > Finalizar tarea" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Reabre el navegador" -ForegroundColor White
Write-Host ""
Write-Host "3. Prueba: https://dropboxaiorganizer.com" -ForegroundColor Cyan
Write-Host "   Deberia aparecer como SEGURO (candado verde)" -ForegroundColor Green
Write-Host ""
