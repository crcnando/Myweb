# Sistema Operativo de Vida — Nando Vega

> "No administras el tiempo, administras las decisiones que tomas en el tiempo."

Este repositorio es el **hub central** de mi vida. Sincroniza mi celular, PC personal y PC laboral mediante Git. Todo lo que importa vive aqui.

---

## Panel de Control Rapido

| Area | Proxima Accion |
|------|----------------|
| [Agenda Semanal](agenda/templates/weekly-template.md) | Planear la semana |
| [KPIs Semanales](kpis/templates/weekly-kpis.md) | Completar revision dominical |
| [Platzi](personal/learning/platzi-tracker.md) | Proxima leccion |
| [Trabajo](work/projects/README.md) | Revisar proyectos activos |
| [Ideas de Negocio](business/ideas/) | Evaluar idea #1 |
| [Finanzas](finances/README.md) | Registrar gastos del dia |
| [Deudas](finances/templates/debt-tracker.md) | Actualizar saldos |
| [Salud](health/tracker/daily-health-log.md) | Registro diario de salud |
| [Segundo Cerebro](brain/ideas/inbox.md) | Procesar ideas del inbox |
| [Marca Personal](brand/content/content-calendar.md) | Publicar contenido |

---

## Estructura del Sistema

```
SISTEMA OPERATIVO DE VIDA
│
├── CIRCULOS DE VIDA
│   ├── personal/     → Aprendizaje, habitos, metas
│   ├── family/       → Compromisos y tiempo familiar
│   ├── work/         → Proyectos y productividad laboral
│   ├── social/       → Red de contactos y comunidad
│   └── marital/      → Vida en pareja y proyectos juntos
│
├── MOTORES DEL SISTEMA
│   ├── agenda/       → Templates diario, semanal, mensual
│   ├── kpis/         → Dashboard de metricas de vida
│   ├── health/       → Salud: sueno, ejercicio, nutricion
│   ├── finances/     → Personal + empresa + pareja
│   └── brain/        → Segundo cerebro: ideas, libros, notas
│
├── EMPRENDIMIENTO
│   └── business/     → Ideas, IA/automatizacion, modelos
│
├── MARCA PERSONAL
│   └── brand/        → Contenido, LinkedIn, red de contactos
│
└── SISTEMA BASE
    ├── docs/         → Guias, filosofia, seguridad
    └── tools/        → Scripts de automatizacion
```

---

## Navegar por Area

### Circulos de Vida
- [Personal](personal/README.md) — Platzi, habitos, metas 2026
- [Familia](family/README.md) — Compromisos y tiempo en familia
- [Trabajo](work/README.md) — Proyectos, productividad, carrera
- [Social](social/README.md) — Red de contactos y comunidad
- [Marital](marital/README.md) — Vida en pareja, economia compartida

### Motores del Sistema
- [Agenda](agenda/templates/) — Templates de planificacion
- [KPIs](kpis/README.md) — Dashboard de metricas personales
- [Salud](health/README.md) — Tracker de sueno, ejercicio, energia
- [Finanzas](finances/README.md) — Contabilidad total: personal + empresa + pareja
- [Segundo Cerebro](brain/README.md) — Ideas, libros, notas de aprendizaje

### Emprendimiento e IA
- [Ideas de Negocio](business/ideas/) — Evaluacion con template
- [Automatizacion con IA](business/ai-automation/) — Proyectos tecnicos
- [Modelos de Negocio](business/models/) — Canvas y validaciones

### Marca Personal
- [Estrategia de Contenido](brand/content/content-calendar.md) — Que publicar y cuando
- [LinkedIn](brand/linkedin-strategy.md) — Plan de posicionamiento
- [Propuesta de Valor](brand/personal-value-proposition.md) — Mi diferenciador
- [Red de Contactos](brand/network/key-contacts.md) — Mentores y aliados

---

## Como Usar en 3 Dispositivos

```bash
# Cada manana (en cualquier dispositivo):
git pull origin main

# Al terminar de trabajar:
git add .
git commit -m "agenda: daily del lunes 2026-06-23"
git push origin main

# Atajo (script incluido):
bash tools/sync.sh "tu mensaje aqui"
```

- [Guia completa de configuracion](docs/setup-guide.md)
- [Guia de seguridad](docs/security-guide.md) — Que NO subir al repo

---

## Documentacion y Recursos

- [Roadmap](ROADMAP.md) — Plan de 5 fases
- [Filosofia del Sistema](docs/philosophy.md) — Los principios que guian todo
- [Guia de Configuracion](docs/setup-guide.md) — Git en celular, PC personal y PC laboral
- [Seguridad](docs/security-guide.md) — Como proteger tu informacion

---

## Mi Situacion Actual (Junio 2026)

- Aprendiendo en Platzi: habilidades blandas + programacion
- Objetivo: automatizar procesos con IA para emprender
- Reto personal: ser hiper-productivo en todos mis circulos
- Vision: sistematizar el modelo y venderlo / replicarlo

---

*Ultima actualizacion: 2026-06-20*
