@echo off
echo ========================================
echo Dropbox AI Organizer - Setup con ngrok
echo OAuth funcional desde cualquier dispositivo
echo ========================================
echo.

echo PASO 1: Verifica que ngrok este instalado
echo.
where ngrok >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: ngrok no esta instalado
    echo.
    echo Descargalo desde: https://ngrok.com/download
    echo Registrate gratis en: https://dashboard.ngrok.com/signup
    echo.
    pause
    exit /b 1
)

echo [OK] ngrok encontrado
echo.

echo ========================================
echo PASO 2: Inicia los servidores locales
echo ========================================
echo.

echo Iniciando Backend en puerto 8000...
start "Backend (Port 8000)" cmd /k "cd ..\backend && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

echo Iniciando Frontend en puerto 5173...
start "Frontend (Port 5173)" cmd /k "cd ..\frontend && npm run dev"

timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo PASO 3: Inicia los tuneles ngrok
echo ========================================
echo.

echo Creando tunel para Backend (puerto 8000)...
start "ngrok Backend" cmd /k "ngrok http 8000"

timeout /t 2 /nobreak >nul

echo Creando tunel para Frontend (puerto 5173)...
start "ngrok Frontend" cmd /k "ngrok http 5173"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo CONFIGURACION COMPLETADA
echo ========================================
echo.
echo Se han abierto 4 ventanas:
echo   1. Backend local (puerto 8000)
echo   2. Frontend local (puerto 5173)
echo   3. ngrok Backend (tunel HTTPS)
echo   4. ngrok Frontend (tunel HTTPS)
echo.
echo ========================================
echo SIGUIENTE: Configura las URLs de ngrok
echo ========================================
echo.
echo 1. Mira las ventanas de ngrok y copia las URLs HTTPS
echo    Ejemplo: https://abc123.ngrok.io
echo.
echo 2. Actualiza backend/.env:
echo    DROPBOX_REDIRECT_URI=https://TU_URL_BACKEND_NGROK/auth/dropbox/callback
echo    FRONTEND_URL=https://TU_URL_FRONTEND_NGROK
echo.
echo 3. Actualiza frontend/.env.development:
echo    VITE_BACKEND_URL=https://TU_URL_BACKEND_NGROK
echo.
echo 4. Configura Dropbox App Console:
echo    https://www.dropbox.com/developers/apps
echo    Redirect URI: https://TU_URL_BACKEND_NGROK/auth/dropbox/callback
echo.
echo 5. Reinicia los servidores (Ctrl+C y vuelve a ejecutar)
echo.
echo Ver guia completa: docs/OAUTH_PRODUCTION_SETUP.md
echo.
echo ========================================
pause
