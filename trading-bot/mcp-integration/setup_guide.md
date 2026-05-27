# Guía de Setup: Claude + TradingView MCP

## Arquitectura completa

```
TradingView Desktop
    ↕ Chrome DevTools Protocol (CDP, puerto 9222)
tradingview-mcp (Node.js server)
    ↕ Model Context Protocol
Claude Code (CLI)
    ↕ Archivos locales
trading-bot/ (Python)
    ↕ WebSocket
Binance + Polymarket
```

---

## Paso 1: Instalar TradingView Desktop

Descarga desde: https://www.tradingview.com/desktop/

> Requiere suscripción de pago para datos en tiempo real.
> La versión gratuita funciona con retraso de 15 minutos.

---

## Paso 2: Instalar el MCP Server

```bash
# Clonar el repositorio
git clone https://github.com/tradesdontlie/tradingview-mcp.git
cd tradingview-mcp
npm install

# Verificar que funciona
node src/server.js --help
```

---

## Paso 3: Configurar Claude Code

Edita (o crea) el archivo `~/.claude/.mcp.json` en tu máquina local:

```json
{
  "mcpServers": {
    "tradingview": {
      "command": "node",
      "args": ["/RUTA/ABSOLUTA/tradingview-mcp/src/server.js"]
    }
  }
}
```

**Reemplaza `/RUTA/ABSOLUTA/tradingview-mcp`** con la ruta real donde clonaste el repo.

Ejemplo macOS: `/Users/tuusuario/projects/tradingview-mcp/src/server.js`
Ejemplo Windows: `C:\\Users\\tuusuario\\projects\\tradingview-mcp\\src\\server.js`

---

## Paso 4: Lanzar TradingView con CDP

**macOS:**
```bash
/Applications/TradingView.app/Contents/MacOS/TradingView --remote-debugging-port=9222
```

**Windows (PowerShell):**
```powershell
& "$env:LOCALAPPDATA\Programs\TradingView\TradingView.exe" --remote-debugging-port=9222
```

**Atajo:** Usa el script incluido:
```bash
chmod +x launch_tradingview.sh
./launch_tradingview.sh
```

---

## Paso 5: Iniciar Claude Code

```bash
# En la carpeta del proyecto
cd /ruta/a/Myweb
claude
```

Al iniciar, Claude verá las herramientas `tradingview.*` disponibles.

**Verificar conexión:**
```
> Ejecuta tv_health_check para verificar que TradingView está conectado
```

---

## Paso 6: Primeras Pruebas

### Test 1: Leer el gráfico
```
¿Qué símbolo y precio está mostrando TradingView ahora mismo?
```

### Test 2: Cambiar símbolo
```
Cambia el gráfico a BTCUSDT en timeframe 15 minutos
```

### Test 3: Inyectar Pine Script
```
Inyecta en el gráfico un indicador simple que muestre la EMA 20 y EMA 50
```

### Test 4: Análisis completo
```
Analiza el gráfico actual con metodología SMC y dame el setup
```

---

## Paso 7 (Opcional): Conectar a Broker para Ejecución Real

### Opción A: 3Commas (más fácil)
1. Crea cuenta en 3commas.io
2. Crea un bot DCA/Signal
3. Copia el webhook URL del bot
4. En el Pine Script `Webhook_Executor.pine`, pon ese URL como destino

### Opción B: Bybit Direct
1. Ve a Bybit → API Management → Crea API key
2. Configura un servidor de webhooks (puede ser un VPS con Flask/FastAPI)
3. El servidor recibe el JSON de TradingView y ejecuta via Bybit API

### Opción C: Alpaca (para acciones/crypto)
1. Crea cuenta en alpaca.markets (paper trading gratis)
2. Usa el webhook para llamar a la API de Alpaca directamente

---

## Troubleshooting

| Problema | Solución |
|---|---|
| `tv_health_check` falla | TradingView no está corriendo con --remote-debugging-port=9222 |
| "Connection refused port 9222" | Cierra TradingView y relánzalo con el script |
| Pine Script no compila | Lee el error con `tv_compile_pine_script` y pídele a Claude que lo corrija |
| Claude no ve las herramientas TV | Verifica que `~/.claude/.mcp.json` tiene la ruta correcta |
| Datos con retraso | Necesitas suscripción de pago en TradingView |

---

## Flujo Diario Recomendado

```
08:50 UTC  → Lanzar launch_tradingview.sh
08:55 UTC  → Iniciar Claude: "Dame el morning brief"
09:00 UTC  → Inicio London Killzone → monitoreo activo
10:00 UTC  → Fin London → revisar trades abiertos
13:25 UTC  → Pre-NY → "Analiza el gráfico actual para NY open"
13:30 UTC  → Inicio NY Killzone → buscar setups
16:00 UTC  → Fin NY → cerrar sesión
16:05 UTC  → "Dame resumen de la sesión: trades, PnL, setup perdidos"
```
