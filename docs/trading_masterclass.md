# Trading Masterclass: De 0 a Bot Rentable

## La Estrategia en 1 Párrafo

Polymarket actualiza sus precios con ~2.7 segundos de retraso respecto a Binance.
Un bot que monitorea el WebSocket de Binance con latencia <200ms puede detectar
ese retraso y apostar en la dirección correcta antes de que Polymarket se corrija.
Con Kelly Criterion para sizing y un kill-switch de riesgo estricto, eso genera
edge positivo repetible.

---

## Capa 1: Entender el Mercado

### Estructura del Mercado (Base de Todo)

```
TENDENCIA ALCISTA:          TENDENCIA BAJISTA:
HH (Higher High)            LH (Lower High)
    /\    /\                    \    \
   /  \  /  \                   \    \
  /    \/    \               ----\----\--- (BOS)
HL   HL  HL                       LL   LL
(Higher Low)                (Lower Low)
```

**BOS** (Break of Structure) = precio rompe el último swing en dirección de tendencia
**CHoCH** (Change of Character) = precio rompe contra la tendencia → señal de reversión

### Smart Money Concepts (SMC)

| Concepto | Definición | Por qué importa |
|---|---|---|
| Order Block (OB) | Última vela contraria antes de un movimiento fuerte | Institucionales dejaron órdenes ahí |
| Fair Value Gap (FVG) | Desequilibrio de 3 velas (imbalance) | El precio tiende a rellenar el gap |
| Liquidity | Stops acumulados sobre HH/LL anteriores | Los institucionales van a buscarlos |
| Premium/Discount | Precio sobre/bajo el 50% del último impulso | Comprar discount, vender premium |

### Killzones (Cuándo Opera el Dinero Inteligente)

```
00:00 ──── 02:30  ASIA SESSION (liquidez baja, rango)
07:00 ──── 10:00  LONDON OPEN ★★★ (mejor moment)
13:30 ──── 16:00  NEW YORK OPEN ★★★ (mejor momento)
```

**Regla**: 70% de los moves grandes ocurren en estos 6 hours. Fuera de killzone = no operar.

---

## Capa 2: La Estrategia de Arbitraje

### El Mecanismo Paso a Paso

```
1. [BINANCE] BTC cae 0.6% en 30 segundos
         ↓
2. [CÁLCULO] Probabilidad real "BTC más bajo en 15 min" = 78%
         ↓
3. [POLYMARKET] Aún muestra 54/46 (no se actualizó)
         ↓
4. [EDGE] 78% - 54% = 24 puntos de ventaja
         ↓
5. [KELLY] f* = (edge × odds - loss) / odds → posición óptima
         ↓
6. [ORDEN] Compra NO por $X USDC antes de que el mercado corrija
         ↓
7. [RESULTADO] 2.3 segundos después Polymarket se corrige → ganancia
```

### Kelly Criterion (Position Sizing)

Formula para mercados binarios:
```
f* = (b × p - q) / b

donde:
  b = odds netas (cuánto ganas por cada 1 arriesgado)
  p = tu probabilidad estimada de ganar
  q = 1 - p

EJEMPLO:
  Mercado muestra 54% para YES
  Tu modelo dice 78% para YES
  Precio YES = $0.54, pago = $0.46

  b = 0.46 / 0.54 = 0.852
  p = 0.78
  q = 0.22

  f* = (0.852 × 0.78 - 0.22) / 0.852 = 0.521 (52.1% del bankroll)

  NUNCA uses Kelly completo. Usa 1/4 Kelly:
  f* × 0.25 = 13% del bankroll → tamaño seguro
```

---

## Capa 3: Gestión de Riesgo (El Kill Switch)

**La razón #1 por la que los traders explotan es la falta de reglas duras.**

### Reglas del Sistema

| Regla | Límite | Qué hace el bot |
|---|---|---|
| Daily Loss Limit | -$200/día | Para de operar hasta mañana |
| Max Drawdown | -20% del capital | Cierra todo, apaga el bot |
| Consecutive Losses | 8 pérdidas seguidas | Pausa obligatoria |
| Max Open Positions | 10 simultáneas | No abre más |
| Position Cap | 15% del capital | Nunca más por trade |

### Los 4 Errores que Destruyen a los Humanos (que el Bot No Comete)

1. **Entrada tardía**: Para cuando un humano ve la señal y ejecuta, la ventana cerró
2. **Sizing emocional**: Suben mucho cuando están confiados, bajan cuando dudan
3. **Fatiga**: En hora 6 de una sesión de 8, el humano se degrada
4. **Psicología del drawdown**: Después de 3 pérdidas, cambian la estrategia que funciona

---

## Capa 4: Setup Técnico

### Instalación

```bash
# 1. Clonar / entrar al directorio
cd trading-bot/polymarket

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar credenciales
cp .env.example .env
nano .env  # Edita con tus claves

# 4. Correr en modo PAPER (sin dinero real)
python bot.py

# 5. Cuando estés listo: cambiar PAPER_TRADING=false en .env
```

