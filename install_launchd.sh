#!/bin/bash

# DevGuardian Launchd Setup
# Instala monitor como Background Agent no macOS

set -e

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLIST_FILE="$HOME/Library/LaunchAgents/com.devguardian.monitor.plist"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python3"
LOG_DIR="$HOME/.devguardian"

echo "🚀 DevGuardian Launchd Setup"
echo "=============================="

# Verificar venv
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Virtual environment not found"
    echo "   Run: bash setup.sh"
    exit 1
fi

# Criar diretório de logs
mkdir -p "$LOG_DIR"

# Criar plist file
echo "📝 Creating launchd configuration..."

cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.devguardian.monitor</string>

    <key>ProgramArguments</key>
    <array>
        <string>$VENV_PYTHON</string>
        <string>$PROJECT_DIR/monitor.py</string>
    </array>

    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>HOME</key>
        <string>$HOME</string>
    </dict>

    <key>StandardOutPath</key>
    <string>$LOG_DIR/monitor_stdout.log</string>

    <key>StandardErrorPath</key>
    <string>$LOG_DIR/monitor_stderr.log</string>

    <key>KeepAlive</key>
    <true/>

    <key>StartInterval</key>
    <integer>60</integer>

    <key>ProcessType</key>
    <string>Background</string>

    <key>Nice</key>
    <integer>10</integer>

</dict>
</plist>
EOF

echo "✅ Plist created at: $PLIST_FILE"

# Load launchd
echo "🔄 Loading launchd service..."
launchctl load "$PLIST_FILE" 2>/dev/null || launchctl unload "$PLIST_FILE" 2>/dev/null; launchctl load "$PLIST_FILE"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Quick commands:"
echo "   Check status:  launchctl list | grep devguardian"
echo "   View logs:     tail -f ~/.devguardian/monitor_stdout.log"
echo "   Stop service:  launchctl unload ~/Library/LaunchAgents/com.devguardian.monitor.plist"
echo "   Start service: launchctl load ~/Library/LaunchAgents/com.devguardian.monitor.plist"
echo ""
echo "🎉 Monitor is now running in background!"
echo ""
