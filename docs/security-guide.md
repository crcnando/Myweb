# Guia de Seguridad del Sistema

## La Regla de Oro

> Si no lo dirias en voz alta en publico, no lo pongas en el repositorio.

Este repo puede ser visto por cualquier persona si es publico.
Incluso si es privado, tratar los datos con cuidado es buena practica.

---

## Lo que SI puedes poner en el repo

- Templates en blanco (sin datos reales)
- Metas y planes generales
- Notas de aprendizaje
- Ideas de negocio (sin datos confidenciales de clientes)
- Listas de tareas
- Rutinas y habitos
- Reflexiones personales no sensibles

## Lo que NO debes poner en el repo

| Dato | Alternativa Segura |
|------|-------------------|
| Contrasenas | Bitwarden (gratis) o 1Password |
| Numeros de tarjeta / cuenta | Solo en `private/` (no sube a Git) |
| Cedula / identificacion | Solo en `private/` |
| Tokens y API keys | Variables de entorno o `private/` |
| Datos de clientes | Nunca en Git |
| Extractos bancarios reales | Solo en `private/` |
| Contratos firmados | Solo en `private/` |

---

## Configurar el Repo como Privado en GitHub

Si quieres que nadie mas pueda ver el repo:
1. Ve a github.com/crcnando/Myweb
2. Settings > Danger Zone > Change repository visibility
3. Selecciona "Private"

Incluso privado: NO subas contrasenas. Los repos pueden volverse publicos accidentalmente.

---

## Verificar que nada sensible se subio

```bash
# Buscar si hay algo que parezca contrasena o token
git log --all --full-history -- "*.env"
git grep -i "password\|token\|secret\|api_key\|contraseña"

# Si encuentras algo, avisa y lo removemos del historial
```

---

## Herramientas de Seguridad Recomendadas

| Herramienta | Para que | Costo |
|-------------|---------|-------|
| Bitwarden | Gestor de contrasenas | Gratis |
| 2FA (Google Authenticator) | Doble factor en GitHub | Gratis |
| GitHub Mobile con biometria | Acceso seguro desde celular | Gratis |

---

## Checklist de Seguridad (Hacer una vez)

- [ ] Activar 2FA en GitHub
- [ ] Configurar `.gitignore` (ya esta hecho)
- [ ] Verificar que el repo es privado o que entiendes que es publico
- [ ] Instalar Bitwarden o gestor de contrasenas
- [ ] Nunca usar la misma contrasena en GitHub y otros servicios
- [ ] Revisar que no haya datos reales en los archivos de finanzas

---

*Seguridad v1.0 | Revisar cada 6 meses*
