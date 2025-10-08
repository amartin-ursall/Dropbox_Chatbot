# HTTPS Configuration Setup

Esta aplicación está configurada para ejecutarse con HTTPS en el dominio `dropboxaiorganizer.com` **sin puerto visible** (puerto 443 estándar).

> ⚠️ **Para despliegue en producción completo**, consulta [PRODUCTION_DEPLOYMENT.md](./PRODUCTION_DEPLOYMENT.md)

## Configuration Steps

### 1. SSL Certificates
✅ Self-signed SSL certificates have been generated in `frontend/ssl/`:
- `cert.pem` - Certificate file
- `key.pem` - Private key file

**Note:** These are self-signed certificates for development. For production, use certificates from Let's Encrypt or a trusted CA.

### 2. Update Hosts File (Required)

Since `dropboxaiorganizer.com` needs to point to localhost, you must update your hosts file:

**Windows:**
1. Open Notepad as Administrator
2. Open file: `C:\Windows\System32\drivers\etc\hosts`
3. Add this line:
   ```
   127.0.0.1 dropboxaiorganizer.com
   ```
4. Save the file

**Linux/Mac:**
1. Open terminal
2. Edit hosts file: `sudo nano /etc/hosts`
3. Add this line:
   ```
   127.0.0.1 dropboxaiorganizer.com
   ```
4. Save and exit

### 3. Trust the SSL Certificate (Optional but Recommended)

To avoid browser security warnings:

**Windows:**
1. Double-click `frontend/ssl/cert.pem`
2. Click "Install Certificate"
3. Choose "Local Machine"
4. Select "Place all certificates in the following store"
5. Browse and select "Trusted Root Certification Authorities"
6. Complete the wizard

**Mac:**
1. Open Keychain Access
2. File → Import Items → Select `frontend/ssl/cert.pem`
3. Double-click the certificate in Keychain
4. Expand "Trust" section
5. Set "When using this certificate" to "Always Trust"

**Linux:**
```bash
sudo cp frontend/ssl/cert.pem /usr/local/share/ca-certificates/dropboxaiorganizer.crt
sudo update-ca-certificates
```

### 4. Start the Application

#### Opción A: Scripts Automáticos (Recomendado)

**Para Desarrollo (puerto 5173):**
```cmd
start-dev.bat
```

**Para Producción-like (puerto 443 - Requiere Administrador):**
```cmd
# Clic derecho → Ejecutar como Administrador
start-prod.bat
```

#### Opción B: Manual

**Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (Desarrollo - Puerto 5173):**
```bash
cd frontend
npm run dev
```

**Frontend (Producción - Puerto 443, Requiere Administrador):**
```bash
cd frontend
npm run dev -- --mode production
```

### 5. Access the Application

**Modo Desarrollo:**
- Frontend: `https://dropboxaiorganizer.com:5173`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

**Modo Producción (Puerto 443):**
- Frontend: `https://dropboxaiorganizer.com` (¡SIN PUERTO!)
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

## Configuration Details

### Vite Configuration
- Host: `dropboxaiorganizer.com`
- Port: `5173`
- HTTPS enabled with SSL certificates
- Proxy configured for `/api` and `/auth` endpoints to backend

### Backend CORS Configuration
Allowed origins:
- `http://localhost:5173` (development fallback)
- `https://localhost:5173` (local HTTPS)
- `https://dropboxaiorganizer.com:5173` (main domain)
- `https://dropboxaiorganizer.com` (production)

### API Proxy
The Vite dev server proxies API requests:
- `https://dropboxaiorganizer.com:5173/api/*` → `http://localhost:8000/api/*`
- `https://dropboxaiorganizer.com:5173/auth/*` → `http://localhost:8000/auth/*`

This ensures secure frontend-to-backend communication.

## Production Deployment

For production deployment:

1. **Get a Real SSL Certificate:**
   - Use Let's Encrypt (free): `certbot certonly --standalone -d dropboxaiorganizer.com`
   - Or use your SSL provider

2. **Update Vite Config:**
   Replace self-signed certificates with production certificates

3. **Configure DNS:**
   Point `dropboxaiorganizer.com` to your server's IP address

4. **Enable HTTPS on Backend:**
   Consider using a reverse proxy like Nginx or run uvicorn with SSL:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --ssl-keyfile=./ssl/key.pem --ssl-certfile=./ssl/cert.pem
   ```

5. **Update Environment Variables:**
   Set appropriate CORS origins for production

## Troubleshooting

**Browser shows "Not Secure" warning:**
- Trust the self-signed certificate (see Step 3 above)
- Or proceed anyway (click Advanced → Proceed)

**Cannot connect to dropboxaiorganizer.com:**
- Check hosts file configuration
- Verify Vite dev server is running
- Check firewall settings

**CORS errors:**
- Verify backend CORS configuration includes your origin
- Check that backend server is running on port 8000

**Certificate errors:**
- Regenerate certificates if needed:
  ```bash
  cd frontend/ssl
  openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=ES/ST=State/L=City/O=Organization/CN=dropboxaiorganizer.com"
  ```
