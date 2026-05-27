#!/usr/bin/env bash
# Verifica que la máquina esté lista para aplicar un examen.
# Uso: ./check-prod.sh

set -u

# Colores
RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
YELLOW=$'\033[0;33m'
BOLD=$'\033[1m'
RESET=$'\033[0m'

cd "$(dirname "$0")"

errors=0

echo "${BOLD}Verificando estado para aplicar examen...${RESET}"
echo

# 1. Rama
current_branch=$(git branch --show-current)
if [ "$current_branch" = "main" ]; then
  echo "${GREEN}✓${RESET} Rama: $current_branch"
else
  echo "${RED}✗${RESET} Rama: ${BOLD}$current_branch${RESET} (debería ser ${BOLD}main${RESET})"
  echo "  Para arreglarlo: ${YELLOW}git checkout main${RESET}"
  errors=$((errors+1))
fi

# 2. Working tree limpio
if [ -z "$(git status --porcelain --untracked-files=no)" ]; then
  echo "${GREEN}✓${RESET} Working tree limpio (sin cambios sin guardar)"
else
  echo "${RED}✗${RESET} Hay cambios sin guardar en archivos versionados:"
  git status --porcelain --untracked-files=no | sed 's/^/    /'
  echo "  Revisa con: ${YELLOW}git status${RESET}"
  errors=$((errors+1))
fi

# 3. Sincronizado con origin/main
git fetch --quiet origin main 2>/dev/null || true
local_head=$(git rev-parse HEAD 2>/dev/null || echo "?")
remote_head=$(git rev-parse origin/main 2>/dev/null || echo "?")
if [ "$local_head" = "$remote_head" ]; then
  echo "${GREEN}✓${RESET} Al día con origin/main"
else
  behind=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "?")
  ahead=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "?")
  echo "${YELLOW}!${RESET} Diferencia con origin/main (atrás: $behind, adelante: $ahead)"
  if [ "$behind" != "0" ] && [ "$behind" != "?" ]; then
    echo "  Para traer cambios: ${YELLOW}git pull${RESET}"
  fi
fi

# 4. Puerto 3000
if lsof -ti :3000 >/dev/null 2>&1; then
  pid=$(lsof -ti :3000)
  echo "${YELLOW}!${RESET} Puerto 3000 ocupado (PID $pid). Ya hay un server corriendo."
  echo "  Para detenerlo: ${YELLOW}kill -9 $pid${RESET}"
else
  echo "${GREEN}✓${RESET} Puerto 3000 libre (listo para arrancar server)"
fi

# 5. node_modules instalado
if [ -d node_modules ] && [ -f package.json ]; then
  echo "${GREEN}✓${RESET} node_modules presente"
else
  echo "${RED}✗${RESET} Falta node_modules. Corre: ${YELLOW}npm install${RESET}"
  errors=$((errors+1))
fi

echo
if [ $errors -eq 0 ]; then
  echo "${GREEN}${BOLD}✓ Todo listo para aplicar examen.${RESET}"
  echo "  Arranca con: ${YELLOW}node server.js${RESET}"
  exit 0
else
  echo "${RED}${BOLD}✗ $errors problema(s) que arreglar antes de aplicar.${RESET}"
  exit 1
fi
