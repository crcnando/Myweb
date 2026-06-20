# Herramientas y Scripts

## Lo que vive aqui

Scripts de automatizacion, atajos y herramientas que hacen el sistema mas eficiente.

## Herramientas Actuales

| Herramienta | Para que sirve | Como usarla |
|-------------|---------------|------------|
| `sync.sh` | Sincronizar el repo rapidamente | `bash tools/sync.sh "mensaje"` |

---

## Scripts

### sync.sh — Sincronizacion Rapida

Guarda y sube cambios con un solo comando.

```bash
#!/bin/bash
# Uso: bash tools/sync.sh "descripcion del cambio"
git add .
git commit -m "${1:-actualizacion diaria}"
git push origin main
echo "¡Sincronizado exitosamente!"
```

---

## Ideas de Automatizacion Futura

- [ ] Script para crear agenda diaria automaticamente
- [ ] Script para generar reporte semanal
- [ ] Integracion con Google Calendar via API
- [ ] Notificaciones en celular cuando hay cambios importantes

---

*Agregar scripts a medida que se van creando*
