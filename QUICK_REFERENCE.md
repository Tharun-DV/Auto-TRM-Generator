# TRM Bot - Quick Reference

## 🚀 Quick Start

### 1. Set Environment Variables
```bash
export SLACK_BOT_TOKEN='xoxb-your-bot-token'
export SLACK_APP_TOKEN='xapp-your-app-token'
export PORTKEY_API_KEY='your-portkey-api-key'
export PORTKEY_MODEL='pilot-poc/claude-sonnet-4-5'  # Optional, defaults to this
```

### 2. Start the Bot
```bash
cd /Users/tharun.dv_int/src/tries/Auto-TRM-Generator
python app.py
```

### 3. Use in Slack
```
/trm
```
A modal will appear. Enter week or date range:
- `week 8`
- `Feb 25 to Mar 4 2026`
- `last week`

Then click "Generate Report"

---

## 📋 Input Examples

When the modal appears after typing `/trm`, you can enter:

| Input | Description |
|---------|-------------|
| `week 8` | Generate report for week 8 of current year |
| `week 10` | Generate report for week 10 of current year |
| `Feb 25 to Mar 4 2026` | Generate report for specific date range |
| `last week` | Generate report for last week |
| `yesterday` | Generate report for yesterday |
| `March 1` | Generate report for March 1 |

---

## 🔧 Configuration

### Channel ID (app.py line 16)
```python
DEVOPS_HELP_CHANNEL_ID = "C6P2C6938"  # #devops-help
```

### AI Model (app.py line 16)
```python
PORTKEY_MODEL = os.environ.get("PORTKEY_MODEL", "pilot-poc/claude-sonnet-4-5")
```
Or set via environment variable:
```bash
export PORTKEY_MODEL='pilot-poc/claude-sonnet-4-5'  # Claude Sonnet 4.5
export PORTKEY_MODEL='gpt-4o'                        # OpenAI GPT-4o
export PORTKEY_MODEL='claude-3-opus-20240229'        # Claude 3 Opus
```

### Message Limit (app.py line 120)
```python
combined_text = "\n".join(messages[:200])  # Process up to 200 messages
```

---

## 📊 Report Sections

1. **📋 Header** - Week #, dates, oncall name
2. **🔴 Issues** - Compute, Infrasec, Haproxy, Latency, Alerting, Logging
3. **📊 P0 Metrics** - P1 Alerts, Infrasec P0, RCAs
4. **🚨 Alerts** - Component, alert, frequency, description
5. **💰 Cost** - Week-over-week comparison
6. **🔥 Outages** - Outage/RCA, severity, reason, owner, date
7. **🎫 Tickets** - Total, status breakdown
8. **✅ Action Items** - Description, owner, ETA

---

## 🔑 Required Slack Scopes

Add these in your Slack App settings:
- ✅ `commands` - For /trm slash command
- ✅ `channels:history` - Read #devops-help messages
- ✅ `channels:read` - Access channel info
- ✅ `chat:write` - Send reports to users

---

## 🐛 Common Issues

### "No messages found"
- Check channel ID is correct: `C6P2C6938`
- Verify bot has access to #devops-help
- Confirm date range is valid

### "API Error"
- Check `PORTKEY_API_KEY` is set
- Verify API key is valid
- Check Portkey dashboard for quota

### "Permission denied"
- Add `channels:history` scope
- Re-install Slack app
- Invite bot to #devops-help

### "Could not parse date"
- Use clearer format: "Feb 25 to Mar 4 2026"
- Try "week 8" or "last week"
- Check date is valid

---

## 📁 File Structure

```
Auto-TRM-Generator/
├── app.py                    # Main bot application (294 lines)
├── requirements.txt          # Python dependencies
├── env.example              # Environment variable template
├── test_bot.py              # Test suite
├── TRM_BOT_GUIDE.md         # Comprehensive guide
├── UPGRADE_SUMMARY.md       # What changed in upgrade
├── QUICK_REFERENCE.md       # This file
├── README.md                # Project readme
├── SETUP.md                 # Setup instructions
└── venv/                    # Virtual environment
```

---

## 🧪 Testing

Run the test suite:
```bash
venv/bin/python test_bot.py
```

Test with a small date range first:
```
/trm yesterday
```

---

## 📞 Support

1. Check `TRM_BOT_GUIDE.md` for detailed troubleshooting
2. Review bot logs for errors
3. Check Portkey AI dashboard
4. Verify Slack app configuration

---

## 🔄 Maintenance

### Update Dependencies
```bash
venv/bin/python -m pip install -r requirements.txt --upgrade
```

### Check Bot Status
```bash
ps aux | grep app.py
```

### View Logs
Bot logs are printed to stdout. Consider redirecting to a file:
```bash
python app.py > bot.log 2>&1 &
```

---

## 💡 Tips

- Start with short date ranges for testing
- Review the AI-generated report for accuracy
- Adjust the AI prompt if categorization is off
- Keep Portkey API key secure (never commit to git)
- Monitor API usage to avoid unexpected costs
- Use "week N" format for consistency

---

## 📚 Documentation Files

- **TRM_BOT_GUIDE.md** - Full guide with all details
- **UPGRADE_SUMMARY.md** - What changed in the upgrade
- **QUICK_REFERENCE.md** - This quick reference (you are here)
- **SLACK_APP_SETUP_GUIDE.md** - Slack app setup
- **SETUP.md** - Initial setup instructions

---

## 🎯 Key Features

✅ Flexible date parsing (week numbers, relative dates, ranges)  
✅ Automatic pagination (handles 200+ messages)  
✅ AI-powered categorization (Claude Sonnet 4.5)  
✅ Configurable AI model via PORTKEY_MODEL env var  
✅ Error handling with helpful messages  
✅ Slack markdown formatting  
✅ Channel ID configurable  
✅ SSL certificate handling  
✅ Environment validation  

---

*Last updated: March 6, 2026*
