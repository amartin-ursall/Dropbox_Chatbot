# Ejecución en Segundo Plano - Dropbox AI Organizer

## Descripción

Este documento describe cómo ejecutar la aplicación Dropbox AI Organizer en segundo plano, permitiendo acceso por **IP:Puerto** desde cualquier dispositivo en la red local, sin necesidad de publicar la aplicación en internet.

## Requisitos Previos

- **Backend**: Python 3.8+ instalado
- **Frontend**: Node.js 16+ y npm instalado
- **Red**: Todos los dispositivos deben estar en la misma red local
- **Firewall**: Los puertos 8000 (backend) y 5173 (frontend) deben estar abiertos

## Configuración OAuth de Dropbox

Para que la autenticación OAuth funcione correctamente con acceso por IP, asegúrate de configurar la **URL de redirección** en tu aplicación de Dropbox:

1. Ve a https://www.dropbox.com/developers/apps
2. Selecciona tu aplicación
3. En "OAuth 2" → "Redirect URIs", añade:
   - `http://localhost:8000/auth/dropbox/callback` (para desarrollo local)
   - `http://TU_IP_LOCAL:8000/auth/dropbox/callback` (ejemplo: `http://192.168.0.75:8000/auth/dropbox/callback`)

## Scripts Disponibles

### Windows (PowerShell)

| Script | Descripción |
|--------|-------------|
| `start-background.ps1` | Inicia backend y frontend en segundo plano |
| `stop-background.ps1` | Detiene todos los servicios en ejecución |
| `status-background.ps1` | Muestra el estado de los servicios |

### Linux/Mac (Bash)

| Script | Descripción |
|--------|-------------|
| `start-background.sh` | Inicia backend y frontend en segundo plano |
| `stop-background.sh` | Detiene todos los servicios en ejecución |
| `status-background.sh` | Muestra el estado de los servicios |

## Uso

### Iniciar los Servicios

**Windows:**
```powershell
.\start-background.ps1
```

**Linux/Mac:**
```bash
chmod +x start-background.sh  # Solo la primera vez
./start-background.sh
```

El script realizará automáticamente:
1. Verificación de servicios en ejecución
2. Instalación de dependencias (si es necesario)
3. Detección de IP local
4. Inicio del backend (puerto 8000)
5. Inicio del frontend (puerto 5173)
6. Verificación de que ambos servicios respondan

**Salida esperada:**
```
================================================
  Dropbox AI Organizer - Background Start
================================================

[1/5] Verificando estado de servicios...
  [OK] Servicios no están ejecutándose

[2/5] Verificando dependencias...
  [OK] Dependencias verificadas

[3/5] Configurando acceso de red...
  [*] IP Local detectada: 192.168.0.75

[4/5] Iniciando Backend (FastAPI)...
  [*] Backend iniciado (PID: 12345)
  [OK] Backend listo en http://192.168.0.75:8000

[5/5] Iniciando Frontend (Vite + React)...
  [*] Frontend iniciado (PID: 12346)
  [OK] Frontend listo en http://192.168.0.75:5173

================================================
  SERVICIOS INICIADOS CORRECTAMENTE
================================================

Accede a la aplicación desde:
  Frontend: http://192.168.0.75:5173
  Backend:  http://192.168.0.75:8000
  API Docs: http://192.168.0.75:8000/docs

Desde otros dispositivos en la red:
  http://192.168.0.75:5173
```

### Verificar Estado

**Windows:**
```powershell
.\status-background.ps1
```

**Linux/Mac:**
```bash
./status-background.sh
```

**Ejemplo de salida:**
```
================================================
  Dropbox AI Organizer - Service Status
================================================

Backend (FastAPI):
  Estado:  EJECUTÁNDOSE
  PID:     12345
  Puerto:  8000
  URL:     http://192.168.0.75:8000
  Docs:    http://192.168.0.75:8000/docs

Frontend (Vite + React):
  Estado:  EJECUTÁNDOSE
  PID:     12346
  Puerto:  5173
  URL:     http://192.168.0.75:5173

================================================
  TODOS LOS SERVICIOS EJECUTÁNDOSE
================================================

Acceso desde la red:
  http://192.168.0.75:5173
```

### Detener los Servicios

**Windows:**
```powershell
.\stop-background.ps1
```

**Linux/Mac:**
```bash
./stop-background.sh
```

