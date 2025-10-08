@echo off
echo ========================================
echo Starting Dropbox AI Organizer (Development)
echo Network Access Enabled
echo ========================================
echo.

echo Checking hosts file configuration...
findstr /C:"dropboxaiorganizer.com" C:\Windows\System32\drivers\etc\hosts >nul
if %errorlevel% neq 0 (
    echo WARNING: dropboxaiorganizer.com not found in hosts file!
    echo.
    echo To enable network access, add this line to:
    echo C:\Windows\System32\drivers\etc\hosts
    echo.
    echo For local access only:
    echo 127.0.0.1 dropboxaiorganizer.com
    echo.
    echo For network access (recommended):
    echo YOUR_LOCAL_IP dropboxaiorganizer.com
    echo (Replace YOUR_LOCAL_IP with your machine's IP, e.g., 192.168.1.100)
    echo.
    echo To find your IP: ipconfig (look for IPv4 Address)
    echo.
    pause
)

echo.
echo Starting Backend on port 8000...
start "Backend Server (Port 8000)" cmd /k "cd ..\backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo Starting Frontend on port 5173...
start "Frontend Server (Port 5173)" cmd /k "cd ..\frontend && npm run dev"

timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo Servers starting successfully!
echo ========================================
echo.
echo LOCAL ACCESS:
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo NETWORK ACCESS (from any device):
echo   Frontend: http://dropboxaiorganizer.com:5173
echo   Backend:  http://dropboxaiorganizer.com:8000
echo   API Docs: http://dropboxaiorganizer.com:8000/docs
echo.
echo Note: Other devices must have dropboxaiorganizer.com
echo       pointing to this machine's IP in their hosts file
echo.
echo Press Ctrl+C in each window to stop the servers
echo ========================================
