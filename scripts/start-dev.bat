@echo off
echo ========================================
echo Starting Dropbox AI Organizer (Development)
echo ========================================
echo.

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
start "Backend Server" cmd /k "cd ..\backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3

echo Starting Frontend...
start "Frontend Server" cmd /k "cd ..\frontend && npm run dev"

echo.
echo ========================================
echo Servers starting...
echo.
echo Backend:  http://localhost:8000
echo          http://dropboxaiorganizer.com:8000
echo Frontend: http://localhost:5173
echo          http://dropboxaiorganizer.com:5173
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C in each window to stop
echo ========================================
