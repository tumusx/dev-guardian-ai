# DevGuardian 🤖

Background **monitor** for macbook that detects build/IDE errors, notifies you on Telegram/Slack, and Claude resolves + pushes to GitHub.

Runs 24/7 as a Launchd Agent (native macOS).

## Quick Start (5 minutes)

```bash
# 1. Clone and setup
cd ~/Projects/DevGuardian
devguardian setup

# 2. Configure credentials in .env
nano .env

# 3. Start the daemon
devguardian start

# Done! Monitor is running in background 🎉
```

---

## Installation

Inside the DevGuardian directory:

```bash
# Install the CLI command
pip install -e .

# Now 'devguardian' is available globally
```

---

## CLI Commands

| Command | What It Does |
|---|---|
| `devguardian setup` | Initialize: create venv, install deps, scaffold .env |
| `devguardian install` | Install daemon as Launchd Agent (auto-start on reboot) |
| `devguardian start` | Start the daemon |
| `devguardian stop` | Stop the daemon gracefully |
| `devguardian stop -f` | Force kill all processes (nuclear option) |
| `devguardian status` | Show daemon status + last log lines |
| `devguardian logs` | View daemon logs |
| `devguardian logs -f` | Stream logs in real-time |
| `devguardian capture` | Backup logs + config to timestamped folder |
| `devguardian shutdown` | Capture state then stop daemon |

---

## Configuration

### Step 1: Telegram Bot Token

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a name (e.g., "DevGuardianBot")
4. Copy the **TOKEN**

### Step 2: Get Your Chat ID

1. Search for **@userinfobot** on Telegram
2. Send any message
3. It responds with your **ID**

### Step 3: Edit `.env`

```bash
nano .env
```

Fill in:
```
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_id_here
PROJECT_PATH=/path/to/your/project
MONITOR_INTERVAL=30
ANTHROPIC_API_KEY=your_api_key_here
```

### Step 4: Start!

```bash
devguardian start
```

---

## How It Works

```
🔄 Daemon running in background (Launchd)
    ↓
Checks project builds every N seconds
    ↓
Error detected? → Send Telegram notification
    ↓
You approve via Telegram → Claude fixes code
    ↓
Auto-fixer runs tests, build, push
```

---

## For Slack (Corporate)

If your company uses Slack:

1. Create app at https://api.slack.com/apps
2. Enable "Files" and "Message Posting"
3. Copy **Slack Bot Token** (starts with `xoxb-`)
4. Add to `.env`:
   ```
   SLACK_BOT_TOKEN=xoxb-your-token
   SLACK_CHANNEL=#devguardian
   ```

Daemon will use Slack if Telegram is not configured.

---

## Project Structure

```
~/Projects/DevGuardian/
├── cli.py               # CLI commands (start, stop, status, logs, capture)
├── daemon.py            # Main daemon loop (monitors builds, handles fixes)
├── detector.py          # Error detection (logs, tests, git status)
├── auto_fixer.py        # Auto-fix runner (deps, tests, build, push)
├── setup.sh             # Legacy setup (can also use 'devguardian setup')
├── install_daemon.sh    # Legacy installer (can also use 'devguardian install')
├── projects_config.json # Project registry
├── .env                 # Your credentials (local only, not in git)
├── .gitignore           # Protects .env and secrets
└── README.md            # This file
```

---

## Monitoring Details

The daemon monitors:

✅ **Build Commands**
- Configured `build_cmd` per project (e.g., `./gradlew build`)
- Error detection via stdout/stderr patterns

✅ **Log Files**
- `build.log`, `npm-debug.log`, `test-results.log`
- Any file in `.logs/` directory

✅ **Test Results**
- `test-results.json` (numFailedTests)
- Coverage reports

✅ **Patterns** (auto-detected)
- ERROR, error, failed, FAILED
- Exception, panic, fatal, crash
- Module not found, import error

---

## Troubleshooting

### Daemon won't start
```bash
# Check status
devguardian status

# View recent logs
devguardian logs -f

# Reinstall
devguardian install
```

### Not getting Telegram notifications
1. Check your token:
   ```bash
   curl https://api.telegram.org/bot[YOUR_TOKEN]/getMe
   ```
2. Verify `.env` has correct token and chat ID
3. Check daemon logs: `devguardian logs`

### Want to see backups
```bash
ls -la ~/.devguardian/backups/
```

### Want to debug manually
```bash
python3 daemon.py
python3 detector.py
```

---

## Future Plans

- [ ] Web dashboard for history
- [ ] Multiple project support
- [ ] GitHub Issues integration
- [ ] Email notifications
- [ ] Slack file uploads

---

**Made with ❤️ for makers who aren't glued to their desk**
