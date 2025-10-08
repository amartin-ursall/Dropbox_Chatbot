# Guía de Despliegue en Producción

Esta guía te ayudará a desplegar la aplicación para que se acceda como `https://dropboxaiorganizer.com` sin puerto visible y sin advertencias de seguridad.

## 📋 Requisitos Previos

### 1. Dominio Configurado
- Tener el dominio `dropboxaiorganizar.com` registrado
- Configurar el DNS para apuntar a tu servidor:
  ```
  A Record: dropboxaiorganizer.com → [IP de tu servidor]
  ```

### 2. Certificado SSL Real
Para que el navegador no muestre advertencias, necesitas un certificado SSL de una autoridad certificadora válida.

#### Opción A: Let's Encrypt (Gratuito) - Recomendado

**En Linux/Ubuntu:**
```bash
# Instalar Certbot
sudo apt update
sudo apt install certbot

# Generar certificado
sudo certbot certonly --standalone -d dropboxaiorganizer.com

# Los certificados se guardarán en:
# /etc/letsencrypt/live/dropboxaiorganizer.com/fullchain.pem
# /etc/letsencrypt/live/dropboxaiorganizer.com/privkey.pem
```

**Copiar certificados al proyecto:**
```bash
cd /path/to/Dropbox_Chatbot/frontend/ssl

# Copiar certificados (requiere sudo)
sudo cp /etc/letsencrypt/live/dropboxaiorganizer.com/fullchain.pem ./cert.pem
sudo cp /etc/letsencrypt/live/dropboxaiorganizer.com/privkey.pem ./key.pem

# Dar permisos de lectura
sudo chmod 644 cert.pem
sudo chmod 600 key.pem
```

#### Opción B: Certificado de Proveedor de Hosting

Si usas proveedores como:
- **Cloudflare** → Usar SSL/TLS automático + proxy
- **AWS** → Amazon Certificate Manager (ACM)
- **Azure** → Azure Key Vault
- **DigitalOcean** → Certificados gestionados

## 🚀 Configuración de Producción

### 1. Actualizar Archivo Hosts (Solo para Desarrollo Local)

**Para producción real en servidor:** No necesitas esto, el DNS hará el trabajo.

**Para pruebas locales con certificado real:**
```
# Windows: C:\Windows\System32\drivers\etc\hosts
# Linux/Mac: /etc/hosts

127.0.0.1 dropboxaiorganizer.com
```

### 2. Configurar Variables de Entorno

#### Backend (`backend/.env`)
```bash
# URLs del Frontend
FRONTEND_URL=https://dropboxaiorganizer.com
FRONTEND_URLS=https://dropboxaiorganizer.com

# Credenciales Dropbox
DROPBOX_APP_KEY=tu_app_key_aqui
DROPBOX_APP_SECRET=tu_app_secret_aqui

# API Key de Gemini
GEMINI_API_KEY=tu_gemini_key_aqui
```

#### Frontend (Usar `.env.production`)
Ya está configurado en `frontend/.env.production`:
```bash
VITE_USE_HTTPS=true
VITE_PORT=443
VITE_BACKEND_URL=http://localhost:8000
```

### 3. Configurar OAuth de Dropbox

**IMPORTANTE:** Actualiza la configuración de tu app en Dropbox:

1. Ve a https://www.dropbox.com/developers/apps
2. Selecciona tu aplicación
3. En **Redirect URIs**, añade:
   ```
   https://dropboxaiorganizer.com/auth/dropbox/callback
   ```
4. Guarda los cambios

### 4. Iniciar la Aplicación

#### Windows - Modo Producción

**Opción 1: Script automático (Requiere permisos de Administrador)**
```cmd
# Clic derecho → Ejecutar como Administrador
start-prod.bat
```

**Opción 2: Manual**
```cmd
# Terminal 1 - Backend
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend (como Administrador)
cd frontend
npm run dev -- --mode production
```

#### Linux/Mac - Modo Producción

```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend (requiere sudo para puerto 443)
cd frontend
sudo npm run dev -- --mode production
```

### 5. Acceder a la Aplicación

Una vez iniciado, accede a:
- **Frontend:** https://dropboxaiorganizer.com
- **Backend API:** http://localhost:8000/docs

**¡Sin puerto en la URL!** Usa el puerto 443 (estándar HTTPS) para que no aparezca.

## 🔒 Verificación de Seguridad

### Comprobar que el Certificado es Válido

