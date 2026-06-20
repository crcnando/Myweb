#!/bin/bash
# sync.sh — Guarda y sube todos los cambios al repo
# Uso: bash tools/sync.sh "descripcion del cambio"
# Ejemplo: bash tools/sync.sh "agenda: diaria del lunes"

MESSAGE="${1:-actualizacion: $(date +%Y-%m-%d)}"

echo "Sincronizando Sistema Operativo de Vida..."
git add .
git commit -m "$MESSAGE"
git push origin main
echo ""
echo "Listo! Cambios subidos: $MESSAGE"
