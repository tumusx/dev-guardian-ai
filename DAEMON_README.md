# DevGuardian Central Daemon

Sistema **centralizado** que monitora **TODOS OS SEUS PROJETOS** 24/7

- 🔍 Monitora builds automaticamente
- 🤖 Claude API corrige erros
- 📱 Comunica TUDO via Telegram
- 0️⃣ Zero interação no terminal

## Setup (2 minutos)

### 1️⃣ Adicionar seu projeto

Edite `projects_config.json`:

```json
{
  "projects": [
    {
      "name": "http-cat-app",
      "path": "/Users/murilloalvesdasilva/Projects/personal/http-cat-app",
      "type": "android",
      "build_cmd": "./gradlew build",
      "active": true
    },
    {
      "name": "seu-outro-projeto",
      "path": "/path/to/project",
      "type": "nodejs",
      "build_cmd": "npm run build",
      "active": true
    }
  ],
  "monitor_interval": 30,
  "auto_fix_enabled": true
}
```

### 2️⃣ Instalar daemon

```bash
cd ~/Projects/DevGuardian
bash install_daemon.sh
```

Pronto! ✅ Daemon rodando 24/7

## Como funciona

### Fluxo automático

```
[Projeto X quebra] → 🚨 Telegram notifica
                        ↓
                  Você no Telegram:
                    "fix http-cat-app"
                        ↓
            ⏳ Corrigindo... (analisando)
            ⏳ Corrigindo... (aplicando)
            ⏳ Corrigindo... (testando)
                        ↓
        ✅ "Corrigido e subido!" OU
        ❌ "Erro ao corrigir. [detalhes]"
```

## Comandos Telegram

| Comando | O que faz |
|---------|-----------|
| `fix http-cat-app` | Corrige projeto que quebrou |
| `status` | Ver status de todos os projetos |
| `help` | Ver ajuda |

## Monitoramento

**Ver logs ao vivo:**
```bash
tail -f ~/.devguardian/daemon.log
```

**Ver todos os logs:**
```bash
ls -lah ~/.devguardian/
```

## Gerenciar daemon

**Status:**
```bash
launchctl list | grep devguardian
```

**Parar:**
```bash
launchctl unload ~/Library/LaunchAgents/com.devguardian.daemon.plist
```

**Reiniciar:**
```bash
launchctl unload ~/Library/LaunchAgents/com.devguardian.daemon.plist
launchctl load ~/Library/LaunchAgents/com.devguardian.daemon.plist
```

**Ver erros:**
```bash
tail -f ~/.devguardian/daemon_stderr.log
```

## Notificações Telegram

```
🚨 BUILD FAILED: http-cat-app
Column(...) expected
...
Responda: fix http-cat-app

---

⏳ http-cat-app: Corrigindo... (analisando)
⏳ http-cat-app: Corrigindo... (aplicando mudanças)
⏳ http-cat-app: Corrigindo... (testando build)

---

✅ http-cat-app: Corrigido e subido no GitHub!
```

## Adicionar novo projeto

1. Edite `projects_config.json`
2. Adicione seu projeto na lista
3. Salve

Pronto! Daemon já vai monitorar automaticamente.

---

**Tudo rodando 24/7 sem você fazer nada! 🤖**
