# Prompts de Workflow para Claude + TradingView MCP

Estos son los prompts exactos que le das a Claude una vez conectado.
Cópialos y pégalos directamente.

---

## SETUP INICIAL (ejecutar una vez)

```
Verifica la conexión a TradingView con tv_health_check.
Luego lee el símbolo actual, timeframe, y los indicadores activos.
Dame un resumen del estado del gráfico.
```

---

## ANÁLISIS COMPLETO DE MERCADO

```
Analiza el gráfico actual siguiendo el protocolo SMC:
1. Lee el precio y OHLC con tv_get_symbol_info
2. Obtén los valores de todos los indicadores activos
3. Identifica la tendencia en HTF (cambia a 4H, lee estructura, vuelve al original)
4. Determina el último BOS o CHoCH
5. Ubica el Order Block o FVG más cercano al precio actual
6. Define el setup: entrada, SL, TP1, TP2
7. Da una calificación del setup: A (excelente), B (bueno), C (marginal), D (no operar)
```

---

## INYECTAR ESTRATEGIA SMC

```
Lee el archivo trading-bot/tradingview/SMC_LiquidityBot.pine
e inyéctalo en el gráfico actual usando tv_inject_pine_script.
Si hay errores de compilación, corrígelos automáticamente.
Confirma cuando esté activo.
```

---

## CREAR PINE SCRIPT PERSONALIZADO

```
Escribe un indicador Pine Script v5 que haga lo siguiente:
[DESCRIBE LO QUE QUIERES AQUÍ]

Requisitos mínimos:
- Compatible con Pine Script v5
- Incluye alertas via alert()
- Muestra tabla de estadísticas en la esquina
- Usa colores: verde para largos, rojo para cortos, gris para neutro

Después de escribirlo, inyéctalo con tv_inject_pine_script y compílalo.
```

---

## CONFIGURAR ALERTA CON WEBHOOK

```
Basándote en el análisis actual del gráfico, crea una alerta en TradingView
usando tv_create_alert con estos parámetros:
- Condición: [la señal del setup actual]
- Webhook URL: [TU_WEBHOOK_URL]
- Mensaje JSON:
{
  "action": "{{strategy.order.action}}",
  "symbol": "{{ticker}}",
  "price": {{close}},
  "sl": [SL calculado],
  "tp1": [TP1 calculado],
  "tp2": [TP2 calculado],
  "timeframe": "{{interval}}",
  "timestamp": {{time}}
}
```

---

## BACKTEST DE UNA IDEA

```
Quiero hacer backtest de esta estrategia en TradingView:
[DESCRIBE LA ESTRATEGIA]

Pasos:
1. Escribe un Pine Script strategy() completo con esa lógica
2. Incluye gestión de riesgo: 1% por trade, SL dinámico por ATR
3. Inyéctalo con tv_inject_pine_script
4. Compílalo y corrige errores
5. Toma un screenshot del backtest con tv_screenshot
6. Lee los resultados y dame: win rate, profit factor, max drawdown
```

---

## SESIÓN DE TRADING EN VIVO (PAPER)

```
Inicia una sesión de monitoreo en vivo:
1. Cambia el símbolo a BTCUSDT en timeframe 15m
2. Activa streaming con tv_stream_quotes
3. Cada 5 minutos, lee los valores de los indicadores
4. Si detectas un setup A o B (según protocolo SMC), avísame con:
   - Símbolo y timeframe
   - Tipo de setup (long/short)
   - Entrada exacta, SL, TP1, TP2
   - RR ratio
   - Screenshot del gráfico
5. Continúa monitoreando hasta que te diga "stop"
```

---

## MULTI-CHART DASHBOARD

```
Configura un layout 2x2 con estos pares:
- Pane 1: BTCUSDT 1H
- Pane 2: ETHUSDT 1H
- Pane 3: EURUSD 1H
- Pane 4: SPX500USD 1H

En cada pane, añade: EMA 50, EMA 200, y el indicador SMC si está disponible.
Luego dame un análisis rápido de cada uno: tendencia y nivel clave más cercano.
```

---

## MORNING BRIEF (ejecutar al abrir sesión)

```
Buenos días. Dame el morning brief:
1. Lee BTCUSDT Daily y 4H → tendencia macro
2. Lee ETHUSDT Daily → correlación con BTC
3. Lee DXY (índice del dólar) → impacto en crypto
4. Lee SPX500 → risk-on / risk-off
5. Para BTC: ¿hay setup intraday hoy? ¿Cuáles son los niveles clave?
6. Dame un bias: ALCISTA / BAJISTA / NEUTRAL para la sesión de hoy
7. Los mejores pares para operar hoy y por qué
```
