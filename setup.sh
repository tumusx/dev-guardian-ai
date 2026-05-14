#!/bin/bash

echo "🚀 DevGuardian Setup"
echo "===================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale via: brew install python3"
    exit 1
fi

# Create venv
echo "📦 Criando virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install deps
echo "📥 Instalando dependências..."
pip install -r requirements.txt

# Create .env
if [ ! -f .env ]; then
    echo "📝 Criando .env..."
    cp .env.example .env
    echo "⚠️  IMPORTANTE: Edite .env com seu TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID"
    echo "   - Bot: https://telegram.me/botfather"
    echo "   - ID: https://telegram.me/userinfobot"
else
    echo "✅ .env já existe"
fi

# Create screenshot directory
mkdir -p ~/.devguardian/screenshots

echo ""
echo "✅ Setup completo!"
echo ""
echo "Próximo passo:"
echo "1. Edite .env com suas credenciais"
echo "2. source venv/bin/activate"
echo "3. python3 monitor.py"
echo ""