El script detendrá:
- Procesos principales (backend y frontend)
- Procesos hijos (uvicorn, vite, node)
- Procesos residuales en los puertos 8000 y 5173
- Limpiará archivos PID y temporales

## Acceso desde Otros Dispositivos

Una vez iniciados los servicios, cualquier dispositivo en la misma red puede acceder a la aplicación.

### Desde un navegador

Abre cualquier navegador y accede a:
```
http://TU_IP_LOCAL:5173
```

Ejemplo:
```
http://192.168.0.75:5173
```

### Desde un móvil/tablet

1. Conecta el dispositivo a la misma red WiFi
2. Abre el navegador
3. Navega a `http://TU_IP_LOCAL:5173`

## Archivos Generados

### Archivos PID

Los scripts generan archivos para controlar los procesos:

- `.backend.pid` - ID del proceso del backend
- `.frontend.pid` - ID del proceso del frontend

**No elimines estos archivos manualmente**. Usa `stop-background` para detener los servicios correctamente.

### Logs

Los logs se guardan en el directorio `logs/` con timestamp:

```
logs/
├── backend_20250117_143022.log
├── frontend_20250117_143022.log
├── backend_20250117_150134.log
└── frontend_20250117_150134.log
```

Para ver logs en tiempo real:

**Windows:**
```powershell
Get-Content logs\backend_TIMESTAMP.log -Wait -Tail 50
```

**Linux/Mac:**
```bash
tail -f logs/backend_TIMESTAMP.log
```

## Configuración de Red

### Configuración CORS

El backend está configurado para aceptar peticiones de cualquier origen cuando no se especifica `FRONTEND_URLS` en las variables de entorno:

```python
# backend/app/main.py
if not FRONTEND_URLS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Permite acceso desde cualquier IP
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
```

### Frontend sin HTTPS

Para acceso por IP, el frontend se ejecuta en **HTTP** (no HTTPS):

```bash
# Variables de entorno configuradas automáticamente
VITE_USE_HTTPS=false
VITE_BACKEND_URL=http://TU_IP_LOCAL:8000
```

### Puertos Utilizados

| Servicio | Puerto | Protocolo |
|----------|--------|-----------|
| Backend  | 8000   | HTTP      |
| Frontend | 5173   | HTTP      |

## Configuración del Firewall

### Windows Firewall

Si el firewall bloquea las conexiones, añade reglas para los puertos:

```powershell
# Permitir puerto 8000 (Backend)
New-NetFirewallRule -DisplayName "Dropbox Organizer Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow

# Permitir puerto 5173 (Frontend)
New-NetFirewallRule -DisplayName "Dropbox Organizer Frontend" -Direction Inbound -LocalPort 5173 -Protocol TCP -Action Allow
```

### Linux (UFW)

```bash
sudo ufw allow 8000/tcp
sudo ufw allow 5173/tcp
sudo ufw reload
```

### macOS

macOS generalmente permite conexiones entrantes. Si hay problemas:

1. Ve a **Preferencias del Sistema** → **Seguridad y Privacidad** → **Firewall**
2. Haz clic en **Opciones del firewall**
3. Añade Python y Node.js a las aplicaciones permitidas

## Solución de Problemas

### Los servicios no inician

**Verificar dependencias:**
```bash
# Backend
cd backend
python --version  # Debe ser 3.8+
pip list | grep fastapi

# Frontend
cd frontend
node --version  # Debe ser 16+
npm --version
```

**Verificar puertos ocupados:**

**Windows:**
```powershell
netstat -ano | findstr ":8000"
netstat -ano | findstr ":5173"
```

**Linux/Mac:**
```bash
lsof -i :8000
lsof -i :5173
```

### No puedo acceder desde otro dispositivo

1. **Verifica que ambos dispositivos estén en la misma red:**
   ```bash
   # Desde el servidor
   ipconfig  # Windows
   ifconfig  # Mac
   ip addr   # Linux
   ```

2. **Prueba hacer ping desde el otro dispositivo:**
   ```bash
   ping 192.168.0.75
   ```

3. **Verifica el firewall** (ver sección anterior)

4. **Verifica que los servicios estén escuchando en 0.0.0.0:**
   ```bash
   # Backend debe mostrar: 0.0.0.0:8000
   # Frontend debe mostrar: 0.0.0.0:5173
   ```

