# Configuración de Acceso desde Red

Esta guía explica cómo acceder a la aplicación Dropbox AI Organizer desde cualquier dispositivo en tu red local.

## ✅ Configuración Completada

La aplicación está completamente configurada para acceso desde red:

### Puertos Configurados
- **Frontend**: Puerto `5173` - `http://dropboxaiorganizer.com:5173`
- **Backend**: Puerto `8000` - `http://dropboxaiorganizer.com:8000`

### Archivos Modificados
- ✅ `frontend/.env.development` - Puerto 5173 y URL del backend
- ✅ `frontend/vite.config.ts` - Host 0.0.0.0 + CORS habilitado
- ✅ `backend/app/main.py` - CORS configurado para dropboxaiorganizer.com:5173
- ✅ `backend/.env` - Variables de entorno para red
- ✅ `scripts/start-dev.bat` - Script de inicio actualizado (Windows)
- ✅ `scripts/start-dev.sh` - Script de inicio actualizado (Linux/Mac)
- ✅ `scripts/start-prod.bat` - Script de producción actualizado (Windows)
- ✅ `scripts/start-prod.sh` - Script de producción actualizado (Linux/Mac)

## 🚀 Cómo Usar

### 1. Configurar el Servidor (Máquina que ejecuta la aplicación)

#### a. Obtener la IP del servidor
**Windows:**
```bash
ipconfig
```
Busca "IPv4 Address" (ej: 192.168.1.100)

**Linux/Mac:**
```bash
ip addr show
# o
ifconfig
```
Busca "inet" (ej: 192.168.1.100)

#### b. Configurar archivo hosts en el SERVIDOR
**Windows:** `C:\Windows\System32\drivers\etc\hosts`
**Linux/Mac:** `/etc/hosts`

Añade esta línea:
```
TU_IP_LOCAL dropboxaiorganizer.com
```

Ejemplo:
```
192.168.1.100 dropboxaiorganizer.com
```

#### c. Iniciar la aplicación
**Windows:**
```bash
cd scripts
start-dev.bat
```

**Linux/Mac:**
```bash
cd scripts
./start-dev.sh
```

### 2. Configurar Dispositivos Clientes (Otros equipos en la red)

Cada dispositivo que quiera acceder debe configurar su archivo hosts:

#### Windows
1. Abrir Notepad como Administrador
2. Abrir: `C:\Windows\System32\drivers\etc\hosts`
3. Añadir al final:
   ```
   192.168.1.100 dropboxaiorganizer.com
   ```
   (Reemplaza 192.168.1.100 con la IP del servidor)
4. Guardar

#### Linux/Mac
```bash
sudo nano /etc/hosts
```
Añadir:
```
192.168.1.100 dropboxaiorganizer.com
```
Guardar con Ctrl+X, Y, Enter

#### Android
1. Requiere root o app de hosts (no recomendado para usuarios no técnicos)
2. Alternativa: Usar la IP directamente (ver sección "Sin configurar hosts")

#### iOS
1. Requiere jailbreak (no recomendado)
2. Alternativa: Usar la IP directamente (ver sección "Sin configurar hosts")

### 3. Acceder desde el Cliente

Abrir navegador y acceder a:
```
http://dropboxaiorganizer.com:5173
```

## 🔧 Alternativa: Acceso Directo por IP (Sin configurar hosts)

Si no quieres o no puedes modificar el archivo hosts en los clientes, puedes acceder directamente usando la IP:

```
http://192.168.1.100:5173
```
(Reemplaza con tu IP del servidor)

**Nota:** Esta opción puede causar problemas con CORS si el backend no está configurado para aceptar la IP directa.

## 📱 URLs de Acceso

Una vez configurado, puedes acceder desde cualquier dispositivo:

### Acceso Local (en el servidor)
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

### Acceso desde Red (cualquier dispositivo)
- Frontend: `http://dropboxaiorganizer.com:5173`
- Backend: `http://dropboxaiorganizer.com:8000`
- API Docs: `http://dropboxaiorganizer.com:8000/docs`

## 🔥 Verificar Firewall

Asegúrate de que el firewall permite el tráfico en los puertos 5173 y 8000:

### Windows
```bash
# Permitir puerto 5173
netsh advfirewall firewall add rule name="Dropbox AI Frontend" dir=in action=allow protocol=TCP localport=5173

# Permitir puerto 8000
netsh advfirewall firewall add rule name="Dropbox AI Backend" dir=in action=allow protocol=TCP localport=8000
```

### Linux (ufw)
```bash
sudo ufw allow 5173/tcp
sudo ufw allow 8000/tcp
```

### Linux (firewalld)
```bash
sudo firewall-cmd --permanent --add-port=5173/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

## ⚠️ Troubleshooting

### No puedo acceder desde otro dispositivo

1. **Verificar que ambos dispositivos están en la misma red**
   ```bash
   ping 192.168.1.100
   ```

2. **Verificar firewall** (ver sección anterior)

3. **Verificar archivo hosts** en el cliente:
   - Windows: `type C:\Windows\System32\drivers\etc\hosts`
   - Linux/Mac: `cat /etc/hosts`

4. **Verificar que los servidores están escuchando en 0.0.0.0**
   ```bash
   # Windows
   netstat -an | findstr "5173"
   netstat -an | findstr "8000"

   # Linux/Mac
   netstat -tulpn | grep 5173
   netstat -tulpn | grep 8000
   ```

### Error CORS

Si ves errores CORS en la consola del navegador:
1. Verifica que `backend/.env` tiene las URLs correctas en `FRONTEND_URLS`
2. Reinicia el backend
3. Limpia la caché del navegador

### No resuelve dropboxaiorganizer.com

1. Verifica el archivo hosts:
   ```bash
   # Windows
   ping dropboxaiorganizer.com

   # Linux/Mac
   ping dropboxaiorganizer.com
   ```

2. Si el ping falla, revisa el archivo hosts y asegúrate de que la IP es correcta

## 🔒 Seguridad

**IMPORTANTE:** Esta configuración es solo para redes locales privadas.

**NO expongas estos puertos a Internet sin:**
- Configurar HTTPS con certificados válidos
- Implementar autenticación robusta
- Configurar un firewall adecuado
- Usar un proxy inverso (nginx, Apache)

## 📚 Más Información

- [HTTPS_SETUP.md](./HTTPS_SETUP.md) - Configurar HTTPS
- [PRODUCTION_DEPLOYMENT.md](./PRODUCTION_DEPLOYMENT.md) - Despliegue en producción
- [README.md](../README.md) - Documentación principal
