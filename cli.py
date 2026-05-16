#!/usr/bin/env python3

import typer
import subprocess
import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

app = typer.Typer(help="DevGuardian CLI - Background build monitor and auto-fixer")

LOG_DIR = Path.home() / ".devguardian"
BACKUPS_DIR = LOG_DIR / "backups"
PLIST_PATH = Path.home() / "Library/LaunchAgents/com.devguardian.daemon.plist"
PLIST_LABEL = "com.devguardian.daemon"
PROJECT_ROOT = Path(__file__).parent


def run_cmd(cmd: str, check: bool = True) -> str:
    """Run shell command, return stdout."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        typer.echo(f"❌ Command failed: {cmd}", err=True)
        typer.echo(f"   Error: {result.stderr}", err=True)
        raise typer.Exit(1)
    return result.stdout.strip()


def is_daemon_running() -> bool:
    """Check if daemon.py is running."""
    try:
        run_cmd("pgrep -f 'python.*daemon.py'", check=False)
        return True
    except:
        return False


@app.command()
def setup():
    """Initialize DevGuardian (venv, dependencies, .env)."""
    typer.echo("🚀 Setting up DevGuardian...")

    venv_path = PROJECT_ROOT / "venv"
    if venv_path.exists():
        typer.echo("✅ venv already exists")
    else:
        typer.echo("📦 Creating virtual environment...")
        run_cmd(f"python3 -m venv {venv_path}")

    typer.echo("📦 Installing dependencies...")
    pip = str(venv_path / "bin" / "pip")
    run_cmd(f"{pip} install -e {PROJECT_ROOT} -q")

    env_example = PROJECT_ROOT / ".env.example"
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists() and env_example.exists():
        typer.echo("📝 Creating .env from template...")
        shutil.copy(env_example, env_file)
        typer.echo(f"   ✏️  Edit {env_file} with your credentials")

    screenshots_dir = LOG_DIR / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    typer.echo("✅ Setup complete!")


@app.command()
def install():
    """Install daemon as macOS Launchd Agent."""
    typer.echo("📋 Installing DevGuardian daemon...")

    if not PLIST_PATH.parent.exists():
        PLIST_PATH.parent.mkdir(parents=True, exist_ok=True)

    venv_python = PROJECT_ROOT / "venv" / "bin" / "python3"
    if not venv_python.exists():
        typer.echo("❌ Virtual environment not found. Run 'devguardian setup' first.", err=True)
        raise typer.Exit(1)

    daemon_script = PROJECT_ROOT / "daemon.py"
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{PLIST_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{venv_python}</string>
        <string>{daemon_script}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{LOG_DIR}/daemon.log</string>
    <key>StandardErrorPath</key>
    <string>{LOG_DIR}/daemon_stderr.log</string>
    <key>WorkingDirectory</key>
    <string>{PROJECT_ROOT}</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>HOME</key>
        <string>{Path.home()}</string>
    </dict>
</dict>
</plist>
"""

    with open(PLIST_PATH, "w") as f:
        f.write(plist_content)
    typer.echo(f"✅ Plist created: {PLIST_PATH}")

    typer.echo("🚀 Loading daemon with launchctl...")
    try:
        run_cmd(f"launchctl load {PLIST_PATH}")
    except:
        typer.echo("⚠️  launchctl load failed (may already be loaded)")

    import time
    time.sleep(1)

    if is_daemon_running():
        typer.echo("✅ Daemon is running!")
    else:
        typer.echo("⚠️  Daemon may not have started yet. Check 'devguardian status'")


@app.command()
def start():
    """Start the DevGuardian daemon."""
    typer.echo("🚀 Starting DevGuardian...")

    if is_daemon_running():
        typer.echo("✅ Daemon already running")
        return

    if not PLIST_PATH.exists():
        typer.echo("📋 Plist not found, creating...")
        install()
        return

    typer.echo("🔧 Loading daemon with launchctl...")
    try:
        run_cmd(f"launchctl load {PLIST_PATH}")
    except:
        pass

    import time
    time.sleep(1)

    if is_daemon_running():
        typer.echo("✅ Daemon started!")
        typer.echo(f"📊 View logs: devguardian logs -f")
    else:
        typer.echo("❌ Failed to start daemon", err=True)
        raise typer.Exit(1)


