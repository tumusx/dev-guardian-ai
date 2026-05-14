# DevGuardian - Shutdown & Capture

Scripts para parar o daemon e capturar estado.

## 📸 Capturar Estado (sem parar)

```bash
bash capture_state.sh
```

Cria backup em `~/.devguardian/backups/state_YYYYMMDD_HHMMSS/` com:
- `daemon.log` - log completo do daemon
- `daemon_stderr.log` - erros
- `projects_config.json` - configuração
- `system_status.txt` - status de processos/serviços

## 🛑 Parar Daemon (sem captura)

```bash
bash stop_daemon.sh
```

- Desativa launchd
- Mata processos Python
- Mostra status final
- Exibe últimas linhas do log

## 🔴 Shutdown Completo (captura + para)

```bash
bash shutdown.sh
```

Faz tudo:
1. Captura estado completo
2. Para o daemon
3. Mostra status final

## 🔄 Reiniciar

```bash
bash install_daemon.sh
```

Reinstala e inicia o daemon normalmente.
