#!/bin/bash

echo "========================================"
echo "Starting Dropbox AI Organizer (Production Mode)"
echo "Network Access Enabled"
echo "========================================"
echo ""

# Check hosts file configuration
if ! grep -q "dropboxaiorganizer.com" /etc/hosts; then
    echo "⚠️  WARNING: dropboxaiorganizer.com not found in /etc/hosts!"
    echo ""
    echo "To enable network access, add this line to /etc/hosts:"
    echo ""
    echo "For local access only:"
    echo "127.0.0.1 dropboxaiorganizer.com"
    echo ""
    echo "For network access (recommended):"
    echo "YOUR_LOCAL_IP dropboxaiorganizer.com"
    echo "(Replace YOUR_LOCAL_IP with your machine's IP, e.g., 192.168.1.100)"
    echo ""
    echo "To find your IP: ip addr show (look for inet address)"
    echo ""
    read -p "Press Enter to continue anyway..."
fi

echo ""
echo "Checking dependencies..."
echo ""

echo "[1/3] Checking Frontend dependencies..."
cd ../frontend
if [ ! -d "node_modules" ]; then
    echo "Installing Frontend dependencies..."
    npm install
else
    echo "Frontend dependencies already installed (skipping)"
fi

echo ""
echo "[2/3] Checking Backend dependencies..."
cd ../backend
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo "Installing Backend dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "Backend virtual environment already exists (skipping)"
fi

echo ""
echo "[3/3] Starting servers..."

echo ""
echo "Starting Backend on port 8000 (Production Mode)..."
cd ../backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 3

echo "Starting Frontend on port 5173 (Production Mode)..."
cd ../frontend
npm run dev -- --mode production &
FRONTEND_PID=$!

sleep 2

echo ""
echo "========================================"
echo "Servers started successfully (PRODUCTION)!"
echo "========================================"
echo ""
echo "LOCAL ACCESS:"
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "NETWORK ACCESS (from any device):"
echo "  Frontend: http://dropboxaiorganizer.com:5173"
echo "  Backend:  http://dropboxaiorganizer.com:8000"
echo "  API Docs: http://dropboxaiorganizer.com:8000/docs"
echo ""
echo "Note: Other devices must have dropboxaiorganizer.com"
echo "      pointing to this machine's IP in their /etc/hosts"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop all servers"
echo "========================================"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
