#!/bin/bash
set -e

LOG_DIR="$HOME/.devguardian"
BACKUP_DIR="$HOME/.devguardian/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_PATH="$BACKUP_DIR/state_$TIMESTAMP"

echo "📸 Capturando estado do DevGuardian..."

# Cria diretório de backup
mkdir -p "$BACKUP_DIR"

# Copia logs
echo "📋 Copiando logs..."
mkdir -p "$BACKUP_PATH"
if [ -f "$LOG_DIR/daemon.log" ]; then
    cp "$LOG_DIR/daemon.log" "$BACKUP_PATH/daemon.log"
    echo "  ✅ daemon.log"
fi

if [ -f "$LOG_DIR/daemon_stderr.log" ]; then
    cp "$LOG_DIR/daemon_stderr.log" "$BACKUP_PATH/daemon_stderr.log"
    echo "  ✅ daemon_stderr.log"
fi

# Copia configuração
echo "📝 Copiando configuração..."
if [ -f "projects_config.json" ]; then
    cp projects_config.json "$BACKUP_PATH/projects_config.json"
    echo "  ✅ projects_config.json"
fi

# Status do sistema
echo "🖥️ Capturando status..."
echo "=== LAUNCHCTL STATUS ===" > "$BACKUP_PATH/system_status.txt"
launchctl list | grep devguardian >> "$BACKUP_PATH/system_status.txt" 2>/dev/null || echo "Nenhum serviço ativo" >> "$BACKUP_PATH/system_status.txt"

echo "=== PROCESSOS PYTHON ===" >> "$BACKUP_PATH/system_status.txt"
pgrep -f daemon.py >> "$BACKUP_PATH/system_status.txt" 2>/dev/null || echo "Nenhum processo ativo" >> "$BACKUP_PATH/system_status.txt"

echo ""
echo "✅ Estado capturado em: $BACKUP_PATH"
echo ""
echo "📁 Conteúdo:"
ls -lah "$BACKUP_PATH"
