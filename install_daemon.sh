#!/bin/bash

DEVGUARDIAN_DIR="/Users/murilloalvesdasilva/Projects/DevGuardian"
VENV_PATH="$DEVGUARDIAN_DIR/venv"
LOG_DIR="$HOME/.devguardian"

mkdir -p "$LOG_DIR"

echo "📦 Verificando dependências..."
source "$VENV_PATH/bin/activate"
pip install python-telegram-bot anthropic python-dotenv requests > /dev/null 2>&1

# Create launchd plist
cat > "$HOME/Library/LaunchAgents/com.devguardian.daemon.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.devguardian.daemon</string>

    <key>ProgramArguments</key>
    <array>
        <string>/Users/murilloalvesdasilva/Projects/DevGuardian/venv/bin/python3</string>
        <string>/Users/murilloalvesdasilva/Projects/DevGuardian/daemon.py</string>
    </array>

    <key>WorkingDirectory</key>
    <string>/Users/murilloalvesdasilva/Projects/DevGuardian</string>

    <key>StandardOutPath</key>
    <string>/Users/murilloalvesdasilva/.devguardian/daemon_stdout.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/murilloalvesdasilva/.devguardian/daemon_stderr.log</string>

    <key>KeepAlive</key>
    <true/>

    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
EOF

chmod 644 "$HOME/Library/LaunchAgents/com.devguardian.daemon.plist"

echo "✅ Instalando daemon..."
launchctl load "$HOME/Library/LaunchAgents/com.devguardian.daemon.plist" 2>/dev/null || \
launchctl load -w "$HOME/Library/LaunchAgents/com.devguardian.daemon.plist"

sleep 2

if launchctl list | grep -q "com.devguardian.daemon"; then
    echo "✅ Daemon instalado e rodando!"
    echo "📁 Logs em: $LOG_DIR/"
    echo ""
    echo "Comandos úteis:"
    echo "  tail -f $LOG_DIR/daemon.log        (ver logs)"
    echo "  launchctl list | grep devguardian  (status)"
    echo "  launchctl unload ~/Library/LaunchAgents/com.devguardian.daemon.plist  (parar)"
else
    echo "❌ Falha ao instalar daemon"
    exit 1
fi
