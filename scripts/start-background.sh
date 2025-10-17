#!/bin/bash
# =============================================================================
# Dropbox AI Organizer - Start Background Services
# =============================================================================
# Este script inicia el backend y frontend en segundo plano para acceso por IP
# No se requiere dominio, acceso directo por IP:Puerto

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

echo -e "${CYAN}================================================${NC}"
echo -e "${CYAN}  Dropbox AI Organizer - Background Start${NC}"
echo -e "${CYAN}================================================${NC}"
echo ""

# Obtener directorio del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Directorios
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
LOGS_DIR="$SCRIPT_DIR/logs"

# Crear directorio de logs si no existe
mkdir -p "$LOGS_DIR"

# Archivos de log con timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKEND_LOG="$LOGS_DIR/backend_$TIMESTAMP.log"
FRONTEND_LOG="$LOGS_DIR/frontend_$TIMESTAMP.log"

# Archivos PID para control de procesos
BACKEND_PID_FILE="$SCRIPT_DIR/.backend.pid"
FRONTEND_PID_FILE="$SCRIPT_DIR/.frontend.pid"

# =============================================================================
# FUNCIONES
# =============================================================================

check_port() {
    local port=$1
    if command -v nc &> /dev/null; then
        nc -z localhost $port 2>/dev/null
        return $?
    elif command -v netstat &> /dev/null; then
        netstat -tuln | grep ":$port " &> /dev/null
        return $?
    else
        # Fallback: intentar conectar con bash
        (echo > /dev/tcp/localhost/$port) &>/dev/null
        return $?
    fi
}

get_local_ip() {
    # Detectar sistema operativo
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n1)
    else
        # Linux
        LOCAL_IP=$(hostname -I | awk '{print $1}')
    fi

    if [ -z "$LOCAL_IP" ]; then
        LOCAL_IP="127.0.0.1"
    fi

    echo "$LOCAL_IP"
}

# =============================================================================
# VERIFICAR SI YA ESTÁ EJECUTÁNDOSE
# =============================================================================

echo -e "${YELLOW}[1/5] Verificando estado de servicios...${NC}"

if [ -f "$BACKEND_PID_FILE" ]; then
    BACKEND_PID=$(cat "$BACKEND_PID_FILE")
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo -e "${RED}  [!] Backend ya está ejecutándose (PID: $BACKEND_PID)${NC}"
        echo -e "${RED}  [!] Use './stop-background.sh' para detenerlo primero${NC}"
        exit 1
    else
        rm -f "$BACKEND_PID_FILE"
    fi
fi

if [ -f "$FRONTEND_PID_FILE" ]; then
    FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo -e "${RED}  [!] Frontend ya está ejecutándose (PID: $FRONTEND_PID)${NC}"
        echo -e "${RED}  [!] Use './stop-background.sh' para detenerlo primero${NC}"
        exit 1
    else
        rm -f "$FRONTEND_PID_FILE"
    fi
fi

echo -e "${GREEN}  [OK] Servicios no están ejecutándose${NC}"

# =============================================================================
# INSTALAR DEPENDENCIAS SI ES NECESARIO
# =============================================================================

echo ""
echo -e "${YELLOW}[2/5] Verificando dependencias...${NC}"

# Backend - Python
cd "$BACKEND_DIR"
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}  [!] Creando entorno virtual de Python...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate
echo -e "${GRAY}  [*] Verificando paquetes Python...${NC}"
pip install -q -r requirements.txt

# Frontend - Node
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}  [!] Instalando dependencias de Node.js...${NC}"
    npm install --silent
fi

echo -e "${GREEN}  [OK] Dependencias verificadas${NC}"

# =============================================================================
# OBTENER IP LOCAL
# =============================================================================

echo ""
echo -e "${YELLOW}[3/5] Configurando acceso de red...${NC}"

LOCAL_IP=$(get_local_ip)
echo -e "${CYAN}  [*] IP Local detectada: $LOCAL_IP${NC}"

# =============================================================================
# INICIAR BACKEND
# =============================================================================

echo ""
echo -e "${YELLOW}[4/5] Iniciando Backend (FastAPI)...${NC}"

cd "$BACKEND_DIR"
source venv/bin/activate

# Iniciar backend en segundo plano
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "$BACKEND_PID_FILE"

echo -e "${GREEN}  [*] Backend iniciado (PID: $BACKEND_PID)${NC}"
echo -e "${GRAY}  [*] Log: $BACKEND_LOG${NC}"

# Esperar a que el backend esté listo
echo -e -n "${GRAY}  [*] Esperando a que el backend esté listo...${NC}"
attempts=0
max_attempts=30
while ! check_port 8000 && [ $attempts -lt $max_attempts ]; do
    sleep 1
    attempts=$((attempts + 1))
    echo -n "."
done
echo ""

if check_port 8000; then
    echo -e "${GREEN}  [OK] Backend listo en http://$LOCAL_IP:8000${NC}"
else
    echo -e "${RED}  [!] Backend no responde. Revisa el log.${NC}"
    exit 1
fi

# =============================================================================
# INICIAR FRONTEND
# =============================================================================

echo ""
echo -e "${YELLOW}[5/5] Iniciando Frontend (Vite + React)...${NC}"

cd "$FRONTEND_DIR"

# Configurar variables de entorno para frontend
export VITE_USE_HTTPS=false
export VITE_BACKEND_URL="http://$LOCAL_IP:8000"

# Iniciar frontend en segundo plano
nohup npm run dev > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$FRONTEND_PID_FILE"

echo -e "${GREEN}  [*] Frontend iniciado (PID: $FRONTEND_PID)${NC}"
echo -e "${GRAY}  [*] Log: $FRONTEND_LOG${NC}"

# Esperar a que el frontend esté listo
echo -e -n "${GRAY}  [*] Esperando a que el frontend esté listo...${NC}"
attempts=0
max_attempts=45
while ! check_port 5173 && [ $attempts -lt $max_attempts ]; do
    sleep 1
    attempts=$((attempts + 1))
    echo -n "."
done
echo ""

if check_port 5173; then
    echo -e "${GREEN}  [OK] Frontend listo en http://$LOCAL_IP:5173${NC}"
else
    echo -e "${RED}  [!] Frontend no responde. Revisa el log.${NC}"
fi

# =============================================================================
# RESUMEN
# =============================================================================

echo ""
echo -e "${CYAN}================================================${NC}"
echo -e "${GREEN}  SERVICIOS INICIADOS CORRECTAMENTE${NC}"
echo -e "${CYAN}================================================${NC}"
echo ""
echo -e "Accede a la aplicación desde:"
echo -e "  ${CYAN}Frontend: http://$LOCAL_IP:5173${NC}"
echo -e "  ${CYAN}Backend:  http://$LOCAL_IP:8000${NC}"
echo -e "  ${CYAN}API Docs: http://$LOCAL_IP:8000/docs${NC}"
echo ""
echo -e "Desde otros dispositivos en la red:"
echo -e "  ${YELLOW}http://$LOCAL_IP:5173${NC}"
echo ""
echo -e "Control de servicios:"
echo -e "  ${GRAY}Detener:  ./stop-background.sh${NC}"
echo -e "  ${GRAY}Estado:   ./status-background.sh${NC}"
echo -e "  ${GRAY}Logs:     $LOGS_DIR${NC}"
echo ""
echo -e "Procesos en segundo plano:"
echo -e "  ${GRAY}Backend PID:  $BACKEND_PID${NC}"
echo -e "  ${GRAY}Frontend PID: $FRONTEND_PID${NC}"
echo ""

# Volver al directorio original
cd "$SCRIPT_DIR"
