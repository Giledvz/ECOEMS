#!/usr/bin/env bash
# update-prod.sh — Actualiza la máquina al último main y reinicia el server.
#
# Aborta automáticamente si:
#   - Hay cambios locales sin guardar (no toca tu trabajo en progreso).
#   - Hay un examen activo (no borra el estado de alumnos en aplicación).
#   - El server nuevo no arranca (te avisa para que revises).
#
# Uso: ./update-prod.sh

set -u

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
PORT=3000
LOG_FILE="$REPO_DIR/server.log"

# Colores para la salida
RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
YELLOW=$'\033[0;33m'
BLUE=$'\033[0;34m'
BOLD=$'\033[1m'
RESET=$'\033[0m'

cd "$REPO_DIR"

echo "${BOLD}== Actualización segura de ECOEMS ==${RESET}"
echo

# ── 1. Working tree limpio ──────────────────────────────────────────────────
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  echo "${RED}✗ Hay cambios locales sin guardar:${RESET}"
  git status --short --untracked-files=no | sed 's/^/    /'
  echo
  echo "${YELLOW}Resuélvelos primero (commit, stash o descarta) y vuelve a correr.${RESET}"
  exit 1
fi
echo "${GREEN}✓${RESET} Sin cambios sin guardar"

# ── 2. Fetch desde GitHub ───────────────────────────────────────────────────
if ! git fetch origin 2>&1 | sed 's/^/    /'; then
  echo "${RED}✗ git fetch falló. ¿Hay internet?${RESET}"
  exit 1
fi
echo "${GREEN}✓${RESET} Fetch completado"

# ── 3. Comparar estado local vs origin/main ────────────────────────────────
CUR_BRANCH=$(git branch --show-current)
LOCAL_HEAD=$(git rev-parse HEAD)
REMOTE_HEAD=$(git rev-parse origin/main)

ALREADY_OK=false
if [ "$CUR_BRANCH" = "main" ] && [ "$LOCAL_HEAD" = "$REMOTE_HEAD" ]; then
  echo "${GREEN}✓${RESET} Ya estás en main al día"
  ALREADY_OK=true
else
  echo "${BLUE}→${RESET} Pendiente actualizar (local ${LOCAL_HEAD:0:7} → remoto ${REMOTE_HEAD:0:7})"
fi

# ── 4. Chequear examen activo (solo si server corriendo) ───────────────────
if lsof -tnP -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1; then
  if ROOMS_JSON=$(curl -fs --max-time 3 "http://localhost:$PORT/api/rooms" 2>/dev/null); then
    ACTIVE_COUNT=$(node -e "try{const r=JSON.parse(process.argv[1]);console.log(r.filter(x=>x.phase==='active').length)}catch(e){console.log(0)}" "$ROOMS_JSON" 2>/dev/null || echo 0)
    if [ "${ACTIVE_COUNT:-0}" -gt 0 ]; then
      echo
      echo "${RED}${BOLD}✗ PELIGRO: hay $ACTIVE_COUNT examen(es) activo(s) ahora mismo.${RESET}"
      echo "${RED}  Actualizar borraría el estado de los alumnos en plena aplicación.${RESET}"
      echo "${YELLOW}  Espera a que terminen y reintenta.${RESET}"
      exit 2
    fi
    echo "${GREEN}✓${RESET} No hay exámenes activos"
  fi
fi

# Si ya estábamos OK y el server está corriendo, salir sin reiniciar
if $ALREADY_OK && lsof -tnP -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1; then
  echo
  echo "${GREEN}${BOLD}== Nada que hacer, todo en orden ==${RESET}"
  exit 0
fi

# ── 5. Cambiar a main si hace falta y pull ─────────────────────────────────
if [ "$CUR_BRANCH" != "main" ]; then
  echo "${BLUE}→${RESET} Cambiando de '$CUR_BRANCH' a 'main'"
  if ! git checkout main; then
    echo "${RED}✗ No se pudo cambiar a main${RESET}"
    exit 3
  fi
fi
if ! $ALREADY_OK; then
  if ! git pull --ff-only origin main; then
    echo "${RED}✗ Pull falló (posible divergencia local). Revisa manualmente.${RESET}"
    exit 4
  fi
  echo "${GREEN}✓${RESET} Pulled $(git rev-parse --short HEAD)"
fi

# ── 6. Detener server actual ────────────────────────────────────────────────
if PID=$(lsof -tnP -iTCP:$PORT -sTCP:LISTEN 2>/dev/null); then
  echo "${BLUE}→${RESET} Deteniendo server PID $PID..."
  kill "$PID" 2>/dev/null || true
  for i in 1 2 3 4 5; do
    sleep 1
    lsof -tnP -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1 || break
  done
  if lsof -tnP -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1; then
    kill -9 "$PID" 2>/dev/null || true
    sleep 1
  fi
fi

# ── 7. Arrancar server fresh en background ─────────────────────────────────
echo "${BLUE}→${RESET} Arrancando node server.js (logs en $LOG_FILE)"
nohup node server.js > "$LOG_FILE" 2>&1 &
disown

# ── 8. Verificar que arrancó ────────────────────────────────────────────────
for i in 1 2 3 4 5; do
  sleep 1
  if NEWPID=$(lsof -tnP -iTCP:$PORT -sTCP:LISTEN 2>/dev/null); then
    echo "${GREEN}✓${RESET} Server arrancado (PID $NEWPID) en :$PORT"
    echo
    echo "${GREEN}${BOLD}== Actualización completa ==${RESET}"
    echo "  Logs en vivo:    ${YELLOW}tail -f $LOG_FILE${RESET}"
    echo "  Panel profesor:  ${YELLOW}http://localhost:$PORT/teacher.html${RESET}"
    exit 0
  fi
done

echo "${RED}✗ Server NO arrancó. Últimas líneas del log:${RESET}"
tail -20 "$LOG_FILE" 2>/dev/null | sed 's/^/    /'
exit 5
