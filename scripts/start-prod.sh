#!/bin/bash

echo "========================================"
echo "Starting Dropbox AI Organizer (Production Mode)"
echo "========================================"
echo ""

# Check if running as root (needed for port 443)
if [ "$EUID" -ne 0 ]; then
    echo "❌ ERROR: This script must be run as root to use port 443"
    echo "Please run: sudo ./start-prod.sh"
    exit 1
fi

# Check hosts file configuration
if ! grep -q "dropboxaiorganizer.com" /etc/hosts; then
    echo "⚠️  WARNING: dropboxaiorganizer.com not found in /etc/hosts!"
    echo "Please add this line to /etc/hosts:"
    echo "127.0.0.1 dropboxaiorganizer.com"
    echo ""
    read -p "Press Enter to continue anyway..."
fi

echo "Starting Backend..."
cd ../backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 3

echo "Starting Frontend (Production Mode on port 443)..."
cd ../frontend
npm run dev -- --mode production &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "Servers started in PRODUCTION mode!"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: https://dropboxaiorganizer.com"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop all servers"
echo "========================================"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
