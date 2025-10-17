# ============================================================================
# Script de Instalacion de Certificado SSL con win-acme
# Dropbox AI Organizer - URSALL System
# ============================================================================
# Este script descarga e instala win-acme para gestionar certificados SSL
# de Let's Encrypt automaticamente en IIS
# ============================================================================

param(
    [string]$Domain = "",
    [switch]$SelfSigned = $false
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Instalacion de Certificado SSL" -ForegroundColor Cyan
Write-Host "  Dropbox AI Organizer - URSALL" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que se ejecuta como administrador
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: Este script debe ejecutarse como Administrador" -ForegroundColor Red
    exit 1
}

# ============================================================================
# OPCION 1: Certificado Let's Encrypt con win-acme (PRODUCCION)
# ============================================================================

if (-not $SelfSigned) {
    Write-Host "Instalando win-acme para certificados Let's Encrypt..." -ForegroundColor Green
    Write-Host ""

    # Verificar dominio
    if (-not $Domain) {
        Write-Host "ADVERTENCIA: No se especifico dominio" -ForegroundColor Yellow
        $Domain = Read-Host "Ingresa tu dominio (ej: dropboxorganizer.com)"
    }

    if (-not $Domain) {
        Write-Host "ERROR: Debes especificar un dominio para Let's Encrypt" -ForegroundColor Red
        Write-Host "Uso: .\install-ssl-certificate.ps1 -Domain tudominio.com" -ForegroundColor Yellow
        exit 1
    }

    Write-Host "Dominio: $Domain" -ForegroundColor Cyan
    Write-Host ""

    # Verificar que el dominio resuelve a este servidor
    Write-Host "[1/5] Verificando resolucion DNS..." -ForegroundColor Green
    try {
        $dnsResult = Resolve-DnsName -Name $Domain -Type A -ErrorAction Stop
        $resolvedIP = $dnsResult[0].IPAddress

        Write-Host "  El dominio $Domain resuelve a: $resolvedIP" -ForegroundColor Gray

        # Obtener IP local
        $localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" })[0].IPAddress

        if ($resolvedIP -eq $localIP) {
            Write-Host "  OK DNS configurado correctamente" -ForegroundColor Green
        } else {
            Write-Host "  ADVERTENCIA: El dominio resuelve a $resolvedIP pero la IP local es $localIP" -ForegroundColor Yellow
            Write-Host "  Asegurate de que el DNS este correctamente configurado" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ADVERTENCIA No se pudo verificar DNS: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host "  Continuando de todos modos..." -ForegroundColor Yellow
    }

    # Descargar win-acme
    Write-Host ""
    Write-Host "[2/5] Descargando win-acme..." -ForegroundColor Green

    $winAcmePath = "C:\win-acme"
    $winAcmeUrl = "https://github.com/win-acme/win-acme/releases/latest/download/win-acme.v2.2.9.1701.x64.pluggable.zip"
    $winAcmeZip = "$env:TEMP\win-acme.zip"

    try {
        New-Item -ItemType Directory -Path $winAcmePath -Force | Out-Null

        Write-Host "  Descargando desde GitHub..." -ForegroundColor Gray
        Invoke-WebRequest -Uri $winAcmeUrl -OutFile $winAcmeZip -UseBasicParsing

        Write-Host "  Extrayendo archivos..." -ForegroundColor Gray
        Expand-Archive -Path $winAcmeZip -DestinationPath $winAcmePath -Force

        Remove-Item $winAcmeZip -Force -ErrorAction SilentlyContinue

        Write-Host "  OK win-acme instalado en $winAcmePath" -ForegroundColor Green
    } catch {
        Write-Host "  ERROR descargando win-acme: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }

    # Verificar que IIS tiene un sitio web escuchando en puerto 80
    Write-Host ""
    Write-Host "[3/5] Verificando configuracion de IIS..." -ForegroundColor Green

    try {
        Import-Module WebAdministration -ErrorAction Stop

        $site = Get-Website | Where-Object { $_.Bindings.Collection.bindingInformation -like "*:80:*" }

        if (-not $site) {
            Write-Host "  ADVERTENCIA: No hay sitio IIS escuchando en puerto 80" -ForegroundColor Yellow
            Write-Host "  win-acme necesita que IIS responda en puerto 80 para la validacion" -ForegroundColor Yellow
        } else {
            Write-Host "  OK Sitio IIS encontrado: $($site.Name)" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ADVERTENCIA No se pudo verificar IIS" -ForegroundColor Yellow
    }

    # Ejecutar win-acme en modo interactivo
    Write-Host ""
    Write-Host "[4/5] Ejecutando win-acme..." -ForegroundColor Green
    Write-Host ""
    Write-Host "INSTRUCCIONES:" -ForegroundColor Yellow
    Write-Host "  1. Selecciona opcion N (Create certificate - simple mode)" -ForegroundColor Gray
    Write-Host "  2. Ingresa tu dominio: $Domain" -ForegroundColor Gray
    Write-Host "  3. Selecciona IIS como destino de instalacion" -ForegroundColor Gray
    Write-Host "  4. Acepta crear tarea programada para renovacion automatica" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Presiona Enter para continuar..." -ForegroundColor Yellow
    $null = Read-Host

    Set-Location $winAcmePath
    & ".\wacs.exe"

    # Verificar certificado instalado
    Write-Host ""
    Write-Host "[5/5] Verificando instalacion..." -ForegroundColor Green

    $cert = Get-ChildItem -Path Cert:\LocalMachine\My | Where-Object { $_.Subject -like "*$Domain*" } | Sort-Object NotAfter -Descending | Select-Object -First 1

    if ($cert) {
        Write-Host "  OK Certificado instalado correctamente" -ForegroundColor Green
        Write-Host "  Subject: $($cert.Subject)" -ForegroundColor Gray
        Write-Host "  Emisor: $($cert.Issuer)" -ForegroundColor Gray
        Write-Host "  Valido hasta: $($cert.NotAfter)" -ForegroundColor Gray
        Write-Host "  Thumbprint: $($cert.Thumbprint)" -ForegroundColor Gray
    } else {
        Write-Host "  ADVERTENCIA No se encontro certificado para $Domain" -ForegroundColor Yellow
    }

    # Verificar tarea programada
    $task = Get-ScheduledTask -TaskName "win-acme*" -ErrorAction SilentlyContinue

    if ($task) {
        Write-Host ""
        Write-Host "  OK Tarea programada de renovacion creada" -ForegroundColor Green
        Write-Host "  El certificado se renovara automaticamente cada 60 dias" -ForegroundColor Gray
    }

} else {
    # ============================================================================
    # OPCION 2: Certificado Autofirmado (SOLO DESARROLLO/TESTING)
    # ============================================================================

    Write-Host "ADVERTENCIA: Creando certificado autofirmado" -ForegroundColor Yellow
    Write-Host "Los certificados autofirmados NO son validos para OAuth de Dropbox" -ForegroundColor Yellow
    Write-Host "Solo usalos para pruebas internas" -ForegroundColor Yellow
    Write-Host ""

    if (-not $Domain) {
        $Domain = Read-Host "Ingresa el dominio (ej: dropboxorganizer.com)"
    }

    Write-Host ""
    Write-Host "[1/3] Creando certificado autofirmado..." -ForegroundColor Green

    try {
        $cert = New-SelfSignedCertificate `
            -DnsName $Domain `
            -CertStoreLocation "cert:\LocalMachine\My" `
            -KeyLength 2048 `
            -KeyAlgorithm RSA `
            -HashAlgorithm SHA256 `
            -KeyUsage DigitalSignature, KeyEncipherment `
            -NotAfter (Get-Date).AddYears(2) `
            -FriendlyName "Dropbox Organizer - Self Signed"

        Write-Host "  OK Certificado creado" -ForegroundColor Green
        Write-Host "  Thumbprint: $($cert.Thumbprint)" -ForegroundColor Gray
        Write-Host "  Valido hasta: $($cert.NotAfter)" -ForegroundColor Gray

    } catch {
        Write-Host "  ERROR creando certificado: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }

    Write-Host ""
    Write-Host "[2/3] Configurando binding HTTPS en IIS..." -ForegroundColor Green

    try {
        Import-Module WebAdministration -ErrorAction Stop

        $site = Get-Website | Select-Object -First 1

        if ($site) {
            # Remover binding HTTPS existente si existe
            $existingBinding = Get-WebBinding -Name $site.Name -Protocol "https" -Port 443
            if ($existingBinding) {
                Remove-WebBinding -Name $site.Name -Protocol "https" -Port 443
            }

            # Agregar nuevo binding
            New-WebBinding -Name $site.Name -Protocol "https" -Port 443 -HostHeader $Domain -SslFlags 0

            # Asociar certificado
            $binding = Get-WebBinding -Name $site.Name -Protocol "https" -Port 443
            $binding.AddSslCertificate($cert.Thumbprint, "my")

            Write-Host "  OK Binding HTTPS configurado en IIS" -ForegroundColor Green
            Write-Host "  Sitio: $($site.Name)" -ForegroundColor Gray
        } else {
            Write-Host "  ADVERTENCIA No se encontro sitio en IIS" -ForegroundColor Yellow
            Write-Host "  Deberas configurar el binding HTTPS manualmente" -ForegroundColor Yellow
        }

    } catch {
        Write-Host "  ADVERTENCIA No se pudo configurar IIS automaticamente" -ForegroundColor Yellow
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  Configura manualmente en IIS Manager:" -ForegroundColor Yellow
        Write-Host "    1. Site - Bindings - Add" -ForegroundColor Gray
        Write-Host "    2. Type: https, Port: 443" -ForegroundColor Gray
        Write-Host "    3. Seleccionar certificado: Dropbox Organizer - Self Signed" -ForegroundColor Gray
    }

    Write-Host ""
    Write-Host "[3/3] Exportando certificado (opcional)..." -ForegroundColor Green
    Write-Host "  Para confiar en este certificado en navegadores, puedes exportarlo:" -ForegroundColor Gray
    Write-Host "    certlm.msc - Personal - Certificates - Click derecho - Export" -ForegroundColor Gray
}

# ============================================================================
# RESUMEN FINAL
# ============================================================================

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  OK Instalacion SSL Completada" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

if (-not $SelfSigned) {
    Write-Host "Proximos pasos:" -ForegroundColor Yellow
    Write-Host "  1. Verificar que https://$Domain funciona" -ForegroundColor Gray
    Write-Host "  2. Configurar DROPBOX_REDIRECT_URI=https://$Domain/auth/dropbox/callback" -ForegroundColor Gray
    Write-Host "  3. Actualizar Dropbox App Console con la nueva Redirect URI" -ForegroundColor Gray
    Write-Host "  4. Probar flujo completo de OAuth" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Comandos utiles:" -ForegroundColor White
    Write-Host "  - Ver certificados: Get-ChildItem Cert:\LocalMachine\My" -ForegroundColor Gray
    Write-Host "  - Renovar manualmente: cd $winAcmePath; .\wacs.exe --renew" -ForegroundColor Gray
    Write-Host "  - Ver tareas programadas: Get-ScheduledTask -TaskName win-acme*" -ForegroundColor Gray
} else {
    Write-Host "IMPORTANTE: Certificado autofirmado instalado" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Este certificado NO funcionara para:" -ForegroundColor Yellow
    Write-Host "  - OAuth de Dropbox desde navegadores externos" -ForegroundColor Gray
    Write-Host "  - Navegadores sin agregar excepcion de seguridad" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Para produccion, usa Let's Encrypt:" -ForegroundColor Yellow
    Write-Host "  .\install-ssl-certificate.ps1 -Domain tudominio.com" -ForegroundColor Gray
}

Write-Host ""
