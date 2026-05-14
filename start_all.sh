#!/bin/bash
set -e

echo "🟢 STARTUP - DevGuardian"
echo "========================"
echo ""

DAEMON_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST_PATH="$HOME/Library/LaunchAgents/com.devguardian.daemon.plist"

# 1. Verifica se está parado
echo "1️⃣ Verificando status..."
if pgrep -f "daemon.py" > /dev/null; then
    echo "  ⚠️  Daemon já está rodando!"
    echo "  Use 'bash kill_all.sh' para parar"
    exit 1
fi
echo "  ✅ Daemon está parado"
echo ""

# 2. Instala o serviço
echo "2️⃣ Instalando serviço launchd..."
if [ ! -f "$PLIST_PATH" ]; then
    echo "  Criando plist..."
    mkdir -p "$HOME/Library/LaunchAgents"

    cat > "$PLIST_PATH" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.devguardian.daemon</string>
    <key>ProgramArguments</key>
    <array>
        <string>DAEMON_PATH/venv/bin/python3</string>
        <string>DAEMON_PATH/daemon.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>HOME/.devguardian/daemon.log</string>
    <key>StandardErrorPath</key>
    <string>HOME/.devguardian/daemon_stderr.log</string>
    <key>WorkingDirectory</key>
    <string>DAEMON_PATH</string>
</dict>
</plist>
EOF

    # Substitui paths
    sed -i '' "s|DAEMON_PATH|$DAEMON_DIR|g" "$PLIST_PATH"
    sed -i '' "s|HOME|$HOME|g" "$PLIST_PATH"
    echo "  ✅ Plist criado"
else
    echo "  ✅ Plist já existe"
fi
echo ""

# 3. Ativa o serviço
echo "3️⃣ Ativando daemon..."
launchctl load "$PLIST_PATH" 2>/dev/null || true
sleep 2
echo "  ✅ Daemon ativado"
echo ""

# 4. Verifica se iniciou
echo "4️⃣ Verificando se está rodando..."
if pgrep -f "daemon.py" > /dev/null; then
    PID=$(pgrep -f "daemon.py")
    echo "  ✅ Daemon rodando (PID: $PID)"
else
    echo "  ❌ Falha ao iniciar daemon!"
    echo "  Verifique os logs:"
    echo "  tail -f ~/.devguardian/daemon.log"
    exit 1
fi
echo ""

# 5. Mostra status
echo "5️⃣ Status final:"
launchctl list | grep devguardian || echo "  (serviço ativo)"
echo ""

echo "🟢 TUDO LIGADO!"
echo ""
echo "Ver logs:"
echo "  tail -f ~/.devguardian/daemon.log"
