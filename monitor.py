#!/usr/bin/env python3
"""
DevGuardian Monitor - Detecta erros e notifica via Telegram/Slack
Roda em background como Launchd Agent
"""
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import requests
import time

from detector import ErrorDetector

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL")
PROJECT_PATH = os.getenv("PROJECT_PATH", os.getcwd())
MONITOR_INTERVAL = int(os.getenv("MONITOR_INTERVAL", "30"))

class Notifier:
    def __init__(self):
        self.detector = ErrorDetector(PROJECT_PATH)

    def log(self, msg: str):
        """Log centralizado"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {msg}"
        print(log_msg)

        log_file = Path.home() / ".devguardian" / "monitor.log"
        with open(log_file, 'a') as f:
            f.write(log_msg + "\n")

    def send_telegram_error(self, error: dict, screenshot_path: Path = None) -> bool:
        """Envia erro via Telegram"""
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            self.log("⚠️ Telegram not configured")
            return False

        try:
            caption = f"""
🚨 **ERROR DETECTED**

⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔴 Type: {error['type']}
📍 Severity: {error.get('severity', 'medium')}

**Error:**
```
{error['message'][:300]}
```

✅ **Next Step:**
1. Open Claude (web or Claude Code)
2. Paste this screenshot
3. Say "Fix this error"
4. Claude will resolve and push to GitHub
"""

            if screenshot_path and screenshot_path.exists():
                with open(screenshot_path, 'rb') as photo:
                    files = {'photo': photo}
                    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
                    data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
                    response = requests.post(url, files=files, data=data, timeout=10)
                    return response.status_code == 200
            else:
                # Sem screenshot, envia só texto
                url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                data = {'chat_id': TELEGRAM_CHAT_ID, 'text': caption, 'parse_mode': 'Markdown'}
                response = requests.post(url, data=data, timeout=10)
                return response.status_code == 200

        except Exception as e:
            self.log(f"❌ Telegram error: {e}")
            return False

    def send_slack_error(self, error: dict) -> bool:
        """Envia erro via Slack"""
        if not SLACK_BOT_TOKEN or not SLACK_CHANNEL:
            self.log("⚠️ Slack not configured")
            return False

        try:
            text = f"""
🚨 *ERROR DETECTED*

⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔴 Type: {error['type']}
📍 Severity: {error.get('severity', 'medium')}

*Error:*
```
{error['message'][:300]}
```

✅ *Next Step:*
1. Open Claude
2. Describe the error
3. Claude will fix and push
"""

            url = "https://slack.com/api/chat.postMessage"
            headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
            data = {"channel": SLACK_CHANNEL, "text": text}

            response = requests.post(url, headers=headers, json=data, timeout=10)
            return response.status_code == 200

        except Exception as e:
            self.log(f"❌ Slack error: {e}")
            return False

    def take_screenshot(self) -> Path:
        """Captura screenshot da tela inteira"""
        import subprocess

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_file = Path.home() / ".devguardian" / "screenshots" / f"error_{timestamp}.png"
        screenshot_file.parent.mkdir(parents=True, exist_ok=True)

        cmd = f"screencapture -x {screenshot_file}"
        subprocess.run(cmd, shell=True, capture_output=True)

        if screenshot_file.exists():
            self.log(f"📸 Screenshot saved: {screenshot_file}")
            return screenshot_file
        else:
            self.log("❌ Screenshot failed")
            return None

    def run(self):
        """Loop principal do monitor"""
        self.log("="*60)
        self.log("🚀 DevGuardian Monitor Started (Background Mode)")
        self.log(f"📁 Project: {PROJECT_PATH}")
        self.log(f"⏱️ Interval: {MONITOR_INTERVAL}s")
        self.log(f"📱 Telegram: {'✅' if TELEGRAM_BOT_TOKEN else '❌'}")
        self.log(f"💼 Slack: {'✅' if SLACK_BOT_TOKEN else '❌'}")
        self.log("="*60)

        error_count = 0
        last_error_msg = None

        while True:
            try:
                # Detecta erro
                error = self.detector.detect_error()

                if error:
                    error_count += 1

                    # Evita notificar múltiplas vezes do mesmo erro
                    if error['message'] == last_error_msg:
                        self.log(f"⏭️ Skipping duplicate error notification")
                        time.sleep(MONITOR_INTERVAL)
                        continue

                    last_error_msg = error['message']

                    self.log(f"\n🚨 ERROR #{error_count} DETECTED!")
                    self.log(f"Type: {error['type']}")
                    self.log(f"Message: {error['message'][:200]}")

                    # Screenshot
                    screenshot = self.take_screenshot()
                    time.sleep(1)  # Aguarda screenshot completar

                    # Notifica
                    self.log("📤 Sending notifications...")

                    telegram_ok = self.send_telegram_error(error, screenshot) if TELEGRAM_BOT_TOKEN else False
                    slack_ok = self.send_slack_error(error) if SLACK_BOT_TOKEN else False

                    if telegram_ok:
                        self.log("✅ Telegram notification sent!")
                    if slack_ok:
                        self.log("✅ Slack notification sent!")

                    if not (telegram_ok or slack_ok):
                        self.log("⚠️ No notifications sent (check configuration)")

                    self.log("⏳ Waiting for next check...\n")

                else:
                    last_error_msg = None

                time.sleep(MONITOR_INTERVAL)

            except KeyboardInterrupt:
                self.log("\n👋 Monitor stopped by user")
                break
            except Exception as e:
                self.log(f"❌ Error in main loop: {e}")
                time.sleep(MONITOR_INTERVAL)

        self.log("🛑 Monitor closed")


if __name__ == "__main__":
    notifier = Notifier()
    notifier.run()
