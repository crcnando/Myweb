# Guia de Configuracion — Git en 3 Dispositivos

## Objetivo

Que puedas editar este sistema desde tu celular, PC personal y PC laboral, y que todo se sincronice automaticamente via Git + GitHub.

---

## Prerequisitos

- Cuenta en GitHub (ya la tienes: `crcnando`)
- Repositorio `crcnando/Myweb` (ya existe)
- Internet en cada dispositivo

---

## Configuracion por Dispositivo

### PC Personal (Linux / Mac / Windows)

```bash
# 1. Instalar Git (si no lo tienes)
# En Ubuntu/Debian:
sudo apt install git

# En Mac:
brew install git

# 2. Configurar tu identidad (solo una vez)
git config --global user.name "Nando Vega"
git config --global user.email "tu-email@gmail.com"

# 3. Clonar el repositorio
git clone https://github.com/crcnando/Myweb.git
cd Myweb

# 4. ¡Listo! Ahora puedes editar y sincronizar
```

### PC Laboral (Windows principalmente)

```bash
# 1. Descargar Git para Windows desde: https://git-scm.com/download/win
# Instalar con opciones por defecto

# 2. Abrir "Git Bash" y configurar identidad
git config --global user.name "Nando Vega"
git config --global user.email "tu-email@gmail.com"

# 3. Clonar el repositorio
git clone https://github.com/crcnando/Myweb.git
cd Myweb
```

> IMPORTANTE: En el trabajo, asegurate de que el IT Policy permita GitHub.
> Alternativa: usa GitHub.com directamente desde el navegador para editar archivos.

### Celular

**Opcion A — GitHub Mobile (Recomendada para leer y editar notas simples)**
1. Descargar "GitHub" desde App Store o Play Store
2. Iniciar sesion con tu cuenta `crcnando`
3. Ir al repositorio Myweb y editar archivos directamente

**Opcion B — Termux (Android) para uso avanzado**
```bash
# En Termux:
pkg install git
git clone https://github.com/crcnando/Myweb.git
cd Myweb
```

---

## Flujo Diario de Sincronizacion

### Al comenzar el dia (en cualquier dispositivo)
```bash
# Ir a la carpeta del proyecto
cd ~/Myweb   # o donde lo hayas clonado

# Traer los ultimos cambios
git pull origin main
```

### Al terminar de trabajar
```bash
# Ver que cambiaste
git status

# Agregar los cambios
git add .

# Guardar con mensaje descriptivo
git commit -m "agenda: planificacion semana 26 jun"

# Subir a GitHub (sincroniza todos los dispositivos)
git push origin main
```

---

## Mensajes de Commit Recomendados

Usa prefijos para identificar el tipo de cambio:

```
agenda: <descripcion>       → cambios en agenda
personal: <descripcion>     → aprendizaje, habitos, metas
trabajo: <descripcion>      → proyectos laborales
negocio: <descripcion>      → ideas y emprendimiento
docs: <descripcion>         → documentacion
familia: <descripcion>      → compromisos familiares
```

**Ejemplos:**
```
agenda: daily del lunes 23 jun completado
personal: platzi - termino curso de git
negocio: evaluacion idea #2 de automatizacion
trabajo: notas reunion con cliente
```

---

## Solucion de Problemas Comunes

### Error: "Please commit or stash your changes"
```bash
git stash          # guardar cambios temporalmente
git pull origin main
git stash pop      # recuperar tus cambios
```

### Conflicto de merge
```bash
# Git te marcara los conflictos en el archivo
# Edita el archivo, resuelve el conflicto y luego:
git add archivo-con-conflicto.md
git commit -m "fix: resuelvo conflicto en agenda"
```

### Ver historial de cambios
```bash
git log --oneline -20    # ultimos 20 commits
git log --oneline --all  # todos los commits
```

---

## Herramientas Opcionales (para comodidad)

- **VS Code** — Editor gratuito con integracion Git visual (recomendado para PC)
- **Obsidian** — Excelente para leer/editar archivos .md con formato bonito
- **GitHub Mobile** — Para revisar y editar desde el celular
- **GitKraken** — Interface visual de Git (alternativa a comandos)

---

*Guia v1.0 | Actualizar segun necesidad*
