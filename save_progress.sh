#!/bin/bash

PROGRESS_FILE="$HOME/.claude/projects/-Users-murilloalvesdasilva/memory/devguardian_progress.md"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

echo "💾 Salvando progresso do DevGuardian..."
echo ""

# Verifica se o arquivo existe
if [ ! -f "$PROGRESS_FILE" ]; then
    echo "❌ Arquivo de progresso não encontrado em:"
    echo "   $PROGRESS_FILE"
    exit 1
fi

# Atualiza timestamp
sed -i '' "s/^**Last Updated**:.*/\*\*Last Updated\*\*: $TIMESTAMP/" "$PROGRESS_FILE"

# Conta commits
DAEMON_COMMITS=$(cd ~/Projects/DevGuardian && git rev-list --count HEAD 2>/dev/null || echo "?")
PROJECT_COMMITS=$(cd ~/Projects/personal/http-cat-app && git rev-list --count HEAD 2>/dev/null || echo "?")

echo "📊 Commits:"
echo "   DevGuardian: $DAEMON_COMMITS"
echo "   http-cat-app: $PROJECT_COMMITS"
echo ""

# Status do daemon
if pgrep -f "daemon.py" > /dev/null; then
    DAEMON_STATUS="🟢 RUNNING"
else
    DAEMON_STATUS="⚫ STOPPED"
fi

echo "🔍 Status:"
echo "   Daemon: $DAEMON_STATUS"
echo ""

# Mostra últimos commits
echo "📝 Últimos commits DevGuardian:"
cd ~/Projects/DevGuardian && git log --oneline -5 | sed 's/^/   /'
echo ""

echo "✅ Progresso salvo!"
echo "   Arquivo: $PROGRESS_FILE"
