#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# Lanza TradingView Desktop con el puerto de depuración CDP abierto.
# DEBE ejecutarse ANTES de iniciar Claude Code.
# ─────────────────────────────────────────────────────────────────────────────

DEBUGGING_PORT=9222

# Detectar OS y ejecutar TradingView correctamente
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    TV_PATH="/Applications/TradingView.app/Contents/MacOS/TradingView"
    if [ ! -f "$TV_PATH" ]; then
        echo "TradingView no encontrado en $TV_PATH"
        echo "Buscando..."
        TV_PATH=$(find /Applications -name "TradingView" -type f 2>/dev/null | head -1)
    fi
    "$TV_PATH" --remote-debugging-port=$DEBUGGING_PORT &

elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows (Git Bash / PowerShell)
    TV_PATH="$LOCALAPPDATA\\Programs\\TradingView\\TradingView.exe"
    start "" "$TV_PATH" --remote-debugging-port=$DEBUGGING_PORT

elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    tradingview --remote-debugging-port=$DEBUGGING_PORT &
fi

echo "TradingView lanzado con CDP en puerto $DEBUGGING_PORT"
echo "Espera 5 segundos antes de iniciar Claude Code..."
sleep 5
echo "Listo. Ahora puedes iniciar: claude"
