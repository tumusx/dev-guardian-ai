#!/usr/bin/env python3
"""
Auto-fixer script - Claude roda isso para resolver erros e fazer push
"""
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

class AutoFixer:
    def __init__(self, project_path, error_context=""):
        self.project_path = Path(project_path)
        self.error_context = error_context
        self.log_file = Path.home() / ".devguardian" / "fix_log.txt"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log(self, msg):
        """Log da execução"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {msg}"
        print(log_msg)
        with open(self.log_file, 'a') as f:
            f.write(log_msg + "\n")

    def run_command(self, cmd, description=""):
        """Executa comando e retorna resultado"""
        try:
            self.log(f"▶️ Running: {cmd}")
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                self.log(f"❌ {description} failed")
                self.log(f"Error: {result.stderr}")
                return False
            else:
                self.log(f"✅ {description} successful")
                if result.stdout:
                    self.log(f"Output: {result.stdout[:200]}")
                return True
        except Exception as e:
            self.log(f"❌ Exception: {e}")
            return False

    def install_dependencies(self):
        """Instala dependências"""
        self.log("\n📦 Installing dependencies...")
        return self.run_command("npm install || pip install -r requirements.txt", "Dependencies")

    def run_tests(self):
        """Roda testes"""
        self.log("\n🧪 Running tests...")
        return self.run_command("npm test || pytest", "Tests")

    def run_build(self):
        """Roda build"""
        self.log("\n🔨 Running build...")
        return self.run_command("npm run build || python -m build", "Build")

    def commit_and_push(self, message="Auto-fix: resolved build error"):
        """Faz commit e push"""
        self.log("\n📤 Committing and pushing...")

        # Git status
        self.run_command("git status", "Git status check")

        # Add changes
        self.run_command("git add -A", "Git add")

        # Commit
        if not self.run_command(f'git commit -m "{message}"', "Git commit"):
            self.log("⚠️ No changes to commit")
            return False

        # Push
        if not self.run_command("git push", "Git push"):
            return False

        self.log("✅ Changes pushed to GitHub!")
        return True

    def execute(self):
        """Executa fix completo"""
        self.log("\n" + "="*50)
        self.log("🤖 AUTO-FIXER STARTED")
        self.log(f"Project: {self.project_path}")
        self.log(f"Error context: {self.error_context[:100]}")
        self.log("="*50 + "\n")

        # 1. Instalar dependências
        if not self.install_dependencies():
            self.log("❌ Failed to install dependencies")
            return False

        # 2. Rodar testes (se falhar, volta)
        if not self.run_tests():
            self.log("⚠️ Tests failed - manual intervention needed")
            return False

        # 3. Build
        if not self.run_build():
            self.log("⚠️ Build failed - manual intervention needed")
            return False

        # 4. Fazer push
        if not self.commit_and_push():
            self.log("❌ Failed to push")
            return False

        self.log("\n" + "="*50)
        self.log("✅ AUTO-FIX COMPLETED SUCCESSFULLY!")
        self.log("="*50)
        return True

if __name__ == "__main__":
    project_path = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    error_context = sys.argv[2] if len(sys.argv) > 2 else ""

    fixer = AutoFixer(project_path, error_context)
    success = fixer.execute()
    sys.exit(0 if success else 1)