### Error de OAuth / Redirect URI mismatch

Si obtienes un error de autenticación de Dropbox:

1. Ve a https://www.dropbox.com/developers/apps
2. Edita tu aplicación
3. En "Redirect URIs", asegúrate de tener:
   - `http://localhost:8000/auth/dropbox/callback`
   - `http://TU_IP_REAL:8000/auth/dropbox/callback`
4. Guarda los cambios
5. Reinicia los servicios

### Los logs no se generan

Verifica que el directorio `logs/` exista:

**Windows:**
```powershell
if (!(Test-Path "logs")) { New-Item -ItemType Directory -Path "logs" }
```

**Linux/Mac:**
```bash
mkdir -p logs
```

### Procesos zombies después de detener

Si `stop-background` no detiene todos los procesos:

**Windows:**
```powershell
# Buscar y matar procesos manualmente
Get-Process | Where-Object {$_.ProcessName -like "*python*" -or $_.ProcessName -like "*node*"}
Stop-Process -Name python,node -Force
```

**Linux/Mac:**
```bash
# Buscar procesos
ps aux | grep -E "uvicorn|vite|node"

# Matar por puerto
kill -9 $(lsof -ti:8000)
kill -9 $(lsof -ti:5173)
```

## Diferencias con el Modo de Desarrollo Normal

| Aspecto | Desarrollo Normal | Segundo Plano (IP) |
|---------|-------------------|-------------------|
| HTTPS | Sí (con certificado autofirmado) | No (HTTP simple) |
| Dominio | dropboxaiorganizer.com | IP:Puerto |
| Ventanas | 2 ventanas de terminal visibles | Sin ventanas, segundo plano |
| Logs | En terminal | Archivos en `logs/` |
| Acceso red | Posible pero con warnings SSL | Directo sin warnings |
| Control | Ctrl+C en terminales | Scripts stop/status |

## Seguridad

### Recomendaciones

1. **Usa esta configuración solo en redes confiables** (casa, oficina privada)
2. **No expongas los puertos a internet** (8000, 5173)
3. **Mantén actualizado el archivo `.env`** con credenciales seguras
4. **No compartas tu IP pública** con los puertos abiertos
5. **Considera usar una VPN** si necesitas acceso desde fuera de la red local

### Para Producción

Esta configuración es para **desarrollo y uso interno**. Para producción:

1. Usa HTTPS con certificados válidos (Let's Encrypt)
2. Configura un proxy reverso (nginx, Apache)
3. Implementa autenticación adicional
4. Usa variables de entorno para URLs específicas
5. Considera servicios como Heroku, AWS, o Azure

## Actualizar la Aplicación

Cuando actualices el código:

1. Detén los servicios:
   ```bash
   ./stop-background.ps1  # Windows
   ./stop-background.sh   # Linux/Mac
   ```

2. Actualiza el código (git pull, etc.)

3. Actualiza dependencias si es necesario:
   ```bash
   # Backend
   cd backend
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt

   # Frontend
   cd frontend
   npm install
   ```

4. Reinicia los servicios:
   ```bash
   ./start-background.ps1  # Windows
   ./start-background.sh   # Linux/Mac
   ```

## Comandos Rápidos

### Cheat Sheet

```bash
# Iniciar
.\start-background.ps1   # Windows
./start-background.sh    # Linux/Mac

# Estado
.\status-background.ps1  # Windows
./status-background.sh   # Linux/Mac

# Detener
.\stop-background.ps1    # Windows
./stop-background.sh     # Linux/Mac

# Ver logs en tiempo real
Get-Content logs\backend_*.log -Wait -Tail 50  # Windows
tail -f logs/backend_*.log                     # Linux/Mac

# Verificar puertos
netstat -ano | findstr ":8000"                 # Windows
lsof -i :8000                                  # Linux/Mac

# Reiniciar servicios
.\stop-background.ps1 && .\start-background.ps1   # Windows
./stop-background.sh && ./start-background.sh     # Linux/Mac
```

## Soporte

Para problemas o preguntas:

1. Revisa los logs en `logs/`
2. Ejecuta `status-background` para verificar el estado
3. Consulta la documentación principal en `CLAUDE.md`
4. Revisa la documentación de URSALL en `docs/URSALL_IMPLEMENTATION.md`
