# Configuración OAuth de Dropbox para Producción

## ⚠️ Problema: OAuth de Dropbox requiere HTTPS con dominio real

Dropbox OAuth **NO funciona** desde ordenadores externos con:
- ❌ IPs locales (192.168.x.x)
- ❌ HTTP (sin certificado SSL)
- ❌ localhost o dominios falsos en hosts file

**Dropbox OAuth SÍ funciona** con:
- ✅ Dominio real registrado (ej: `tudominio.com`)
- ✅ HTTPS con certificado SSL válido
- ✅ URLs accesibles públicamente

## 📋 Soluciones Recomendadas

### Opción 1: Túnel Local (Desarrollo - Más Rápido)

Usa **ngrok** o **cloudflare tunnel** para exponer tu servidor local con HTTPS:

#### Con ngrok (Recomendado para desarrollo):

1. **Instalar ngrok:**
   - Descarga de: https://ngrok.com/download
   - Registrate gratis: https://dashboard.ngrok.com/signup

2. **Ejecutar ngrok:**
   ```bash
   # Frontend en puerto 5173
   ngrok http 5173

   # En otra terminal, backend en puerto 8000
   ngrok http 8000
   ```

3. **Copiar las URLs generadas:**
   ```
   Frontend: https://abc123.ngrok.io
   Backend:  https://xyz456.ngrok.io
   ```

4. **Configurar en Dropbox App Console:**
   - Redirect URI: `https://xyz456.ngrok.io/auth/dropbox/callback`

5. **Actualizar `backend/.env`:**
   ```env
   DROPBOX_REDIRECT_URI=https://xyz456.ngrok.io/auth/dropbox/callback
   FRONTEND_URL=https://abc123.ngrok.io
   FRONTEND_URLS=https://abc123.ngrok.io,http://localhost:5173
   ```

6. **Actualizar `frontend/.env.development`:**
   ```env
   VITE_BACKEND_URL=https://xyz456.ngrok.io
   ```

**Ventajas:**
- ✅ Configuración en minutos
- ✅ HTTPS automático
- ✅ Accesible desde cualquier dispositivo
- ✅ Gratis para desarrollo

**Desventajas:**
- ⚠️ La URL cambia cada vez que reinicias ngrok (puedes pagar por URL fija)

---

### Opción 2: Cloudflare Tunnel (Desarrollo - Gratis y Permanente)

1. **Instalar cloudflared:**
   - Windows: https://github.com/cloudflare/cloudflared/releases
   - Descargar `cloudflared-windows-amd64.exe`

2. **Autenticarse:**
   ```bash
   cloudflared tunnel login
   ```

3. **Crear túnel:**
   ```bash
   cloudflared tunnel create dropbox-organizer
   ```

4. **Configurar túnel** (crear `config.yml`):
   ```yaml
   tunnel: dropbox-organizer
   credentials-file: C:\Users\TU_USUARIO\.cloudflared\TUNNEL_ID.json

   ingress:
     - hostname: dropbox-backend.tu-dominio.com
       service: http://localhost:8000
     - hostname: dropbox-frontend.tu-dominio.com
       service: http://localhost:5173
     - service: http_status:404
   ```

5. **Ejecutar túnel:**
   ```bash
   cloudflared tunnel run dropbox-organizer
   ```

**Ventajas:**
- ✅ URL permanente (no cambia)
- ✅ HTTPS automático
- ✅ Gratis
- ✅ Más confiable que ngrok

---

### Opción 3: Servidor VPS (Producción Real)

Para producción, necesitas:

1. **Dominio registrado** (ej: desde Namecheap, GoDaddy)
2. **Servidor VPS** (ej: DigitalOcean, AWS, Azure)
3. **Certificado SSL** (gratis con Let's Encrypt)
4. **Nginx o Apache** como reverse proxy

**Pasos:**

1. **Comprar dominio** (ej: `dropboxorganizer.com`)

2. **Configurar DNS** apuntando a tu servidor VPS:
   ```
   A    @                   -> IP_DEL_VPS
   A    api                 -> IP_DEL_VPS
   CNAME www               -> dropboxorganizer.com
   ```

3. **Instalar certificado SSL:**
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot --nginx -d dropboxorganizer.com -d api.dropboxorganizer.com
   ```

4. **Configurar Nginx:**
   ```nginx
   # Frontend
   server {
       listen 443 ssl;
       server_name dropboxorganizer.com;

       ssl_certificate /etc/letsencrypt/live/dropboxorganizer.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/dropboxorganizer.com/privkey.pem;

       location / {
           proxy_pass http://localhost:5173;
       }
   }

   # Backend
   server {
       listen 443 ssl;
       server_name api.dropboxorganizer.com;

       ssl_certificate /etc/letsencrypt/live/dropboxorganizer.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/dropboxorganizer.com/privkey.pem;

       location / {
           proxy_pass http://localhost:8000;
       }
   }
   ```

5. **Configurar en Dropbox:**
   - Redirect URI: `https://api.dropboxorganizer.com/auth/dropbox/callback`

6. **Actualizar variables de entorno:**
   ```env
   # backend/.env
   DROPBOX_REDIRECT_URI=https://api.dropboxorganizer.com/auth/dropbox/callback
   FRONTEND_URL=https://dropboxorganizer.com

   # frontend/.env.production
   VITE_BACKEND_URL=https://api.dropboxorganizer.com
   ```

---

## 🔧 Configuración Actual del Proyecto

### Para Desarrollo Local (Red Local):

**Configuración actual:**
- Frontend: `http://192.168.0.98:5173`
- Backend: `http://192.168.0.98:8000`

**Problema:** Dropbox OAuth NO funcionará desde otros dispositivos porque requiere HTTPS.

**Solución recomendada:** Usa **ngrok** (Opción 1) para desarrollo.

---

## 📝 Resumen de Pasos Recomendados

### Para Desarrollo/Pruebas (Más rápido):

1. Instalar ngrok
2. Ejecutar:
   ```bash
   ngrok http 8000
   ngrok http 5173
   ```
3. Copiar URLs HTTPS generadas
4. Configurar Dropbox App Console con la URL del backend
5. Actualizar `.env` con las URLs de ngrok
6. Reiniciar servidores

### Para Producción:

1. Comprar dominio
2. Contratar VPS
3. Instalar certificado SSL (Let's Encrypt)
4. Configurar Nginx/Apache
5. Desplegar aplicación
6. Configurar Dropbox con dominio real

---

## 🚨 Importante

**Dropbox NO acepta:**
- URLs con puerto (ej: `https://ejemplo.com:8000`) ❌
- IPs públicas sin dominio ❌

**Dropbox SÍ acepta:**
- `https://ejemplo.com/auth/dropbox/callback` ✅
- `https://api.ejemplo.com/auth/dropbox/callback` ✅
- `https://subdominio.ejemplo.com/auth/dropbox/callback` ✅

Por eso en producción deberás:
- Usar Nginx para que el backend esté en el puerto 443 (HTTPS estándar)
- O usar un subdominio (ej: `api.tudominio.com`)
