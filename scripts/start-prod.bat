@echo off
echo ========================================
echo Starting Dropbox AI Organizer (Production Mode)
echo ========================================
echo.

echo NOTE: You must run this as Administrator to use port 443
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: This script requires Administrator privileges to run on port 443
    echo Please right-click and select "Run as Administrator"
    pause
    exit /b 1
)

echo Checking hosts file configuration...
findstr /C:"dropboxaiorganizer.com" C:\Windows\System32\drivers\etc\hosts >nul
if %errorlevel% neq 0 (
    echo WARNING: dropboxaiorganizer.com not found in hosts file!
    echo Please add this line to C:\Windows\System32\drivers\etc\hosts:
    echo 127.0.0.1 dropboxaiorganizer.com
    echo.
    pause
)

echo Starting Backend...
start "Backend Server" cmd /k "cd ..\backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

timeout /t 3

echo Starting Frontend (Production Mode)...
start "Frontend Server" cmd /k "cd ..\frontend && npm run dev -- --mode production"

echo.
echo ========================================
echo Servers starting in PRODUCTION mode...
echo.
echo Backend:  http://localhost:8000
echo Frontend: https://dropboxaiorganizer.com
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C in each window to stop
echo ========================================
