#!/bin/bash
set -e

DAEMON_NAME="DevGuardian Daemon"
PLIST_PATH="$HOME/Library/LaunchAgents/com.devguardian.daemon.plist"
LOG_DIR="$HOME/.devguardian"

echo "🛑 Parando $DAEMON_NAME..."

# 1. Para o serviço launchd
if launchctl list | grep -q "com.devguardian.daemon"; then
    echo "📋 Desativando launchd..."
    launchctl unload "$PLIST_PATH" 2>/dev/null || true
    sleep 1
fi

# 2. Mata qualquer processo daemon restante
echo "🔍 Procurando processos daemon..."
PID=$(pgrep -f "daemon.py" || true)
if [ -n "$PID" ]; then
    echo "💀 Matando processo: $PID"
    kill -9 "$PID" 2>/dev/null || true
    sleep 1
fi

# 3. Verifica status
echo ""
echo "✅ Status atual:"
if launchctl list | grep -q "com.devguardian.daemon"; then
    echo "  ❌ Daemon ainda está ativo"
else
    echo "  ✅ Daemon parado"
fi

if pgrep -f "daemon.py" > /dev/null; then
    echo "  ❌ Processo ainda está rodando"
else
    echo "  ✅ Nenhum processo daemon ativo"
fi

# 4. Mostra logs recentes
echo ""
echo "📊 Últimas linhas do log:"
if [ -f "$LOG_DIR/daemon.log" ]; then
    tail -10 "$LOG_DIR/daemon.log"
else
    echo "  (nenhum log encontrado)"
fi

echo ""
echo "✅ DevGuardian parado com sucesso!"
