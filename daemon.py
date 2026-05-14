#!/usr/bin/env python3
"""
DevGuardian Central Daemon - Versão Simplificada
Monitora TODOS os projetos via polling direto
"""
import os
import sys
import json
import subprocess
import logging
import requests
import time
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

# Config
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "0"))
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DEVGUARDIAN_DIR = Path(__file__).parent
CONFIG_FILE = DEVGUARDIAN_DIR / "projects_config.json"

# Logging
log_dir = Path.home() / ".devguardian"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "daemon.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Estado global
state = {
    "projects": {},
    "last_message_id": 0,
    "anthropic_client": Anthropic(api_key=ANTHROPIC_API_KEY)
}

def load_projects() -> dict:
    """Carrega configuração de projetos"""
    if not CONFIG_FILE.exists():
        logger.error(f"Config file not found: {CONFIG_FILE}")
        return {}

    try:
        with open(CONFIG_FILE) as f:
            config = json.load(f)
        projects = {}
        for proj in config.get("projects", []):
            if proj.get("active"):
                projects[proj["name"]] = proj
        return projects
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}

def send_telegram(message: str) -> bool:
    """Envia mensagem no Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        resp = requests.post(url, json=data, timeout=5)
        if resp.status_code == 200:
            logger.info("✅ Telegram notificado")
            return True
        else:
            logger.error(f"Telegram error: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        logger.error(f"Telegram connection error: {e}")
        return False

def get_telegram_messages() -> list:
    """Obtém mensagens do Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    params = {"offset": state["last_message_id"] + 1, "timeout": 1}
    try:
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()
        if data.get("ok"):
            return data.get("result", [])
        return []
    except:
        return []

