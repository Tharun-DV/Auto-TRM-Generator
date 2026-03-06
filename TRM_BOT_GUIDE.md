# TRM Report Bot Guide

## Overview
The TRM (Technical Review Meeting) Report Bot automatically generates structured DevOps reports for the Swiggy team by analyzing messages from the #devops-help Slack channel.

## Features
- 📅 **Date Range Support**: Accepts flexible date formats (`week 8`, `Feb 25 to Mar 4 2026`, `last week`)
- 🤖 **AI-Powered Summarization**: Uses Portkey AI to categorize and summarize issues
- 📊 **Structured Reports**: Generates formatted TRM reports with sections for Issues, Metrics, Alerts, Outages, and Action Items
- 💬 **Slack Integration**: Fetches messages from #devops-help and posts results directly to Slack

## Usage

### Command Format
```
/trm
```

This opens a modal where you can enter the week or date range.

### Modal Input Examples
```
week 8
Feb 25 to Mar 4 2026
last week
yesterday
```

### Bot Flow
1. User types `/trm` in Slack
2. Modal appears with input field for week/date range
3. User enters date range (e.g., "week 8") and clicks "Generate Report"
4. Bot parses the date range
5. Bot fetches messages from #devops-help channel (C6P2C6938)
6. Bot sends messages to Portkey AI for summarization
7. Bot posts formatted TRM report back to user

## Report Structure

The bot generates a report with the following sections:

### 📋 Header
- Week number
- Date range
- DevOps oncall name (extracted from messages or "TBD")

### 🔴 Issues
Categorized by:
- Compute
- Infrasec
- Haproxy
- Latency
- Alerting
- Logging

### 📊 P0 Metrics
- P1 Alerts count
- Infrasec P0 count
- S1 RCAs count
- S2/S3 RCAs count

### 🚨 Alerts Summary
Table with: Component, Alert Name, Frequency, Description

### 💰 Cost Highlights
Week-over-week cost comparison (if mentioned in messages)

### 🔥 Outages Summary
Table with: Outage/RCA, Severity, Reason, Owner, Date

### 🎫 Ticket Data
- Total tickets
- Status breakdown (Closed/Blocked/Open)

### ✅ Action Items
Table with: Description, Owner, ETA

## Setup

### Prerequisites
1. Python 3.8+
2. Slack workspace with bot installed
3. Portkey AI account and API key

### Environment Variables
Create a `.env` file or set these variables:

```bash
export SLACK_BOT_TOKEN='xoxb-your-bot-token'
export SLACK_APP_TOKEN='xapp-your-app-token'
export PORTKEY_API_KEY='your-portkey-api-key'
export PORTKEY_MODEL='pilot-poc/claude-sonnet-4-5'  # Optional, defaults to this
```

### Required Slack Permissions
The bot requires these OAuth scopes:
- `commands` - For slash commands
- `channels:history` - To read messages from #devops-help
- `channels:read` - To access channel information
- `chat:write` - To post messages back to users

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Or with venv
venv/bin/python -m pip install -r requirements.txt

# Run the bot
python app.py
```

## Configuration

### Channel ID
The bot is configured to fetch from #devops-help (Channel ID: C6P2C6938).
To change the channel, update the `DEVOPS_HELP_CHANNEL_ID` variable in `app.py`:

```python
DEVOPS_HELP_CHANNEL_ID = "C6P2C6938"  # Change this to your channel ID
```

### AI Model Configuration
The bot uses Portkey AI with Claude Sonnet 4.5 by default. To change the model, set the `PORTKEY_MODEL` environment variable:

```bash
export PORTKEY_MODEL='pilot-poc/claude-sonnet-4-5'  # Default
# Or use another model:
export PORTKEY_MODEL='gpt-4o'
export PORTKEY_MODEL='claude-3-opus-20240229'
```

The model is configurable in your environment variables and doesn't require code changes.

### Message Limit
The bot processes up to 200 messages per request to avoid token overflow. To adjust this:

```python
combined_text = "\n".join(messages[:200])  # Change 200 to your desired limit
```

## Date Parsing Examples

The bot supports various date formats:

| Input | Parsed As |
|-------|-----------|
| `week 8` | Week 8 of current year (Jan 1 + 7 weeks) |
| `Feb 25 to Mar 4 2026` | Specific date range |
| `last week` | Previous calendar week |
| `yesterday` | Yesterday's date |
| `March 1` | March 1 of current year |

## Troubleshooting

### No messages found
- Verify the channel ID is correct
- Check that the bot has access to #devops-help
- Ensure the date range is correct

### API errors
- Verify `PORTKEY_API_KEY` is set correctly
- Check Portkey API quota/limits
- Review Portkey dashboard for errors

### Permission errors
- Ensure bot has `channels:history` scope
- Re-install the app if scopes were added after installation
- Verify bot is added to #devops-help channel

### Date parsing errors
- Use clearer date formats (e.g., "Feb 25 to Mar 4 2026")
- Try alternative formats like "week 8" or "last week"
- Check that dates are valid

## Development

### File Structure
```
Auto-TRM-Generator/
├── app.py                  # Main bot application
├── requirements.txt        # Python dependencies
├── env.example            # Environment variable template
├── TRM_BOT_GUIDE.md       # This guide
├── README.md              # Project readme
└── SETUP.md               # Setup instructions
```

### Key Functions

#### `fetch_slack_messages(client, channel_id, oldest, latest)`
Fetches all messages from a Slack channel within a time range.

#### `parse_date_range(text)`
Parses user input into Unix timestamps and formatted date strings.

#### `summarize_with_portkey(messages, start_date, end_date, week_num)`
Sends messages to Portkey AI for TRM report generation.

#### `handle_trm_command(ack, body, command, client)`
Main command handler for `/trm` slash command.

## API Integration

### Portkey AI Endpoint
```
POST https://api.portkey.ai/v1/chat/completions
```

### Headers
```json
{
  "x-portkey-api-key": "YOUR_API_KEY",
  "Content-Type": "application/json"
}
```

### Request Body
```json
{
  "model": "gpt-4o",
  "messages": [
    {
      "role": "system",
      "content": "You are a DevOps reporting assistant."
    },
    {
      "role": "user",
      "content": "..."
    }
  ]
}
```

## Best Practices

1. **Regular Backups**: Keep backups of generated TRM reports
2. **Monitoring**: Monitor API usage and costs
3. **Access Control**: Limit bot usage to authorized team members
4. **Data Privacy**: Ensure sensitive information is not exposed in reports
5. **Testing**: Test with different date ranges before production use

## Support

For issues or questions:
1. Check this guide and troubleshooting section
2. Review Slack bot logs
3. Check Portkey AI dashboard for API issues
4. Contact DevOps team lead

## Future Enhancements

Potential improvements:
- [ ] Support for multiple channels
- [ ] Custom report templates
- [ ] Export to PDF/CSV
- [ ] Scheduled automatic reports
- [ ] Integration with JIRA/PagerDuty APIs for real metrics
- [ ] Enhanced NLP for better categorization
- [ ] Historical report comparison
