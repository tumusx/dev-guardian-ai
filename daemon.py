#!/usr/bin/env python3
"""
DevGuardian Central Daemon
Monitora TODOS os projetos
Claude API corrige erros automaticamente
"""
import os
import sys
import json
import subprocess
import logging
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
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
    "waiting_for_fix": False,
    "current_project": None,
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

async def send_telegram(message: str):
    """Envia mensagem no Telegram"""
    import requests
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}

    try:
        resp = requests.post(url, json=data, timeout=5)
        return resp.status_code == 200
    except Exception as e:
        logger.error(f"Telegram error: {e}")
        return False

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

    if errors:
        return "\n".join(errors[:3])
    return "Build failed"

async def check_builds():
    """Monitora todos os projetos"""
    projects = load_projects()
    if not projects:
        return

    for proj_name, proj_config in projects.items():
        logger.info(f"🔍 Checking {proj_name}...")

        returncode, stdout, stderr = run_build(proj_config)

        if returncode != 0:
            error_msg = extract_error(stdout, stderr)

            if proj_name not in state["projects"] or state["projects"][proj_name]["status"] != "failed":
                state["projects"][proj_name] = {
                    "status": "failed",
                    "error": error_msg,
                    "config": proj_config
                }

                msg = f"""
🚨 BUILD FAILED: {proj_name}

{error_msg[:300]}

Responda: fix {proj_name}
Para corrigir via Claude
"""
                logger.error(f"{proj_name} build failed:\n{error_msg}")
                await send_telegram(msg)
        else:
            if proj_name in state["projects"] and state["projects"][proj_name]["status"] == "failed":
                await send_telegram(f"✅ {proj_name}: Build recuperado!")

            state["projects"][proj_name] = {"status": "success"}

async def fix_project(proj_name: str) -> bool:
    """Corrige erro de um projeto via Claude"""
    if proj_name not in state["projects"]:
        await send_telegram(f"❌ Projeto {proj_name} não encontrado")
        return False

    proj_state = state["projects"][proj_name]
    proj_config = proj_state.get("config")

    if not proj_config:
        await send_telegram(f"❌ Config do projeto {proj_name} não encontrada")
        return False

    logger.info(f"🤖 Fixing {proj_name}...")
    await send_telegram(f"⏳ {proj_name}: Corrigindo... (analisando)")

    try:
        project_path = Path(proj_config["path"])
        kotlin_files = list(project_path.glob("src/**/*.kt"))[:5]
        file_context = {}

        for file_path in kotlin_files:
            try:
                content = file_path.read_text()
                file_context[str(file_path.relative_to(project_path))] = content[:800]
            except:
                pass

        # Chama Claude
        client = state["anthropic_client"]
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"""Fix this build error (Project: {proj_name}):

ERROR:
{proj_state.get('error', '')[:500]}

FILES:
{str(file_context)[:1000]}

Return ONLY the fixed file content in this format:
FILE: path/to/file.kt
```kotlin
[complete fixed code]
```"""
            }]
        )

        fixes_text = response.content[0].text

        await send_telegram(f"⏳ {proj_name}: Corrigindo... (aplicando mudanças)")
        apply_fixes(fixes_text, project_path)

        await send_telegram(f"⏳ {proj_name}: Corrigindo... (testando build)")
        returncode, stdout, stderr = run_build(proj_config)

        if returncode == 0:
            await send_telegram(f"✅ {proj_name}: Corrigido e subido no GitHub!")
            commit_and_push(project_path)
            state["projects"][proj_name]["status"] = "success"
            return True
        else:
            new_error = extract_error(stdout, stderr)
            state["projects"][proj_name]["error"] = new_error
            await send_telegram(f"""
❌ {proj_name}: Erro ao corrigir

{new_error[:300]}

Responda novamente: fix {proj_name}
""")
            return False

    except Exception as e:
        error_msg = f"Erro ao comunicar com servidor Claude: {str(e)[:100]}"
        logger.error(error_msg)
        await send_telegram(f"❌ {proj_name}: {error_msg}")
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

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa mensagens do Telegram"""
    if update.message.chat_id != TELEGRAM_CHAT_ID:
        return

    text = update.message.text.lower().strip()

    if text.startswith("fix "):
        proj_name = text.replace("fix ", "").strip()
        await fix_project(proj_name)
    elif text == "status":
        projects = load_projects()
        msg = "📊 Status dos projetos:\n\n"
        for proj_name in projects.keys():
            status = state.get("projects", {}).get(proj_name, {}).get("status", "unknown")
            emoji = "✅" if status == "success" else "❌" if status == "failed" else "❓"
            msg += f"{emoji} {proj_name}: {status}\n"
        await send_telegram(msg)
    elif text == "help":
        msg = """
🤖 DevGuardian Daemon

Comandos:
• fix <projeto> - Corrigir erro
• status - Ver status de todos
• help - Ver ajuda
"""
        await send_telegram(msg)

async def monitor_loop(context: ContextTypes.DEFAULT_TYPE):
    """Monitora builds periodicamente"""
    await check_builds()

def main():
    logger.info("🚀 DevGuardian Central Daemon iniciado")

    if not TELEGRAM_BOT_TOKEN or not ANTHROPIC_API_KEY:
        logger.error("❌ Faltam credenciais")
        sys.exit(1)

    projects = load_projects()
    if not projects:
        logger.error("❌ Nenhum projeto configurado em projects_config.json")
        sys.exit(1)

    logger.info(f"📁 Projetos: {', '.join(projects.keys())}")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Job de monitoramento
    config = json.load(open(CONFIG_FILE))
    interval = config.get("monitor_interval", 30)
    app.job_queue.run_repeating(monitor_loop, interval=interval, first=0)

    logger.info(f"⏱️ Monitorando a cada {interval}s")
    logger.info("🤖 Pronto! Enviando mensagens via Telegram...")

    app.run_polling()

if __name__ == "__main__":
    main()