1. Abre https://dropboxaiorganizer.com en el navegador
2. Haz clic en el candado 🔒 en la barra de direcciones
3. Verifica:
   - ✅ **Conexión segura**
   - ✅ **Certificado válido** (emitido por autoridad certificadora)
   - ✅ **Sin advertencias**

### Comprobar Conexión Backend

```bash
curl https://dropboxaiorganizer.com/api/health
```

Debería responder sin errores SSL.

## 🌐 Despliegue en Servidor Real

### Opción 1: Nginx como Reverse Proxy (Recomendado)

**Instalar Nginx:**
```bash
sudo apt update
sudo apt install nginx
```

**Configurar Nginx (`/etc/nginx/sites-available/dropboxaiorganizer`):**
```nginx
server {
    listen 80;
    server_name dropboxaiorganizer.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name dropboxaiorganizer.com;

    ssl_certificate /etc/letsencrypt/live/dropboxaiorganizer.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dropboxaiorganizer.com/privkey.pem;

    # Frontend (Vite build estático)
    location / {
        root /var/www/dropboxaiorganizer/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /auth/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Activar configuración:**
```bash
sudo ln -s /etc/nginx/sites-available/dropboxaiorganizer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Build del Frontend:**
```bash
cd frontend
npm run build
sudo cp -r dist/* /var/www/dropboxaiorganizer/
```

**Iniciar Backend:**
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Opción 2: Docker

**Crear `docker-compose.yml`:**
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - FRONTEND_URL=https://dropboxaiorganizer.com
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "443:443"
    depends_on:
      - backend
    volumes:
      - ./frontend/ssl:/app/ssl
```

**Iniciar:**
```bash
docker-compose up -d
```

### Opción 3: Servicio Systemd (Linux)

**Backend (`/etc/systemd/system/dropbox-backend.service`):**
```ini
[Unit]
Description=Dropbox AI Organizer Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/dropboxaiorganizer/backend
Environment="PATH=/var/www/dropboxaiorganizer/backend/venv/bin"
ExecStart=/var/www/dropboxaiorganizer/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Activar servicio:**
```bash
sudo systemctl enable dropbox-backend
sudo systemctl start dropbox-backend
sudo systemctl status dropbox-backend
```

## 🔧 Solución de Problemas

### Error: "Puerto 443 ya en uso"
```bash
# Ver qué proceso usa el puerto 443
# Windows
netstat -ano | findstr :443
taskkill /F /PID [PID]

# Linux
sudo lsof -i :443
sudo kill [PID]
```

### Error: "Permission denied" en puerto 443
- **Causa:** Los puertos < 1024 requieren permisos de administrador
- **Solución Windows:** Ejecutar como Administrador
- **Solución Linux:** Usar `sudo` o configurar capabilities:
  ```bash
  sudo setcap 'cap_net_bind_service=+ep' /usr/bin/node
  ```

### Certificado no confiable
- Asegúrate de usar certificado de Let's Encrypt o CA válida
- Renovar certificados expirados:
  ```bash
  sudo certbot renew
  ```

### CORS errors
- Verifica que `FRONTEND_URL` en el backend coincida con la URL real
- Comprueba que `FRONTEND_URLS` incluye el dominio correcto

## 📱 Cloudflare (Alternativa Simple)

Si usas Cloudflare:

1. Añade tu dominio a Cloudflare
2. Activa **SSL/TLS → Full (strict)**
3. Cloudflare proporciona certificado SSL automáticamente
4. Configura tu servidor para HTTP en puerto 8080
5. Cloudflare manejará HTTPS externamente

**Ventajas:**
- ✅ SSL gratis y automático
- ✅ CDN global
- ✅ Protección DDoS
- ✅ Sin configurar certificados manualmente

## ✅ Checklist Final

Antes de lanzar a producción:

- [ ] Certificado SSL instalado de CA válida
- [ ] DNS apunta al servidor correcto
- [ ] Variables de entorno configuradas
- [ ] OAuth Redirect URIs actualizados en Dropbox
- [ ] Puerto 443 accesible (firewall abierto)
- [ ] Backend corriendo en puerto 8000
- [ ] Frontend compilado y sirviendo
- [ ] CORS configurado correctamente
- [ ] Probado desde navegador externo
- [ ] No aparecen advertencias de seguridad

## 🎉 Resultado Final

Al completar estos pasos:
- ✅ **URL limpia:** `https://dropboxaiorganizer.com` (sin puerto)
- ✅ **Conexión segura:** Candado verde en navegador
- ✅ **Sin advertencias:** Certificado válido
- ✅ **Comunicación segura:** Frontend ↔️ Backend correctamente configurado
