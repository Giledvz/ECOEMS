#!/bin/zsh
# Instala el LaunchAgent para que el server arranque solo cuando bootea la Mac.
# Versión no invasiva: solo RunAtLoad, sin KeepAlive (si crashea, queda caído).
#
# Notas importantes:
# - Logs van a /tmp/ecoems-server.log (NO a Documents/, porque macOS bloquea
#   TCC para que launchd escriba ahí).
# - Requiere que el usuario tenga auto-login activado, o que alguien entre la
#   contraseña al bootear. El server arranca cuando se inicia la sesión.

set -e
SRC="$(cd "$(dirname "$0")" && pwd)/com.giledvz.ecoems-server.plist"
DST="$HOME/Library/LaunchAgents/com.giledvz.ecoems-server.plist"

cp "$SRC" "$DST"
echo "✓ plist copiado a $DST"

# Cargar (si ya estaba cargado, lo recarga)
launchctl bootout "gui/$(id -u)/com.giledvz.ecoems-server" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$DST"
echo "✓ LaunchAgent cargado"

sleep 3
if lsof -tnP -iTCP:3000 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "✓ Server arriba en :3000 (logs: /tmp/ecoems-server.log)"
else
  echo "✗ Server no arrancó. Logs:"
  tail -20 /tmp/ecoems-server.log
  exit 1
fi