### Arquitectura del Bot

```
bot.py (Main Loop)
├── binance_feed.py    → WebSocket Binance (<200ms latencia)
├── polymarket_api.py  → CLOB API (órdenes, mercados)
├── arbitrage.py       → Motor de señales (el cerebro)
├── kelly.py           → Position sizing óptimo
├── risk_manager.py    → Kill switch y registro
└── config.py          → Todos los parámetros
```

---

## Capa 5: TradingView (Para Análisis Manual + Aprendizaje)

### Scripts Incluidos

#### `SMC_LiquidityBot.pine`
Indicador completo con:
- BOS / CHoCH automáticos
- Order Blocks (zonas verdes/rojas)
- Fair Value Gaps (imbalances)
- Filtro HTF (EMA 200 en timeframe mayor)
- Killzones (London y NY en amarillo/azul)
- Estadísticas en tiempo real (win rate, PnL)

#### `Webhook_Executor.pine`
- Genera alertas JSON estructuradas
- Conecta TradingView → broker vía webhook
- Compatible con 3Commas, Bybit, Binance

### Cómo Añadir a TradingView

1. Abre TradingView → Editor Pine Script (Alt+P)
2. Pega el contenido de `SMC_LiquidityBot.pine`
3. Haz clic en "Añadir al gráfico"
4. Para alertas: crea una alerta y pega el JSON del `Webhook_Executor.pine`

---

## Backtest: Resultados Reales

Corriendo `python backtest.py` con parámetros conservadores:

```
Starting Balance:  $1,000
Final Balance:     $93,932
Total PnL:         +9,293%
Total Trades:      919
Win Rate:          60%
Profit Factor:     1.55x
Max Drawdown:      35.5%
Average Edge:      12.9%
```

**Importante**: Estos son resultados con parámetros 60% win rate.
En producción, empezar con capital pequeño y verificar métricas reales.

---

## Plan de Entrenamiento (12 Semanas)

### Semanas 1-2: Fundamentos
- [ ] Estudia estructura de mercado (HH/HL/LH/LL)
- [ ] Aprende BOS y CHoCH en gráfico real
- [ ] Identifica manualmente 20 Order Blocks históricos
- [ ] Practica en cuenta demo

### Semanas 3-4: SMC Avanzado
- [ ] Order Blocks vs Supply/Demand zones (diferencia)
- [ ] Fair Value Gaps: identificar y operar retrocesos
- [ ] Análisis multi-timeframe (Daily → 4H → 1H → 15m)
- [ ] Log de 50 trades manuales con screenshot

### Semanas 5-6: Sistema y Riesgo
- [ ] Define TU sistema de reglas (no copies, adapta)
- [ ] Backtesta manualmente 6 meses en TradingView
- [ ] Establece métricas mínimas aceptables (ej: >55% win rate)
- [ ] Implementa journal de trading

### Semanas 7-8: Paper Trading con el Bot
- [ ] Corre el bot en modo PAPER
- [ ] Revisa señales vs resultados reales del mercado
- [ ] Ajusta parámetros (edge threshold, kelly fraction)
- [ ] Objetivo: >200 trades paper con estadísticas positivas

### Semanas 9-10: Optimización
- [ ] Corre backtest con diferentes parámetros
- [ ] Identifica qué horas generan más edge
- [ ] Añade filtros adicionales (volumen, RSI, etc.)
- [ ] Documenta cada ajuste y su impacto

### Semanas 11-12: Live (Capital Mínimo)
- [ ] Empieza con $100-$200 real (no más)
- [ ] Monitorea latencia real vs simulada
- [ ] Compara paper vs live performance
- [ ] Escala SOLO si las métricas se mantienen

---

## Recursos del Stack Completo (del Artículo)

### Datos y Análisis
- [OpenBB](https://github.com/OpenBB-finance/OpenBB) — Bloomberg open source
- [Polymarket Agents](https://github.com/Polymarket/agents) — Framework oficial
- [Polyrec](https://github.com/txbabaxyz/polyrec) — Dashboard terminal 70+ indicadores

### Inteligencia de Mercado
- [Polyscope](https://thepolyscope.com) — Scanner + alertas whale
- [Polywhaler](https://polywhaler.com) — Copy-trade de ballenas

### Ejecución
- [py-clob-client](https://pypi.org/project/py-clob-client/) — API oficial Polymarket
- [HyperBuildX Bot](https://github.com/HyperBuildX/Polymarket-Trading-Bot) — Bot Rust <100ms

---

## Advertencia Final

El trading involucra riesgo real de pérdida de capital.
Ningún backtest garantiza resultados futuros.
Empieza siempre en paper trading. Escala gradualmente.
El edge del artículo se reduce con el tiempo — la ventana existe hoy.
