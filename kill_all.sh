#!/bin/bash

echo "💀 KILLALL - DevGuardian & Related Processes"
echo "=============================================="
echo ""

# 1. Para launchd
echo "🛑 Parando launchd service..."
if launchctl list | grep -q "com.devguardian.daemon"; then
    launchctl unload "$HOME/Library/LaunchAgents/com.devguardian.daemon.plist" 2>/dev/null || true
fi
sleep 1

# 2. Mata daemon Python
echo "💀 Matando daemon.py..."
pkill -9 -f "daemon.py" 2>/dev/null || true
sleep 1

# 3. Mata Gradle builds
echo "💀 Matando gradle..."
pkill -9 -f "gradle" 2>/dev/null || true
pkill -9 -f "gradlew" 2>/dev/null || true
sleep 1

# 4. Mata Java (se houver)
echo "💀 Matando processos Java..."
pkill -9 java 2>/dev/null || true
sleep 1

# 5. Mata qualquer Python relacionado
echo "💀 Matando Python..."
pkill -9 python3 2>/dev/null || true
sleep 1

# 6. Remove locks de Gradle
echo "🔓 Removendo gradle locks..."
rm -rf ~/.gradle/wrapper/dists/*/gradle-*/gradle-*/lib/*/gradle-wrapper.jar.lock 2>/dev/null || true
find ~/.gradle -name "*.lock" -delete 2>/dev/null || true

# 7. Verifica se realmente parou
echo ""
echo "✅ Verificando status final..."
echo ""

echo "Processos daemon:"
pgrep -f "daemon.py" && echo "  ❌ AINDA RODANDO" || echo "  ✅ Parado"

echo "Processos gradle:"
pgrep -f "gradle" && echo "  ❌ AINDA RODANDO" || echo "  ✅ Parado"

echo "Processos Java:"
pgrep java && echo "  ❌ AINDA RODANDO" || echo "  ✅ Parado"

echo "Processos Python:"
pgrep python3 && echo "  ❌ AINDA RODANDO" || echo "  ✅ Parado"

echo ""
echo "🔴 TUDO MORTO!"
