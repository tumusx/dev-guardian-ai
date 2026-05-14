# DevGuardian 🤖

Monitor em **background** para macbook que detecta erros de build/IDE, notifica você no Telegram/Slack, e Claude resolve + faz push no GitHub.

Roda 24/7 como Launchd Agent (nativo do macOS).

## Fluxo

```
🔄 Launchd rodando em background
    ↓
IDE com erro → Monitora logs/files → Screenshot → Telegram/Slack 
    ↓ (você aprova no celular)
Passa screenshot pro Claude → Claude resolve
    ↓
Auto-fixer roda testes, build, push
```

## Setup Completo (10 minutos)

### 1️⃣ Setup inicial

```bash
cd ~/Projects/DevGuardian
bash setup.sh
```

Isso vai:
- Criar virtual environment
- Instalar dependências
- Criar `.env` para você preencher

### 2️⃣ Configurar Telegram Bot

1. Abra Telegram e busque por **@BotFather**
2. Mande `/newbot`
3. Escolha um nome (ex: "DevGuardianBot")
4. Copie o **TOKEN**

### 3️⃣ Pegar seu Chat ID

1. Busque **@userinfobot** no Telegram
2. Mande qualquer mensagem
3. Ele responde seu **ID**

### 4️⃣ Configurar `.env`

```bash
nano .env
```

Preencha:
```
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_id_aqui
PROJECT_PATH=/path/to/your/project
MONITOR_INTERVAL=30
```

### 5️⃣ Instalar como Launchd Agent (background permanente)

```bash
bash install_launchd.sh
```

✅ Monitor está rodando em background agora! Vai reiniciar sozinho até em reboot.

---

## Como Funciona (Background)

Monitor rodando sempre:
- ✅ Verifica logs a cada 30s
- ✅ Monitora mudanças de arquivos
- ✅ Checa resultados de testes
- ✅ Se encontra erro → Screenshota + Telegram

Você está fora de casa:
- 📱 Recebe notificação no Telegram
- 🤖 Abre Claude, cola screenshot
- 🔧 Claude resolve código
- 📤 Executa auto-fixer → push automático

---

## Comandos Úteis

```bash
# Ver status
launchctl list | grep devguardian

# Ver logs em tempo real
tail -f ~/.devguardian/monitor_stdout.log

# Parar o monitor
launchctl unload ~/Library/LaunchAgents/com.devguardian.monitor.plist

# Reiniciar o monitor
launchctl unload ~/Library/LaunchAgents/com.devguardian.monitor.plist
launchctl load ~/Library/LaunchAgents/com.devguardian.monitor.plist

# Ver erros detectados
cat ~/.devguardian/detector.log
```

---

## O que o Detector Monitora

✅ **Log Files**
- `build.log`
- `npm-debug.log`
- `test-results.log`
- Qualquer arquivo em `.logs/`

✅ **Test Results**
- `test-results.json`
- Coverage reports

✅ **Patterns** (detecta automaticamente)
- ERROR, error, failed, FAILED
- Exception, panic, fatal, crash
- Module not found, import error

---

## Quando tem erro (workflow)

1. **Monitor detecta** → Screenshota IDE
2. **Telegram notifica** → Você vê no celular (mesmo longe)
3. **Você aprova** → Abre Claude
4. **Claude resolve** → Edita arquivos necessários
5. **Executa auto-fixer**:
   ```bash
   python3 ~/Projects/DevGuardian/auto_fixer.py /path/to/projeto "descrição do erro"
   ```
6. **Auto-fixer**:
   - ✅ Instala dependências
   - ✅ Roda testes
   - ✅ Build
   - ✅ Git commit + push

---

## Para Slack (Corporativo)

Se sua empresa usa Slack:

1. Crie app em https://api.slack.com/apps
2. Ative "Files" e "Message Posting"
3. Copie **Slack Bot Token** (começa com `xoxb-`)
4. Configure `.env`:
   ```
   SLACK_BOT_TOKEN=xoxb-seu-token
   SLACK_CHANNEL=#devguardian
   ```

Monitor vai usar Slack automaticamente se Telegram não tiver.

---

## Estrutura de Arquivos

```
~/Projects/DevGuardian/
├── monitor.py           # Loop principal (monitora + notifica)
├── detector.py          # Detector inteligente (logs, files, testes)
├── auto_fixer.py        # Claude roda isso (fix + push)
├── install_launchd.sh   # Instala como background service
├── setup.sh             # Setup inicial
├── .env                 # Sua configuração (crie com setup.sh)
└── README.md            # Este arquivo
```

---

## Troubleshooting

### "Monitor não está detectando erro"
Verifica logs:
```bash
cat ~/.devguardian/detector.log
```

Testa manualmente:
```bash
python3 detector.py
```

### "Telegram não envia notificação"
Verifica token:
```bash
curl https://api.telegram.org/bot[SEU_TOKEN]/getMe
```

### "Launchd não inicia"
Verifica plist:
```bash
cat ~/Library/LaunchAgents/com.devguardian.monitor.plist
```

Carrega manualmente:
```bash
launchctl load ~/Library/LaunchAgents/com.devguardian.monitor.plist
```

---

## Próximas Versões

- [ ] Dashboard web para histórico
- [ ] Múltiplos projetos
- [ ] Integração com GitHub Issues
- [ ] Notificação por email
- [ ] Slack File Upload com screenshot

---

**Feito com ❤️ para makers que não estão em casa**
