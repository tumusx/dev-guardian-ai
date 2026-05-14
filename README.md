# DevGuardian 🤖

Background **monitor** for macbook that detects build/IDE errors, notifies you on Telegram/Slack, and Claude resolves + pushes to GitHub.

Runs 24/7 as a Launchd Agent (native macOS).

## Flow

```
🔄 Launchd running in background
    ↓
IDE with error → Monitors logs/files → Screenshot → Telegram/Slack 
    ↓ (you approve on your phone)
Passes screenshot to Claude → Claude resolves
    ↓
Auto-fixer runs tests, build, push
```

## Complete Setup (10 minutes)

### 1️⃣ Initial setup

```bash
cd ~/Projects/DevGuardian
bash setup.sh
```

This will:
- Create virtual environment
- Install dependencies
- Create `.env` for you to fill in

### 2️⃣ Configure Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a name (e.g., "DevGuardianBot")
4. Copy the **TOKEN**

### 3️⃣ Get your Chat ID

1. Search for **@userinfobot** on Telegram
2. Send any message
3. It responds with your **ID**

### 4️⃣ Configure `.env`

```bash
nano .env
```

Fill in:
```
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_id_here
PROJECT_PATH=/path/to/your/project
MONITOR_INTERVAL=30
```

### 5️⃣ Install as Launchd Agent (permanent background)

```bash
bash install_launchd.sh
```

✅ Monitor is now running in background! It will restart automatically even after reboot.

---

## How It Works (Background)

Monitor running continuously:
- ✅ Checks logs every 30s
- ✅ Monitors file changes
- ✅ Checks test results
- ✅ If error found → Takes screenshot + Telegram

You're away from home:
- 📱 Get notification on Telegram
- 🤖 Open Claude, paste screenshot
- 🔧 Claude resolves the code
- 📤 Runs auto-fixer → automatic push

---

## Useful Commands

```bash
# Check status
launchctl list | grep devguardian

# View logs in real time
tail -f ~/.devguardian/monitor_stdout.log

# Stop the monitor
launchctl unload ~/Library/LaunchAgents/com.devguardian.monitor.plist

# Restart the monitor
launchctl unload ~/Library/LaunchAgents/com.devguardian.monitor.plist
launchctl load ~/Library/LaunchAgents/com.devguardian.monitor.plist

# View detected errors
cat ~/.devguardian/detector.log
```

---

## What the Detector Monitors

✅ **Log Files**
- `build.log`
- `npm-debug.log`
- `test-results.log`
- Any file in `.logs/`

✅ **Test Results**
- `test-results.json`
- Coverage reports

✅ **Patterns** (auto-detected)
- ERROR, error, failed, FAILED
- Exception, panic, fatal, crash
- Module not found, import error

---

## Error Workflow

1. **Monitor detects** → Takes IDE screenshot
2. **Telegram notifies** → You see on phone (even away)
3. **You approve** → Open Claude
4. **Claude resolves** → Edits necessary files
5. **Runs auto-fixer**:
   ```bash
   python3 ~/Projects/DevGuardian/auto_fixer.py /path/to/project "error description"
   ```
6. **Auto-fixer**:
   - ✅ Installs dependencies
   - ✅ Runs tests
   - ✅ Build
   - ✅ Git commit + push

---

## For Slack (Corporate)

If your company uses Slack:

1. Create app at https://api.slack.com/apps
2. Enable "Files" and "Message Posting"
3. Copy **Slack Bot Token** (starts with `xoxb-`)
4. Configure `.env`:
   ```
   SLACK_BOT_TOKEN=xoxb-your-token
   SLACK_CHANNEL=#devguardian
   ```

Monitor will automatically use Slack if Telegram is not set.

---

## File Structure

```
~/Projects/DevGuardian/
├── monitor.py           # Main loop (monitors + notifies)
├── detector.py          # Smart detector (logs, files, tests)
├── auto_fixer.py        # Claude runs this (fix + push)
├── install_launchd.sh   # Installs as background service
├── setup.sh             # Initial setup
├── .env                 # Your configuration (create with setup.sh)
└── README.md            # This file
```

---

## Troubleshooting

### "Monitor is not detecting error"
Check logs:
```bash
cat ~/.devguardian/detector.log
```

Test manually:
```bash
python3 detector.py
```

### "Telegram is not sending notification"
Check token:
```bash
curl https://api.telegram.org/bot[YOUR_TOKEN]/getMe
```

### "Launchd is not starting"
Check plist:
```bash
cat ~/Library/LaunchAgents/com.devguardian.monitor.plist
```

Load manually:
```bash
launchctl load ~/Library/LaunchAgents/com.devguardian.monitor.plist
```

---

## Future Versions

- [ ] Web dashboard for history
- [ ] Multiple projects
- [ ] GitHub Issues integration
- [ ] Email notification
- [ ] Slack File Upload with screenshot

---

**Made with ❤️ for makers who are not at home**