def run_build(project: dict) -> tuple[int, str, str]:
    """Executa build de um projeto"""
    try:
        cmd = project.get("build_cmd", "./gradlew build").split()
        result = subprocess.run(
            cmd,
            cwd=project["path"],
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Build timeout"
    except Exception as e:
        return 1, "", str(e)

def extract_error(stdout: str, stderr: str) -> str:
    """Extrai erro principal"""
    combined = stdout + stderr
    lines = combined.split("\n")
    errors = []
    for line in lines:
        if any(x in line.lower() for x in ["error:", "failed", "exception"]):
            errors.append(line.strip())
    return "\n".join(errors[:3]) if errors else "Build failed"

def check_builds():
    """Monitora todos os projetos"""
    projects = load_projects()
    if not projects:
        return

    for proj_name, proj_config in projects.items():
        logger.info(f"🔍 Checking {proj_name}...")

        returncode, stdout, stderr = run_build(proj_config)

        if returncode != 0:
            error_msg = extract_error(stdout, stderr)
            full_log = stdout + stderr

            # Só notifica se erro é diferente do anterior
            old_state = state["projects"].get(proj_name, {})
            old_error = old_state.get("error", "")

            state["projects"][proj_name] = {
                "status": "failed",
                "error": error_msg,
                "full_log": full_log,
                "config": proj_config
            }

            # Se erro é novo/diferente, notifica
            if error_msg != old_error:
                msg = f"🚨 BUILD FAILED: {proj_name}\n\n{error_msg[:300]}\n\nfix"
                logger.error(f"{proj_name} build failed - novo erro, enviando Telegram...")
                success = send_telegram(msg)
                if success:
                    logger.info(f"✅ Notificação enviada para {proj_name}")
                else:
                    logger.error(f"❌ Falha ao enviar notificação para {proj_name}")
        else:
            if proj_name in state["projects"] and state["projects"][proj_name]["status"] == "failed":
                send_telegram(f"✅ {proj_name}: Build recuperado!")
            state["projects"][proj_name] = {"status": "success"}

def fix_project(proj_name: str) -> bool:
    """Corrige erro de um projeto"""
    if proj_name not in state["projects"]:
        send_telegram(f"❌ Projeto {proj_name} não encontrado")
        return False

    proj_state = state["projects"][proj_name]
    proj_config = proj_state.get("config")

    if not proj_config:
        send_telegram(f"❌ Config do projeto {proj_name} não encontrada")
        return False

    logger.info(f"🤖 Fixing {proj_name}...")
    send_telegram(f"⏳ Corrigindo {proj_name}...")

    try:
        project_path = Path(proj_config["path"])

        # Lê regras de correção globais (PRIORIDADE MÁXIMA)
        fix_rules = ""
        rules_path = DEVGUARDIAN_DIR / "FIX_RULES.md"
        if rules_path.exists():
            fix_rules = rules_path.read_text()

        # Lê guia de codebase se existir
        codebase_guide = ""
        guide_path = project_path / "CODEBASE_GUIDE.md"
        if guide_path.exists():
            codebase_guide = guide_path.read_text()

        kotlin_files = list(project_path.glob("src/**/*.kt"))[:10]
        file_context = {}

        for file_path in kotlin_files:
            try:
                content = file_path.read_text()
                file_path_rel = str(file_path.relative_to(project_path))
                file_context[file_path_rel] = content
            except:
                pass

        # Encontra arquivo com erro
        error_file = None
        for file_path in file_context.keys():
            if "MainActivity" in file_path:
                error_file = file_path

        client = state["anthropic_client"]
        full_log = proj_state.get('full_log', '')

        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": f"""=== ABSOLUTE RULES - MUST FOLLOW ===
{fix_rules}

=== CODEBASE GUIDE ===
{codebase_guide}

=== COMPLETE BUILD LOG ===
```
{full_log[-3000:]}
```

=== FILE WITH ERROR ===
{error_file}

=== COMPLETE FILE CONTENT ===
```kotlin
{file_context.get(error_file, '')}
```

=== YOUR TASK ===
1. Read the BUILD LOG carefully
2. Find the EXACT line number and error
3. Look at the file and find that line
4. Change ONLY that line (MINIMAL fix)
5. Do NOT add anything new
6. Do NOT remove anything that works
7. Return COMPLETE file with ONLY error fixed

=== RETURN FORMAT (STRICT) ===
FILE: {error_file}
```kotlin
[COMPLETE file]
```"""
            }]
        )

        fixes_text = response.content[0].text
        apply_fixes(fixes_text, project_path)
        returncode, stdout, stderr = run_build(proj_config)

        if returncode == 0:
            send_telegram(f"✅ {proj_name}: Corrigido e subido no GitHub!")
            commit_and_push(project_path)
            state["projects"][proj_name]["status"] = "success"
            return True
        else:
            new_error = extract_error(stdout, stderr)
            state["projects"][proj_name]["error"] = new_error
            send_telegram(f"""
❌ {proj_name}: Erro ao corrigir

{new_error[:300]}

Responda novamente: fix {proj_name}
""")
            return False

    except Exception as e:
        error_msg = f"Erro ao comunicar com servidor Claude: {str(e)[:100]}"
        logger.error(error_msg)
        send_telegram(f"❌ {proj_name}: {error_msg}")
        return False

def apply_fixes(fixes_text: str, project_path: Path):
    """Aplica correções"""
    lines = fixes_text.split("\n")
    current_file = None
    current_code = []
    in_code_block = False

    for line in lines:
        if line.startswith("FILE:"):
            if current_file and current_code:
                file_path = project_path / current_file
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text("\n".join(current_code))

            current_file = line.replace("FILE:", "").strip()
            current_code = []
            in_code_block = False
        elif line.startswith("```"):
            in_code_block = not in_code_block
        elif in_code_block and current_file:
            current_code.append(line)

    if current_file and current_code:
        file_path = project_path / current_file
        file_path.write_text("\n".join(current_code))
        logger.info(f"✅ Fixed: {current_file}")

def commit_and_push(project_path: Path):
    """Git commit e push"""
    try:
        subprocess.run(["git", "add", "-A"], cwd=project_path, check=True)
        subprocess.run(
            ["git", "commit", "-m", "🤖 Auto-fix: Build error resolved by Claude"],
            cwd=project_path,
            check=True
        )
        subprocess.run(["git", "push"], cwd=project_path, check=True)
        logger.info("✅ Committed and pushed")
    except subprocess.CalledProcessError as e:
        logger.error(f"Git error: {e}")

def main():
    logger.info("🚀 DevGuardian Central Daemon iniciado")

    if not TELEGRAM_BOT_TOKEN or not ANTHROPIC_API_KEY:
        logger.error("❌ Faltam credenciais")
        sys.exit(1)

    projects = load_projects()
    if not projects:
        logger.error("❌ Nenhum projeto configurado")
        sys.exit(1)

    logger.info(f"📁 Projetos: {', '.join(projects.keys())}")

    config = json.load(open(CONFIG_FILE))
    monitor_interval = config.get("monitor_interval", 30)

    logger.info(f"⏱️ Monitorando a cada {monitor_interval}s")
    logger.info("🤖 Pronto! Aguardando erros...")

    check_counter = 0
    while True:
        try:
            check_counter += 1

            # Check builds a cada monitor_interval segundos
            if check_counter >= monitor_interval:
                logger.info("🔄 Iniciando check de builds...")
                check_builds()
                check_counter = 0

            # Verifica mensagens do Telegram
            messages = get_telegram_messages()
            for msg in messages:
                state["last_message_id"] = msg["update_id"]
                if "message" in msg:
                    text = msg["message"].get("text", "").lower().strip()
                    if text == "fix":
                        # Corrige o projeto que está falhando
                        for pname, pstate in state["projects"].items():
                            if pstate.get("status") == "failed":
                                fix_project(pname)
                                break
                    elif text == "status":
                        msg_text = "📊 Status:\n"
                        for pname in projects.keys():
                            status = state.get("projects", {}).get(pname, {}).get("status", "unknown")
                            emoji = "✅" if status == "success" else "❌" if status == "failed" else "❓"
                            msg_text += f"{emoji} {pname}\n"
                        send_telegram(msg_text)

            time.sleep(1)

        except KeyboardInterrupt:
            logger.info("Daemon parado")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(5)

if __name__ == "__main__":
    main()
