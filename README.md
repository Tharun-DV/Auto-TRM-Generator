# Auto-TRM-Generator

An AI-powered Slack bot that generates Technical Review Meeting (TRM) reports for the Swiggy DevOps team by analyzing messages from the #devops-help channel.

## Features

- 📅 **Calendar Date Picker**: Interactive calendar UI to select date ranges
- ✍️ **Manual Entry Mode**: Create TRM reports with custom data via `/trm-manual`
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

#### Option A: Automatic TRM Generation (`/trm`)
Type `/trm` in Slack - a modal will appear with calendar date pickers.

1. Select **Start Date** from the calendar picker
2. Select **End Date** from the calendar picker
3. Click **Generate Report**

The bot will fetch messages from #devops-help and generate an AI-powered TRM report.

#### Option B: Manual TRM Entry (`/trm-manual`)
Type `/trm-manual` in Slack - a modal will appear with input fields.

1. Fill in **Week Number** (auto-filled with current week)
2. Fill in **Date Range** (auto-filled with current week)
3. Fill in **DevOps Oncall** name
4. Optionally fill in Issues, Metrics, Alerts, Cost, Outages, Tickets, Action Items
5. Click **Post TRM Report**

The bot will format and post your custom TRM report. See [TRM_MANUAL_GUIDE.md](TRM_MANUAL_GUIDE.md) for details.

## Documentation

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick command reference
- **[TRM_BOT_GUIDE.md](TRM_BOT_GUIDE.md)** - Comprehensive user guide
- **[TRM_MANUAL_GUIDE.md](TRM_MANUAL_GUIDE.md)** - Manual TRM entry guide
- **[MODEL_CONFIGURATION.md](MODEL_CONFIGURATION.md)** - AI model selection guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture & flow
- **[SETUP.md](SETUP.md)** - Initial setup instructions
- **[SLACK_APP_SETUP_GUIDE.md](SLACK_APP_SETUP_GUIDE.md)** - Slack app configuration

## How It Works

1. User types `/trm` in Slack
2. A modal appears with calendar date pickers for start and end dates
3. User selects dates from the calendar and clicks "Generate Report"
4. Bot validates the date range (end date must be after start date)
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

Test with a small date range by selecting yesterday for both start and end dates.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No messages found | Check channel ID, bot permissions, date range |
| API error | Verify PORTKEY_API_KEY, check quota |
| Permission denied | Add `channels:history` scope, re-install app |
| End date before start date | Select end date after start date in calendar |

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