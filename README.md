# Auto-TRM-Generator

An AI-powered Slack bot that generates Technical Review Meeting (TRM) reports for the Swiggy DevOps team by analyzing messages from the #devops-help channel.

## Features

- 📅 **Flexible Date Parsing**: `week 8`, `Feb 25 to Mar 4 2026`, `last week`
- 🤖 **AI-Powered Summarization**: Uses Claude Sonnet 4.5 via Portkey AI
- 📊 **Structured Reports**: Issues, Metrics, Alerts, Outages, Action Items
- 💬 **Slack Integration**: Fetches messages and posts formatted reports
- ⚙️ **Configurable**: AI model, channel ID, message limits

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
# or with venv
venv/bin/python -m pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
export SLACK_BOT_TOKEN='xoxb-your-bot-token'
export SLACK_APP_TOKEN='xapp-your-app-token'
export PORTKEY_API_KEY='your-portkey-api-key'
export PORTKEY_MODEL='pilot-poc/claude-sonnet-4-5'  # Optional, defaults to this
```

### 3. Run the Bot
```bash
python app.py
```

### 4. Use in Slack
Type `/trm` in Slack - a modal will appear asking for the week or date range.

**Examples of inputs:**
- `week 8`
- `Feb 25 to Mar 4 2026`
- `last week`
- `yesterday`

## Documentation

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick command reference
- **[TRM_BOT_GUIDE.md](TRM_BOT_GUIDE.md)** - Comprehensive user guide
- **[MODEL_CONFIGURATION.md](MODEL_CONFIGURATION.md)** - AI model selection guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture & flow
- **[UPGRADE_SUMMARY.md](UPGRADE_SUMMARY.md)** - What changed in the upgrade
- **[SETUP.md](SETUP.md)** - Initial setup instructions
- **[SLACK_APP_SETUP_GUIDE.md](SLACK_APP_SETUP_GUIDE.md)** - Slack app configuration

## How It Works

1. User types `/trm` in Slack
2. A modal appears asking for week or date range
3. User enters input (e.g., "week 8" or "Feb 25 to Mar 4 2026") and clicks "Generate Report"
4. Bot parses the date range (e.g., "week 8" → Feb 25 to Mar 4)
5. Bot fetches all messages from #devops-help for that period
6. Bot sends messages to Portkey AI (Claude Sonnet 4.5)
7. AI categorizes issues, extracts metrics, and formats TRM report
8. Bot posts formatted report back to user via DM

## Report Structure

- 📋 **Header** - Week number, date range, oncall name
- 🔴 **Issues** - Categorized by Compute, Infrasec, Haproxy, Latency, Alerting, Logging
- 📊 **P0 Metrics** - P1 Alerts, Infrasec P0, RCAs
- 🚨 **Alerts Summary** - Component, alert name, frequency
- 💰 **Cost Highlights** - Week-over-week comparison
- 🔥 **Outages Summary** - Severity, reason, owner
- 🎫 **Ticket Data** - Total, status breakdown
- ✅ **Action Items** - Description, owner, ETA

## Configuration

### AI Model (Default: Claude Sonnet 4.5)
```bash
export PORTKEY_MODEL='pilot-poc/claude-sonnet-4-5'  # Claude Sonnet 4.5 (Default)
export PORTKEY_MODEL='gpt-4o'                        # OpenAI GPT-4o
export PORTKEY_MODEL='claude-3-opus-20240229'        # Claude 3 Opus
```

### Channel ID (Default: #devops-help)
Edit `app.py` line 17:
```python
DEVOPS_HELP_CHANNEL_ID = "C6P2C6938"
```

### Message Limit (Default: 200)
Edit `app.py` line 120:
```python
combined_text = "\n".join(messages[:200])
```

## Required Slack Permissions

- `commands` - For /trm slash command
- `channels:history` - Read messages from #devops-help
- `channels:read` - Access channel info
- `chat:write` - Send reports to users

## Testing

Run the test suite:
```bash
venv/bin/python test_bot.py
```

Test with a small date range:
```
/trm yesterday
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No messages found | Check channel ID, bot permissions, date range |
| API error | Verify PORTKEY_API_KEY, check quota |
| Permission denied | Add `channels:history` scope, re-install app |
| Date parsing error | Use clearer format: "Feb 25 to Mar 4 2026" |

See [TRM_BOT_GUIDE.md](TRM_BOT_GUIDE.md) for detailed troubleshooting.

## Development

### File Structure
```
Auto-TRM-Generator/
├── app.py                        # Main bot application (295 lines)
├── requirements.txt              # Python dependencies
├── env.example                   # Environment variable template
├── test_bot.py                   # Test suite
├── TRM_BOT_GUIDE.md             # Comprehensive guide
├── QUICK_REFERENCE.md           # Quick reference
├── MODEL_CONFIGURATION.md       # AI model guide
├── ARCHITECTURE.md              # System architecture
├── UPGRADE_SUMMARY.md           # Upgrade details
└── venv/                        # Virtual environment
```

### Key Functions

- `fetch_slack_messages()` - Fetches messages from Slack with pagination
- `parse_date_range()` - Parses date input into timestamps
- `summarize_with_portkey()` - Generates TRM report via AI
- `handle_trm_command()` - Main /trm command handler

## Support

1. Check documentation in this repo
2. Review Slack bot logs
3. Check Portkey AI dashboard for API issues
4. Verify Slack app configuration

## License

Internal tool for Swiggy DevOps team.

---

**Version:** 2.0  
**Last Updated:** March 6, 2026  
**Default AI Model:** Claude Sonnet 4.5 (`pilot-poc/claude-sonnet-4-5`)