#!/bin/bash
# =============================================================================
# Dropbox AI Organizer - Stop Background Services
# =============================================================================

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

echo -e "${CYAN}================================================${NC}"
echo -e "${CYAN}  Dropbox AI Organizer - Stop Services${NC}"
echo -e "${CYAN}================================================${NC}"
echo ""

# Obtener directorio del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Archivos PID
BACKEND_PID_FILE="$SCRIPT_DIR/.backend.pid"
FRONTEND_PID_FILE="$SCRIPT_DIR/.frontend.pid"

stopped=false

# =============================================================================
# DETENER BACKEND
# =============================================================================

echo -e "${YELLOW}[1/2] Deteniendo Backend...${NC}"

if [ -f "$BACKEND_PID_FILE" ]; then
    BACKEND_PID=$(cat "$BACKEND_PID_FILE")

    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo -e "${GRAY}  [*] Deteniendo proceso Backend (PID: $BACKEND_PID)...${NC}"

        # Obtener procesos hijos
        CHILD_PIDS=$(pgrep -P $BACKEND_PID 2>/dev/null)

        # Detener proceso principal
        kill $BACKEND_PID 2>/dev/null

        # Esperar un momento
        sleep 1

        # Forzar si aún está corriendo
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            kill -9 $BACKEND_PID 2>/dev/null
        fi

        # Detener procesos hijos
        if [ ! -z "$CHILD_PIDS" ]; then
            echo "$CHILD_PIDS" | xargs kill 2>/dev/null
            sleep 1
            echo "$CHILD_PIDS" | xargs kill -9 2>/dev/null
        fi

        echo -e "${GREEN}  [OK] Backend detenido${NC}"
        stopped=true
    else
        echo -e "${YELLOW}  [!] Proceso Backend no encontrado (ya estaba detenido)${NC}"
    fi

    rm -f "$BACKEND_PID_FILE"
else
    echo -e "${YELLOW}  [!] Backend no está ejecutándose${NC}"
fi

# =============================================================================
# DETENER FRONTEND
# =============================================================================

echo ""
echo -e "${YELLOW}[2/2] Deteniendo Frontend...${NC}"

if [ -f "$FRONTEND_PID_FILE" ]; then
    FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")

    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo -e "${GRAY}  [*] Deteniendo proceso Frontend (PID: $FRONTEND_PID)...${NC}"

        # Obtener procesos hijos
        CHILD_PIDS=$(pgrep -P $FRONTEND_PID 2>/dev/null)

        # Detener proceso principal
        kill $FRONTEND_PID 2>/dev/null

        # Esperar un momento
        sleep 1

        # Forzar si aún está corriendo
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            kill -9 $FRONTEND_PID 2>/dev/null
        fi

        # Detener procesos hijos
        if [ ! -z "$CHILD_PIDS" ]; then
            echo "$CHILD_PIDS" | xargs kill 2>/dev/null
            sleep 1
            echo "$CHILD_PIDS" | xargs kill -9 2>/dev/null
        fi

        echo -e "${GREEN}  [OK] Frontend detenido${NC}"
        stopped=true
    else
        echo -e "${YELLOW}  [!] Proceso Frontend no encontrado (ya estaba detenido)${NC}"
    fi

    rm -f "$FRONTEND_PID_FILE"
else
    echo -e "${YELLOW}  [!] Frontend no está ejecutándose${NC}"
fi

# =============================================================================
# LIMPIEZA ADICIONAL
# =============================================================================

echo ""
echo -e "${GRAY}Limpiando procesos residuales...${NC}"

# Buscar y matar procesos de uvicorn en puerto 8000
if command -v lsof &> /dev/null; then
    UVICORN_PIDS=$(lsof -ti:8000 2>/dev/null)
    if [ ! -z "$UVICORN_PIDS" ]; then
        echo "$UVICORN_PIDS" | xargs kill -9 2>/dev/null
        echo -e "${GRAY}  [*] Procesos uvicorn detenidos${NC}"
        stopped=true
    fi

    # Buscar y matar procesos de vite/node en puerto 5173
    VITE_PIDS=$(lsof -ti:5173 2>/dev/null)
    if [ ! -z "$VITE_PIDS" ]; then
        echo "$VITE_PIDS" | xargs kill -9 2>/dev/null
        echo -e "${GRAY}  [*] Procesos vite/node detenidos${NC}"
        stopped=true
    fi
fi

# Limpiar archivos nohup.out si existen
rm -f "$SCRIPT_DIR/nohup.out" 2>/dev/null
rm -f "$BACKEND_DIR/nohup.out" 2>/dev/null
rm -f "$FRONTEND_DIR/nohup.out" 2>/dev/null

# =============================================================================
# RESUMEN
# =============================================================================

echo ""
echo -e "${CYAN}================================================${NC}"
if [ "$stopped" = true ]; then
    echo -e "${GREEN}  SERVICIOS DETENIDOS${NC}"
else
    echo -e "${YELLOW}  NO HAY SERVICIOS EJECUTÁNDOSE${NC}"
fi
echo -e "${CYAN}================================================${NC}"
echo ""
