#!/bin/bash
set -e

echo "🔴 SHUTDOWN PROCEDURE - DevGuardian"
echo "===================================="
echo ""

# 1. Captura estado
echo "Step 1️⃣ : Capturando estado atual..."
bash "$(dirname "$0")/capture_state.sh"
echo ""

# 2. Para daemon
echo "Step 2️⃣ : Parando daemon..."
bash "$(dirname "$0")/stop_daemon.sh"
echo ""

echo "🎯 Shutdown completo!"
echo "Use 'bash install_daemon.sh' para reiniciar"
