# Quick Start 🚀

## 5 Passos para DevGuardian Rodando

### 1. Telegram Bot (2 min)

```
Telegram: @BotFather
/newbot
→ Copia TOKEN

Telegram: @userinfobot
→ Copia seu ID
```

### 2. Setup

```bash
cd ~/Projects/DevGuardian
bash setup.sh
```

### 3. Configurar

```bash
nano .env
```

Cole seu `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID`

### 4. Instalar Background

```bash
bash install_launchd.sh
```

### 5. Verificar

```bash
launchctl list | grep devguardian
tail -f ~/.devguardian/monitor_stdout.log
```

✅ **Pronto! Monitor rodando 24/7**

---

## Quando tem erro

1. 📱 Recebe notificação Telegram
2. 🤖 Abre Claude, cola screenshot
3. 🔧 Claude: "Resolve esse erro"
4. 📤 Claude roda:
   ```bash
   python3 ~/Projects/DevGuardian/auto_fixer.py /seu/projeto "descrição"
   ```
5. ✅ Automático: testes → build → push

---

## Logs

```bash
# Ver logs em tempo real
tail -f ~/.devguardian/monitor_stdout.log

# Ver histórico de erros detectados
cat ~/.devguardian/detector.log

# Ver auto-fixer log
cat ~/.devguardian/fix_log.txt
```

---

## Parar/Reiniciar

```bash
# Parar
launchctl unload ~/Library/LaunchAgents/com.devguardian.monitor.plist

# Reiniciar
launchctl load ~/Library/LaunchAgents/com.devguardian.monitor.plist
```

---

**Documentação completa:** `README.md` e `WORKFLOW.md`
