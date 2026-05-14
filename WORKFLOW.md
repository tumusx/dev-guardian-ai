# Workflow Prático 🔄

## Cenário: Você está fora de casa

### 1️⃣ Setup Inicial (uma vez)

```bash
cd ~/Projects/DevGuardian
bash setup.sh
# Preenche .env com Telegram token
bash install_launchd.sh
```

Monitor está rodando **24/7 em background** agora! 

✅ Reinicia sozinho mesmo se desligar/reiniciar o mac  
✅ Você não precisa manter nenhum terminal aberto

---

## 2️⃣ Seu código dá erro (você longe de casa)

**O que acontece:**
- 🔴 Erro detectado (build falha, teste quebra, etc)
- 📸 Screenshot da IDE é capturado
- 📱 Telegram envia notificação com screenshot e erro
- ⏳ Monitor aguarda sua aprovação (30s)

**No seu celular:**
```
🚨 BUILD ERROR DETECTED

⏰ Time: 14:23:45
📍 Process: npm run dev
❌ Error: Cannot find module 'react'...

[SCREENSHOT DO ERRO]
```

---

## 3️⃣ Você aprova do celular

Você vê a notificação e pensa: _"Vou resolver isso"_

Abre o **Claude** (web ou Claude Code no seu notebook/outro computador):

```
Eu: "Resolva esse erro"
[Cola o screenshot do Telegram]
```

Claude analisa e:
- ✅ Identifica o problema
- ✅ Edita os arquivos necessários
- ✅ Testa localmente

---

## 4️⃣ Claude faz commit e push

Quando Claude terminou de resolver, você diz:

```
Execute esse comando para confirmar e fazer push:

python3 ~/Projects/DevGuardian/auto_fixer.py /path/to/seu/projeto "package error"
```

Claude executa no terminal e:

```
▶️ Running: npm install
✅ Dependencies successful

▶️ Running: npm test
✅ Tests successful

▶️ Running: git add -A
▶️ Running: git commit -m "Auto-fix: resolved build error"
✅ Git commit successful

▶️ Running: git push
✅ Changes pushed to GitHub!

====================================
✅ AUTO-FIX COMPLETED SUCCESSFULLY!
====================================
```

---

## Exemplo Real (Node.js project)

### Terminal 1 (seu macbook, rodando sempre)
```bash
$ python3 monitor.py
🚀 Starting monitor for: npm run dev
📱 Telegram Chat ID: 123456789

[aguardando erros...]

❌ Error #1 detected!
Output: Error: ENOENT: no such file or directory...
📸 Screenshot saved: /Users/murillo/.devguardian/screenshots/error_20250514_142345.png
✅ Report sent to Telegram!
⏳ Waiting for your approval...
```

### Seu celular (Telegram)
```
[Notification sound]
DevGuardianBot: 🚨 BUILD ERROR DETECTED
Time: 14:23:45
Process: npm run dev
Error: ENOENT: no such file or directory, open '.env'

[Screenshot mostrando o erro no VS Code]
```

### Claude (seu outro computador/celular web)
```
Você: Resolve esse erro de .env

Claude: Vejo que falta o arquivo .env. Vou:
1. Copiar .env.example para .env
2. Configurar variáveis
3. Rodar testes

[Claude edita os arquivos]

Você: Agora execute o auto-fixer:
python3 ~/Projects/DevGuardian/auto_fixer.py /path/to/projeto ".env missing"

Claude: ✅ Executando...
[vê toda a sequência de testes, build, push]
```

### Seu macbook (log do monitor)
```
[aguarda...]

✅ Build successful!
[volta a monitorar]
```

---

## Variações

### Projeto Python/FastAPI
```bash
# Configure em .env
WATCH_PROCESS=python -m pytest || python app.py
```

### Projeto Rust
```bash
# Configure em .env
WATCH_PROCESS=cargo test && cargo build
```

### Projeto Go
```bash
# Configure em .env
WATCH_PROCESS=go test ./... && go build
```

---

## Dicas Pro

### Deixar rodando 24/7 (daemon)
```bash
nohup python3 monitor.py > ~/.devguardian/monitor.log 2>&1 &
```

Depois ver logs:
```bash
tail -f ~/.devguardian/monitor.log
```

### Múltiplos projetos
Crie múltiplas instâncias com `.env` diferentes:
```bash
WATCH_PROCESS=/path/to/project1/run.sh
# em outro terminal
WATCH_PROCESS=/path/to/project2/run.sh
```

### Slack em vez de Telegram
Se sua empresa usa Slack, modifique `monitor.py`:
```python
# Comente send_telegram_report
# sent = self.send_telegram_report(screenshot, error_output)

# Descomente send_slack_report
sent = self.send_slack_report(screenshot, error_output)
```

---

## Troubleshooting

### "TELEGRAM_BOT_TOKEN not found"
Certifique que `.env` existe e tem as variáveis:
```bash
cat .env
```

### "Failed to send report"
Cheque se o token está correto:
```python
# Em Python
import requests
url = f"https://api.telegram.org/bot{TOKEN}/getMe"
print(requests.get(url).json())
```

### Monitor não detecta erro
Configure `WATCH_PROCESS` corretamente:
```bash
# Teste manualmente
npm run dev  # tem que dar erro quando há problema
```

---

## Próximos Passos

1. ✅ Setup inicial (5 min)
2. ✅ Rodar monitor
3. ✅ Testar com um erro forçado
4. ✅ Passar screenshot pro Claude
5. ✅ Ver magic acontecer 🪄

---

**Dúvidas? Sempre funciona assim:**
```
Screenshot → Telegram → Claude → Auto-fixer → GitHub
```
