#!/bin/zsh
# Desinstala el LaunchAgent (para volver al flujo manual nohup/update-prod.sh).
set -e
DST="$HOME/Library/LaunchAgents/com.giledvz.ecoems-server.plist"

launchctl bootout "gui/$(id -u)/com.giledvz.ecoems-server" 2>/dev/null || true
rm -f "$DST"
echo "✓ LaunchAgent removido."
echo "El server actualmente corriendo NO se mata. Si quieres apagarlo:"
echo "  kill \$(lsof -tnP -iTCP:3000 -sTCP:LISTEN)"
