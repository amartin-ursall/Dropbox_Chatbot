#!/bin/bash
# =============================================================================
# Dropbox AI Organizer - Status Check
# =============================================================================

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

echo -e "${CYAN}================================================${NC}"
echo -e "${CYAN}  Dropbox AI Organizer - Service Status${NC}"
echo -e "${CYAN}================================================${NC}"
echo ""

# Obtener directorio del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Archivos PID
BACKEND_PID_FILE="$SCRIPT_DIR/.backend.pid"
FRONTEND_PID_FILE="$SCRIPT_DIR/.frontend.pid"

check_port() {
    local port=$1
    if command -v nc &> /dev/null; then
        nc -z localhost $port 2>/dev/null
        return $?
    elif command -v netstat &> /dev/null; then
        netstat -tuln | grep ":$port " &> /dev/null
        return $?
    else
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

backend_running=false
frontend_running=false
LOCAL_IP=$(get_local_ip)

# =============================================================================
# VERIFICAR BACKEND
# =============================================================================

echo -e "${YELLOW}Backend (FastAPI):${NC}"

if [ -f "$BACKEND_PID_FILE" ]; then
    BACKEND_PID=$(cat "$BACKEND_PID_FILE")

    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        backend_running=true
        echo -e "  Estado:  ${GREEN}EJECUTÁNDOSE${NC}"
        echo -e "  ${GRAY}PID:     $BACKEND_PID${NC}"
        echo -e "  ${GRAY}Puerto:  8000${NC}"

        if check_port 8000; then
            echo -e "  ${CYAN}URL:     http://$LOCAL_IP:8000${NC}"
            echo -e "  ${CYAN}Docs:    http://$LOCAL_IP:8000/docs${NC}"
        else
            echo -e "  ${RED}Estado:  Puerto 8000 no responde${NC}"
        fi
    else
        echo -e "  Estado:  ${RED}DETENIDO${NC}"
        echo -e "  ${GRAY}Info:    Archivo PID existe pero proceso no encontrado${NC}"
    fi
else
    echo -e "  Estado:  ${RED}DETENIDO${NC}"
fi

# =============================================================================
# VERIFICAR FRONTEND
# =============================================================================

echo ""
echo -e "${YELLOW}Frontend (Vite + React):${NC}"

if [ -f "$FRONTEND_PID_FILE" ]; then
    FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")

    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        frontend_running=true
        echo -e "  Estado:  ${GREEN}EJECUTÁNDOSE${NC}"
        echo -e "  ${GRAY}PID:     $FRONTEND_PID${NC}"
        echo -e "  ${GRAY}Puerto:  5173${NC}"

        if check_port 5173; then
            echo -e "  ${CYAN}URL:     http://$LOCAL_IP:5173${NC}"
        else
            echo -e "  ${RED}Estado:  Puerto 5173 no responde${NC}"
        fi
    else
        echo -e "  Estado:  ${RED}DETENIDO${NC}"
        echo -e "  ${GRAY}Info:    Archivo PID existe pero proceso no encontrado${NC}"
    fi
else
    echo -e "  Estado:  ${RED}DETENIDO${NC}"
fi

# =============================================================================
# RESUMEN Y LOGS
# =============================================================================

echo ""
echo -e "${CYAN}================================================${NC}"

if [ "$backend_running" = true ] && [ "$frontend_running" = true ]; then
    echo -e "${GREEN}  TODOS LOS SERVICIOS EJECUTÁNDOSE${NC}"
    echo ""
    echo -e "${WHITE}Acceso desde la red:${NC}"
    echo -e "  ${YELLOW}http://$LOCAL_IP:5173${NC}"
elif [ "$backend_running" = true ] || [ "$frontend_running" = true ]; then
    echo -e "${YELLOW}  ALGUNOS SERVICIOS EJECUTÁNDOSE${NC}"
else
    echo -e "${RED}  TODOS LOS SERVICIOS DETENIDOS${NC}"
    echo ""
    echo -e "${WHITE}Para iniciar los servicios:${NC}"
    echo -e "  ${GRAY}./start-background.sh${NC}"
fi

echo -e "${CYAN}================================================${NC}"

# Mostrar logs recientes si existen
LOGS_DIR="$SCRIPT_DIR/logs"
if [ -d "$LOGS_DIR" ]; then
    latest_logs=$(ls -t "$LOGS_DIR"/*.log 2>/dev/null | head -n 2)
    if [ ! -z "$latest_logs" ]; then
        echo ""
        echo -e "${WHITE}Logs recientes:${NC}"
        echo "$latest_logs" | while read log; do
            echo -e "  ${GRAY}$(basename $log)${NC}"
        done
    fi
fi

echo ""
