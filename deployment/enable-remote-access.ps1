# Script para habilitar acceso remoto a la aplicación
Write-Host "Habilitando acceso remoto..." -ForegroundColor Cyan

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Ejecuta como Administrador" -ForegroundColor Red
    exit 1
}

# 1. Obtener IP del servidor
Write-Host ""
Write-Host "=== IP del servidor ===" -ForegroundColor Yellow
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" -and $_.IPAddress -notlike "169.254.*" } | Select-Object -First 1).IPAddress
Write-Host "  IP Local: $ip" -ForegroundColor Cyan

# 2. Abrir puerto 443 en firewall
Write-Host ""
Write-Host "=== Configurando Firewall ===" -ForegroundColor Yellow
$ruleName = "DropboxAIOrganizer HTTPS"

# Verificar si la regla ya existe
$existingRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue

if ($existingRule) {
    Write-Host "  Regla de firewall ya existe" -ForegroundColor Yellow
    Remove-NetFirewallRule -DisplayName $ruleName
    Write-Host "  Regla antigua eliminada" -ForegroundColor Gray
}

# Crear nueva regla
New-NetFirewallRule -DisplayName $ruleName `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 443 `
    -Action Allow `
    -Profile Any `
    -Enabled True | Out-Null

Write-Host "OK - Puerto 443 (HTTPS) abierto en firewall" -ForegroundColor Green

# 3. Verificar binding de IIS
Write-Host ""
Write-Host "=== Verificando IIS ===" -ForegroundColor Yellow
Import-Module WebAdministration

$bindings = Get-WebBinding -Name "DropboxOrganizer"
foreach ($binding in $bindings) {
    Write-Host "  Protocol: $($binding.protocol) - Info: $($binding.bindingInformation)" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "ACCESO REMOTO HABILITADO" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Para acceder desde OTRO ordenador en la MISMA RED:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. En el OTRO ordenador, edita el archivo hosts:" -ForegroundColor White
Write-Host "   Windows: C:\Windows\System32\drivers\etc\hosts" -ForegroundColor Gray
Write-Host "   Mac/Linux: /etc/hosts" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Agrega esta linea:" -ForegroundColor White
Write-Host "   $ip dropboxaiorganizer.com" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. INSTALA EL CERTIFICADO en el otro ordenador:" -ForegroundColor White
Write-Host "   - Copia el archivo:" -ForegroundColor Gray
Write-Host "     C:\Users\amartin\Desktop\cert.pfx" -ForegroundColor Cyan
Write-Host "   - En el otro PC, doble clic en cert.pfx" -ForegroundColor Gray
Write-Host "   - Instalar en: Equipo local > Trusted Root Certification Authorities" -ForegroundColor Gray
Write-Host "   - Password: MGS-SSL" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Abre el navegador y ve a:" -ForegroundColor White
Write-Host "   https://dropboxaiorganizer.com" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "ACCESO DESDE INTERNET (avanzado)" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Requiere configuracion adicional:" -ForegroundColor White
Write-Host "  - Configurar port forwarding en router (443 -> $ip)" -ForegroundColor Gray
Write-Host "  - Configurar DNS real (dropboxaiorganizer.com -> IP publica)" -ForegroundColor Gray
Write-Host "  - Obtener certificado valido (Let's Encrypt)" -ForegroundColor Gray
Write-Host ""
