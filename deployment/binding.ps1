# === Variables fijas ===
$Domain   = "dropboxaiorganizer.com"
$SiteName = "Default Web Site"   # cámbialo si usas otro sitio

Import-Module WebAdministration -ErrorAction Stop

if (-not (Test-Path "IIS:\Sites\$SiteName")) {
  throw "El sitio '$SiteName' no existe en IIS."
}

# 1) Asegurar binding HTTP :80 con Host header (para que wacs 'N' lo vea)
if (-not (Get-WebBinding -Name $SiteName -Protocol http -Port 80 -HostHeader $Domain -ErrorAction SilentlyContinue)) {
  New-WebBinding -Name $SiteName -Protocol http -Port 80 -IPAddress "*" -HostHeader $Domain | Out-Null
  Write-Host "Binding HTTP creado: http *:80:$Domain"
} else {
  Write-Host "Binding HTTP ya existía: http *:80:$Domain"
}

# 2) (Opcional) Abrir firewall local 80/443 en perfiles de dominio/privado
if (Get-Command New-NetFirewallRule -ErrorAction SilentlyContinue) {
  New-NetFirewallRule -DisplayName "IIS HTTP 80 ($Domain)"  -Direction Inbound -Protocol TCP -LocalPort 80  -Action Allow -Profile Domain,Private -ErrorAction SilentlyContinue | Out-Null
  New-NetFirewallRule -DisplayName "IIS HTTPS 443 ($Domain)" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow -Profile Domain,Private -ErrorAction SilentlyContinue | Out-Null
}
Write-Host "Listo: IIS preparado. Emite el certificado con win-acme (sin autofirmado)."