@app.command()
def stop(force: bool = typer.Option(False, "--force", "-f", help="Force kill all processes")):
    """Stop the DevGuardian daemon."""
    if force:
        typer.echo("💥 Force stopping all DevGuardian processes...")
        run_cmd("launchctl unload ~/Library/LaunchAgents/com.devguardian.daemon.plist 2>/dev/null || true")
        run_cmd("pkill -9 -f 'python.*daemon.py' || true")
        run_cmd("pkill -9 gradle || true")
        run_cmd("pkill -9 gradlew || true")
        run_cmd("pkill -9 java || true")
        run_cmd("find ~/.gradle -name '*.lock' -delete 2>/dev/null || true")
        typer.echo("✅ All processes stopped")
    else:
        typer.echo("🛑 Stopping DevGuardian daemon...")
        run_cmd(f"launchctl unload {PLIST_PATH} 2>/dev/null || true")
        import time
        time.sleep(1)
        run_cmd("pkill -9 -f 'python.*daemon.py' 2>/dev/null || true")
        typer.echo("✅ Daemon stopped")

        log_file = LOG_DIR / "daemon.log"
        if log_file.exists():
            typer.echo("\n📊 Last 10 log lines:")
            lines = run_cmd(f"tail -10 {log_file}")
            typer.echo(lines)


@app.command()
def status():
    """Show daemon status."""
    typer.echo("📊 DevGuardian Status\n")

    typer.echo("🔷 Launchd:")
    try:
        output = run_cmd(f"launchctl list | grep {PLIST_LABEL}", check=False)
        if output:
            typer.echo(f"  ✅ {output}")
        else:
            typer.echo(f"  ❌ Not loaded")
    except:
        typer.echo("  ❌ Not loaded")

    typer.echo("\n🔷 Process:")
    try:
        pid = run_cmd("pgrep -f 'python.*daemon.py'", check=False)
        if pid:
            typer.echo(f"  ✅ Running (PID: {pid})")
        else:
            typer.echo("  ❌ Not running")
    except:
        typer.echo("  ❌ Not running")

    typer.echo("\n🔷 Recent Logs:")
    log_file = LOG_DIR / "daemon.log"
    if log_file.exists():
        lines = run_cmd(f"tail -5 {log_file}")
        for line in lines.split("\n"):
            typer.echo(f"  {line}")
    else:
        typer.echo("  (no logs yet)")


@app.command()
def logs(
    follow: bool = typer.Option(False, "--follow", "-f", help="Stream logs"),
    lines: int = typer.Option(20, "--lines", "-n", help="Number of lines to show"),
):
    """View daemon logs."""
    log_file = LOG_DIR / "daemon.log"

    if not log_file.exists():
        typer.echo("❌ Log file not found", err=True)
        raise typer.Exit(1)

    if follow:
        typer.echo(f"📜 Streaming {log_file}...\n")
        os.system(f"tail -f {log_file}")
    else:
        typer.echo(f"📜 Last {lines} lines of {log_file}:\n")
        output = run_cmd(f"tail -{lines} {log_file}")
        typer.echo(output)


@app.command()
def capture():
    """Backup logs and configuration."""
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUPS_DIR / f"state_{timestamp}"
    backup_path.mkdir(exist_ok=True)

    typer.echo("📸 Capturing DevGuardian state...\n")

    typer.echo("📋 Copying logs...")
    for log_file in ["daemon.log", "daemon_stderr.log"]:
        src = LOG_DIR / log_file
        if src.exists():
            shutil.copy(src, backup_path / log_file)
            typer.echo(f"  ✅ {log_file}")

    typer.echo("📝 Copying configuration...")
    config_file = PROJECT_ROOT / "projects_config.json"
    if config_file.exists():
        shutil.copy(config_file, backup_path / "projects_config.json")
        typer.echo(f"  ✅ projects_config.json")

    typer.echo("🖥️  Capturing system status...")
    status_file = backup_path / "system_status.txt"
    with open(status_file, "w") as f:
        f.write("=== LAUNCHCTL STATUS ===\n")
        try:
            output = run_cmd(f"launchctl list | grep {PLIST_LABEL}", check=False)
            f.write(output + "\n" if output else "No service found\n")
        except:
            f.write("No service found\n")

        f.write("\n=== DAEMON PROCESSES ===\n")
        try:
            output = run_cmd("pgrep -f 'python.*daemon.py'", check=False)
            f.write(output + "\n" if output else "No process found\n")
        except:
            f.write("No process found\n")

    typer.echo(f"  ✅ system_status.txt")

    typer.echo(f"\n✅ State captured in: {backup_path}")
    typer.echo(f"\n📁 Contents:")
    os.system(f"ls -lah {backup_path}")


@app.command()
def shutdown():
    """Capture state and stop daemon."""
    capture()
    typer.echo("\n")
    stop()


if __name__ == "__main__":
    app()
