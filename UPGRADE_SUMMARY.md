# TRM Bot Upgrade Summary

## What Was Changed

### 1. **Dependencies Added** (requirements.txt)
- `slack-sdk>=3.19.0` - For advanced Slack API operations
- `requests>=2.31.0` - For Portkey AI API calls
- `dateparser>=1.1.8` - For flexible date parsing

### 2. **New Environment Variables** (env.example)
- `PORTKEY_API_KEY` - Required for AI-powered TRM report generation
- `PORTKEY_MODEL` - AI model to use (default: `pilot-poc/claude-sonnet-4-5`)

### 3. **Core Functionality Implemented** (app.py)

#### Helper Functions Added:
- **`fetch_slack_messages()`** - Fetches messages from #devops-help channel with pagination
- **`parse_date_range()`** - Parses user input like "week 8" or "Feb 25 to Mar 4 2026" into timestamps
- **`summarize_with_portkey()`** - Sends messages to Portkey AI and returns formatted TRM report

#### Command Handler Updated:
- **`handle_trm_command()`** - Completely rewritten to:
  - Accept date range as command parameter (e.g., `/trm week 8`)
  - Fetch Slack messages from #devops-help
  - Generate AI-powered TRM report
  - Post formatted report back to user
  - Handle errors gracefully with helpful messages

### 4. **Documentation Created**
- `TRM_BOT_GUIDE.md` - Comprehensive guide covering:
  - Usage examples
  - Report structure
  - Setup instructions
  - Troubleshooting
  - API integration details
  - Best practices

## How to Use

### Quick Start
1. Set environment variables:
   ```bash
   export SLACK_BOT_TOKEN='xoxb-your-token'
   export SLACK_APP_TOKEN='xapp-your-token'
   export PORTKEY_API_KEY='your-portkey-key'
   export PORTKEY_MODEL='pilot-poc/claude-sonnet-4-5'  # Optional, this is default
   ```

2. Install dependencies:
   ```bash
   venv/bin/python -m pip install -r requirements.txt
   ```

3. Run the bot:
   ```bash
   python app.py
   ```

### Using the Bot
Send commands in Slack:
- `/trm week 8` - Generate report for week 8
- `/trm Feb 25 to Mar 4 2026` - Generate report for specific date range
- `/trm last week` - Generate report for last week

## Required Slack Permissions
Update your Slack app with these OAuth scopes:
- `commands` - For /trm slash command
- `channels:history` - To read #devops-help messages
- `channels:read` - To access channel info
- `chat:write` - To send reports

## Report Format
The bot generates structured TRM reports with:
- 📋 Header (Week #, Date Range, Oncall)
- 🔴 Issues (categorized by Compute, Infrasec, Haproxy, Latency, Alerting, Logging)
- 📊 P0 Metrics (P1 Alerts, Infrasec P0, RCAs)
- 🚨 Alerts Summary
- 💰 Cost Highlights
- 🔥 Outages Summary
- 🎫 Ticket Data
- ✅ Action Items

## Key Features
✅ Flexible date parsing (week numbers, relative dates, specific ranges)
✅ Automatic message pagination (handles 200+ messages)
✅ AI-powered categorization and summarization (Claude Sonnet 4.5)
✅ Configurable AI model via environment variable
✅ Error handling with helpful user feedback
✅ Slack markdown formatting for rich reports
✅ Channel ID configurable (default: #devops-help C6P2C6938)

## What's Preserved
- ✅ Original SSL certificate handling
- ✅ Environment variable validation
- ✅ Socket mode connection
- ✅ Legacy modal handler (backward compatibility)

## Testing
To test the bot:
1. Ensure all environment variables are set
2. Run `python app.py`
3. In Slack, send `/trm yesterday` for a quick test
4. Verify the bot fetches messages and generates a report

## Next Steps
1. Set up your Portkey AI account and get API key
2. Update Slack app permissions (channels:history, channels:read)
3. Configure environment variables
4. Test with a small date range first
5. Review the generated report format
6. Adjust the AI prompt if needed (in `summarize_with_portkey()`)

## Notes
- The bot processes up to 200 messages per request (configurable)
- AI model defaults to `pilot-poc/claude-sonnet-4-5` (configurable via PORTKEY_MODEL)
- Channel ID is hardcoded to #devops-help (C6P2C6938) but can be changed
- Date parsing supports natural language (thanks to dateparser library)

## Troubleshooting
See `TRM_BOT_GUIDE.md` for detailed troubleshooting steps including:
- No messages found
- API errors
- Permission errors
- Date parsing errors
