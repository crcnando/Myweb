# Cómo Conectar Tu Cuenta de TradingView a Claude

Existen DOS métodos. Elige según lo que tengas:

---

## MÉTODO A — TradingView Desktop (Recomendado)
**No necesitas dar usuario ni contraseña a Claude.**
Simplemente abres la app ya logueada y la expones por el puerto de depuración.

### ¿Cuándo usar este método?
- Tienes la app de escritorio de TradingView instalada
- Ya estás logueado en la app

### Paso 1: Lanzar TradingView con CDP
Cierra TradingView si está abierto. Luego lánzalo así:

**macOS:**
```bash
/Applications/TradingView.app/Contents/MacOS/TradingView --remote-debugging-port=9222
```

**Windows (PowerShell como Administrador):**
```powershell
& "$env:LOCALAPPDATA\TradingView\TradingView.exe" --remote-debugging-port=9222
```

**Linux:**
```bash
/opt/TradingView/tradingview --remote-debugging-port=9222
```

### Paso 2: Instalar el MCP server
```bash
git clone https://github.com/tradesdontlie/tradingview-mcp.git
cd tradingview-mcp
npm install
```

### Paso 3: Configurar Claude Code
Edita `~/.claude/.mcp.json` (créalo si no existe):

```json
{
  "mcpServers": {
    "tradingview": {
      "command": "node",
      "args": ["/Users/TU_USUARIO/tradingview-mcp/src/server.js"]
    }
  }
}
```

### Paso 4: Reiniciar Claude Code
```bash
claude
# Luego escribe: "Ejecuta tv_health_check"
```

**Cómo funciona por dentro:**
```
TradingView Desktop (ya logueado con tu cuenta)
         ↕  puerto 9222 (solo local, no sale a internet)
    tradingview-mcp (Node.js)
         ↕  MCP Protocol
    Claude Code
```

Claude lee tu sesión activa. No guarda ni envía tus credenciales a ningún lado.

---

## MÉTODO B — Sin App de Escritorio (Web via Playwright)
**Necesitas dar tu usuario y contraseña. Se guardan solo en tu máquina.**

### ¿Cuándo usar este método?
- No tienes la app de escritorio
- Solo tienes acceso al sitio web de TradingView

### Paso 1: Instalar

**Opción Docker (más fácil):**
```bash
# Autenticar una sola vez (guarda la sesión en un volumen)
docker run --rm \
  -v tradingview-mcp-session:/data \
  -e TV_USERNAME=tu@email.com \
  -e TV_PASSWORD=tu_contraseña \
  -e TV_SESSION_FILE=/data/.tv_session.json \
  mikeh1975/tradingview-mcp:login
```

Esto abre un Chromium invisible, hace login en tradingview.com y guarda las cookies.
La sesión dura ~25 días. Después repites este comando.

**Opción Node.js local:**
```bash
git clone https://github.com/mikeh-22/tradingview-mcp.git
cd tradingview-mcp
npm install
npx playwright install chromium
npm run build
```

### Paso 2: Configurar Claude Desktop

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

**Con Docker:**
```json
{
  "mcpServers": {
    "tradingview": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-v", "tradingview-mcp-session:/data",
        "-e", "TV_SESSION_FILE=/data/.tv_session.json",
        "mikeh1975/tradingview-mcp:latest"
      ]
    }
  }
}
```

**Con Node.js local:**
```json
{
  "mcpServers": {
    "tradingview": {
      "command": "node",
      "args": ["/ruta/tradingview-mcp/dist/index.js"],
      "env": {
        "TV_USERNAME": "tu@email.com",
        "TV_PASSWORD": "tu_contraseña"
      }
    }
  }
}
```

### Paso 3: Reiniciar Claude y verificar
```
> Ejecuta tv_health_check para confirmar la conexión
```

---

## Comparación Rápida

| | Método A (Desktop) | Método B (Web/Playwright) |
|---|---|---|
| Necesita app instalada | Sí | No |
| Credenciales en config | No | Sí |
| Datos en tiempo real | Sí (según tu plan) | Sí (según tu plan) |
| Velocidad | Más rápido | Más lento (headless browser) |
| 78 herramientas MCP | Sí | Menos herramientas |
| Funciona en servidor/VPS | No | Sí |

---

## Verificar que Funciona

Una vez configurado, escríbele a Claude:

```
Usa tv_health_check para confirmar que TradingView está conectado.
Luego dime qué símbolo y precio está mostrando el gráfico ahora mismo.
```

Si responde con el símbolo y precio actual: **todo está funcionando.**

---

## Seguridad

- Las credenciales del Método B se guardan **solo en tu máquina local**
- La comunicación es **local** (localhost:9222) — no sale a internet
- No compartas tu archivo `claude_desktop_config.json` ni el `.tv_session.json`
- Si usas el Método B en un VPS, asegura el acceso con firewall
