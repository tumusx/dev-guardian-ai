#!/usr/bin/env python3
"""
Detector inteligente de erros - monitora logs, files, processos
"""
import os
import time
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ErrorDetector:
    """Detecta erros monitorando múltiplas fontes"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.log_file = Path.home() / ".devguardian" / "detector.log"
        self.error_db = Path.home() / ".devguardian" / "errors.json"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        self.watch_dirs = [
            self.project_path,
            Path.home() / ".devguardian" / "logs"
        ]

        self.error_patterns = [
            "ERROR", "error", "failed", "FAILED", "Exception",
            "panic", "fatal", "crash", "CRASH", "cannot find",
            "module not found", "import error", "SyntaxError"
        ]

        self.ignore_patterns = ["node_modules", ".git", "__pycache__", "dist", "build"]

    def log(self, msg: str):
        """Log da detecção"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {msg}"
        print(log_msg)
        with open(self.log_file, 'a') as f:
            f.write(log_msg + "\n")

    def check_log_files(self) -> Optional[str]:
        """Monitora arquivos de log"""
        log_paths = [
            self.project_path / "build.log",
            self.project_path / "test-results.log",
            self.project_path / "npm-debug.log",
            self.project_path / ".logs" / "*.log",
            Path.home() / ".devguardian" / "logs" / "*.log",
        ]

        for log_path_pattern in log_paths:
            if "*" in str(log_path_pattern):
                # Wildcard matching
                parent = log_path_pattern.parent
                if parent.exists():
                    for log_file in parent.glob(log_path_pattern.name):
                        error = self._check_file_for_errors(log_file)
                        if error:
                            return error
            else:
                if log_path_pattern.exists():
                    error = self._check_file_for_errors(log_path_pattern)
                    if error:
                        return error

        return None

    def _check_file_for_errors(self, filepath: Path) -> Optional[str]:
        """Verifica arquivo por padrões de erro"""
        try:
            with open(filepath, 'r', errors='ignore') as f:
                lines = f.readlines()

            # Verifica as últimas 50 linhas
            for line in lines[-50:]:
                for pattern in self.error_patterns:
                    if pattern.lower() in line.lower():
                        return line.strip()
        except Exception as e:
            self.log(f"Error reading {filepath}: {e}")

        return None

    def check_process_health(self, process_name: str) -> Optional[str]:
        """Verifica se processo está rodando"""
        try:
            result = subprocess.run(
                f"pgrep -f '{process_name}'",
                shell=True,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return f"Process '{process_name}' is not running"

        except Exception as e:
            self.log(f"Error checking process: {e}")

        return None

    def check_port_health(self, port: int) -> Optional[str]:
        """Verifica se porta está aberta"""
        try:
            result = subprocess.run(
                f"lsof -i :{port} 2>/dev/null | grep -q LISTEN",
                shell=True,
                capture_output=True
            )

            if result.returncode != 0:
                return f"Port {port} is not listening"

        except Exception as e:
            self.log(f"Error checking port: {e}")

        return None

    def check_test_results(self) -> Optional[str]:
        """Verifica resultados de testes"""
        test_files = [
            self.project_path / "test-results.json",
            self.project_path / "coverage/coverage-final.json",
        ]

        for test_file in test_files:
            if test_file.exists():
                try:
                    with open(test_file) as f:
                        data = json.load(f)

                    # Procura por failed tests
                    if isinstance(data, dict):
                        if data.get("numFailedTests", 0) > 0:
                            return f"Tests failed: {data.get('numFailedTests')} failures"
                        if data.get("success") is False:
                            return "Test suite failed"

                except Exception as e:
                    self.log(f"Error reading {test_file}: {e}")

        return None

    def check_git_status(self) -> Optional[str]:
        """Verifica se há problemas no git"""
        try:
            result = subprocess.run(
                "cd {} && git status --porcelain".format(self.project_path),
                shell=True,
                capture_output=True,
                text=True
            )

            # Se tem arquivos não-staged e último commit failed
            if result.stdout.strip():
                # Verifica último commit message para sinais de erro
                log_result = subprocess.run(
                    "cd {} && git log -1 --format=%B".format(self.project_path),
                    shell=True,
                    capture_output=True,
                    text=True
                )

                for pattern in ["revert", "fix", "hotfix"]:
                    if pattern in log_result.stdout.lower():
                        return f"Git: Recent {pattern} detected"

        except Exception as e:
            self.log(f"Error checking git: {e}")

        return None

    def detect_error(self) -> Optional[dict]:
        """Detecta qualquer tipo de erro"""
        self.log("🔍 Scanning for errors...")

        # 1. Checar logs
        error_msg = self.check_log_files()
        if error_msg:
            self.log(f"❌ Found in logs: {error_msg}")
            return {
                "type": "log_error",
                "message": error_msg,
                "severity": "high"
            }

        # 2. Checar testes
        error_msg = self.check_test_results()
        if error_msg:
            self.log(f"❌ Found in tests: {error_msg}")
            return {
                "type": "test_error",
                "message": error_msg,
                "severity": "high"
            }

        # 3. Checar processo (opcional)
        # process_name = os.getenv("WATCH_PROCESS", "node")
        # error_msg = self.check_process_health(process_name)
        # if error_msg:
        #     self.log(f"⚠️ {error_msg}")
        #     return {"type": "process_error", "message": error_msg}

        self.log("✅ No errors detected")
        return None

    def monitor_continuous(self, interval: int = 30):
        """Monitora continuamente por erros"""
        self.log(f"🚀 Starting continuous monitoring (interval: {interval}s)")
        self.log(f"📁 Watching: {self.project_path}")

        error_count = 0
        last_error = None

        while True:
            try:
                error = self.detect_error()

                if error:
                    error_count += 1

                    # Evita duplicatas
                    if error["message"] != last_error:
                        self.log(f"🚨 Error #{error_count}: {error}")
                        last_error = error["message"]

                        # Salvar pra usar depois
                        with open(self.error_db, 'w') as f:
                            json.dump(error, f)

                        return error  # Retorna pra monitor.py handle
                    else:
                        self.log("⏭️ Skipping duplicate error")

                else:
                    last_error = None

                time.sleep(interval)

            except KeyboardInterrupt:
                self.log("👋 Monitoring stopped")
                break
            except Exception as e:
                self.log(f"❌ Error in monitoring: {e}")
                time.sleep(interval)

        return None


class FileWatcher(FileSystemEventHandler):
    """Monitora mudanças de arquivo em tempo real"""

    def __init__(self, detector: ErrorDetector):
        self.detector = detector
        self.last_check = time.time()

    def on_modified(self, event):
        """Arquivo foi modificado"""
        if event.is_directory:
            return

        filepath = Path(event.src_path)

        # Ignora arquivos não relevantes
        if any(ignore in str(filepath) for ignore in self.detector.ignore_patterns):
            return

        # Rate limiting (não checa a cada mudança, só a cada 5s)
        if time.time() - self.last_check < 5:
            return

        self.last_check = time.time()

        # Checa apenas log files
        if any(filepath.name.endswith(ext) for ext in ['.log', '.json']):
            self.detector.log(f"📝 File changed: {filepath.name}")
            # Próxima iteração vai detectar
