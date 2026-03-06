import os
import sys
import ssl
import certifi
import re
import requests
import dateparser
from datetime import datetime, timedelta
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.web.client import WebClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
PORTKEY_API_KEY = os.environ.get("PORTKEY_API_KEY")
PORTKEY_MODEL = os.environ.get("PORTKEY_MODEL", "pilot-poc/claude-sonnet-4-5")
DEVOPS_HELP_CHANNEL_ID = os.environ.get("DEVOPS_HELP_CHANNEL_ID", "C0AKTULBYHW")

# SSL Configuration - disable verification if behind corporate proxy
# Set DISABLE_SSL_VERIFY=1 to disable SSL verification (not recommended for production)
if os.environ.get("DISABLE_SSL_VERIFY") == "1":
    print("⚠️  WARNING: Running with SSL verification disabled!")
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
else:
    ssl_context = ssl.create_default_context(cafile=certifi.where())

if not SLACK_BOT_TOKEN:
    print("Error: SLACK_BOT_TOKEN environment variable is not set.")
    print("\nPlease set your environment variables:")
    print("  export SLACK_BOT_TOKEN='xoxb-your-bot-token'")
    print("  export SLACK_APP_TOKEN='xapp-your-app-token'")
    print("\nSee SETUP.md for detailed instructions.")
    sys.exit(1)

if not SLACK_APP_TOKEN:
    print("Error: SLACK_APP_TOKEN environment variable is not set.")
    print("\nPlease set your environment variables:")
    print("  export SLACK_BOT_TOKEN='xoxb-your-bot-token'")
    print("  export SLACK_APP_TOKEN='xapp-your-app-token'")
    print("  export PORTKEY_API_KEY='your-portkey-api-key'")
    print("\nSee SETUP.md for detailed instructions.")
    sys.exit(1)

if not PORTKEY_API_KEY:
    print("Error: PORTKEY_API_KEY environment variable is not set.")
    print("\nPlease set your environment variables:")
    print("  export PORTKEY_API_KEY='your-portkey-api-key'")
    print("\nSee SETUP.md for detailed instructions.")
    sys.exit(1)

client = WebClient(token=SLACK_BOT_TOKEN, ssl=ssl_context)
app = App(client=client)


def fetch_slack_messages(client: WebClient, channel_id: str, oldest: float, latest: float):
    """Fetch all messages from a Slack channel within a time range."""
    messages = []
    cursor = None
    
    try:
        while True:
            result = client.conversations_history(
                channel=channel_id,
                oldest=str(oldest),
                latest=str(latest),
                limit=200,
                cursor=cursor
            )
            
            for msg in result.get("messages", []):
                if msg.get("text"):
                    user_id = msg.get("user", "Unknown")
                    timestamp = datetime.fromtimestamp(float(msg.get("ts", 0)))
                    text = msg["text"]
                    messages.append(f"[{timestamp}] {text}")
            
            if not result.get("response_metadata", {}).get("next_cursor"):
                break
            cursor = result["response_metadata"]["next_cursor"]
    except Exception as e:
        print(f"Error fetching Slack messages: {e}")
        return []
    
    return messages


def parse_date_range(text: str):
    """Parse user input like 'Feb 25 to Mar 4 2026' or 'week 8' into Unix timestamps."""
    text = text.strip().lower()
    
    # Handle "last week" - return full week range (Monday to Sunday)
    if text in ['last week', 'lastweek', 'previous week']:
        today = datetime.now()
        # Get Monday of last week
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday + 7)
        start_date = last_monday.replace(hour=0, minute=0, second=0, microsecond=0)
        # Get Sunday of last week
        end_date = start_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
        week_num = start_date.isocalendar()[1]
        return start_date.timestamp(), end_date.timestamp(), start_date.strftime("%b %d"), end_date.strftime("%b %d"), week_num
    
    # Handle "this week" - return full week range (Monday to Sunday)
    if text in ['this week', 'thisweek', 'current week']:
        today = datetime.now()
        # Get Monday of this week
        days_since_monday = today.weekday()
        this_monday = today - timedelta(days=days_since_monday)
        start_date = this_monday.replace(hour=0, minute=0, second=0, microsecond=0)
        # Get Sunday of this week
        end_date = start_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
        week_num = start_date.isocalendar()[1]
        return start_date.timestamp(), end_date.timestamp(), start_date.strftime("%b %d"), end_date.strftime("%b %d"), week_num
    
    # Handle "week N" format
    week_match = re.match(r'week\s+(\d+)', text, re.IGNORECASE)
    if week_match:
        week_num = int(week_match.group(1))
        # Calculate week dates (assuming week 1 starts on Jan 1)
        year = datetime.now().year
        start_date = datetime(year, 1, 1) + timedelta(weeks=week_num - 1)
        # Adjust to Monday if Jan 1 is not Monday
        days_to_monday = (7 - start_date.weekday()) % 7
        if start_date.weekday() != 0:  # If not Monday
            start_date = start_date + timedelta(days=days_to_monday)
        end_date = start_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
        return start_date.timestamp(), end_date.timestamp(), start_date.strftime("%b %d"), end_date.strftime("%b %d"), week_num
    
    # Handle "date to date" format
    parts = re.split(r'\s+to\s+', text, flags=re.IGNORECASE)
    if len(parts) == 2:
        start_date = dateparser.parse(parts[0].strip())
        end_date = dateparser.parse(parts[1].strip())
        
        if start_date and end_date:
            # Set start date to beginning of day
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            # Set end date to end of day
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            week_num = start_date.isocalendar()[1]
            return start_date.timestamp(), end_date.timestamp(), start_date.strftime("%b %d"), end_date.strftime("%b %d"), week_num
    
    # Try to parse as a single date (for "yesterday", specific dates, etc.)
    parsed = dateparser.parse(text)
    if parsed:
        start_date = parsed.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = parsed.replace(hour=23, minute=59, second=59, microsecond=999999)
        week_num = start_date.isocalendar()[1]
        return start_date.timestamp(), end_date.timestamp(), start_date.strftime("%b %d"), end_date.strftime("%b %d"), week_num
    
    raise ValueError(f"Could not parse date range from: {text}")


def summarize_with_portkey(messages: list, start_date: str, end_date: str, week_num: int) -> str:
    """Send messages to Portkey AI for TRM summarization."""
    # Limit messages to avoid token overflow
    combined_text = "\n".join(messages[:200])
    
    prompt = f"""You are a DevOps TRM (Technical Review Meeting) report generator for Swiggy.
Given the following Slack messages from #devops-help for Week {week_num} ({start_date} to {end_date}),
generate a structured TRM report in Slack mrkdwn format with these sections:

1. Issues (categorized by: Compute, Infrasec, Haproxy, Latency, Alerting, Logging) - summarize similar issues together
2. P0 Metrics (P1 Alerts count, Infrasec P0, S1/S2/S3 RCAs) - extract counts if mentioned
3. Alerts Summary (component, alert name, frequency, description) - group by component
4. Cost Highlights (if any cost/billing mentioned)
5. Outages Summary (if any S1/S2 severity incidents mentioned)
6. Ticket Data summary (total count, status breakdown if mentioned)
7. Action Items / AIs (owner and ETA if mentioned)

Use this exact format (Slack mrkdwn):

*📋 ProdEngg TRM — Week {week_num} | {start_date} to {end_date}*
*DevOps Oncall:* <extract from messages or use "TBD">
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*🔴 Issues (from #devops-help)*
| Theme/Vertical | Description |
|---|---|
| Compute | <AI-summarized issues or "None"> |
| Infrasec | <AI-summarized issues or "None"> |
| Haproxy | <AI-summarized issues or "None"> |
| Latency | <AI-summarized issues or "None"> |
| Alerting | <AI-summarized issues or "None"> |
| Logging | <AI-summarized issues or "None"> |

*📊 P0 Metrics*
| # | Metric | Value |
|---|---|---|
| 1 | P1 Alerts | <count or 0> |
| 2 | Infra sec P0 | <count or 0> |
| 3 | S1 RCAs | <count or 0> |
| 4 | S2/S3 RCAs | <count or 0> |

*🚨 Alerts Summary*
| Component | Alert | Frequency | Description |
|---|---|---|---|
<add rows if alerts mentioned, else "No alerts reported">

*💰 Cost Highlights*
| Resource | Last Week | This Week |
|---|---|---|
<add rows if cost data mentioned, else "No cost data mentioned">

*🔥 Outages Summary*
| Outage/RCA | Severity | Reason | Owner | Date |
|---|---|---|---|---|
<add rows if outages mentioned, else "No outages reported">

*🎫 Ticket Data*
- Total Tickets: <N or "Not specified">
- Date Range: {start_date} to {end_date}
- Status: Closed: X | Blocked: Y | Open: Z

*✅ Action Items (TRM AIs)*
| Description | Owner | ETA |
|---|---|---|
<add rows if action items mentioned, else "No action items">

Messages:
{combined_text}
"""
    
    headers = {
        "x-portkey-api-key": PORTKEY_API_KEY,
        "Content-Type": "application/json"
    }
    
    body = {
        "model": PORTKEY_MODEL,
        "messages": [
            {"role": "system", "content": "You are a DevOps reporting assistant for Swiggy. Generate concise, structured TRM reports."},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        # Disable SSL verification if requested (for corporate proxies)
        verify_ssl = os.environ.get("DISABLE_SSL_VERIFY") != "1"
        response = requests.post(
            "https://api.portkey.ai/v1/chat/completions",
            json=body,
            headers=headers,
            timeout=60,
            verify=verify_ssl
        )
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Error generating TRM report: {str(e)}\n\nPlease check your Portkey API configuration and try again."


@app.command("/trm")
def handle_trm_command(ack, body, client):
    """Handle /trm command - opens modal for date range selection."""
    ack()
    
    # Get today's date for default values
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "trm_modal",
            "title": {"type": "plain_text", "text": "TRM Report Generator"},
            "submit": {"type": "plain_text", "text": "Generate Report"},
            "close": {"type": "plain_text", "text": "Cancel"},
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Select Date Range:*\nChoose start and end dates for your TRM report"
                    }
                },
                {
                    "type": "input",
                    "block_id": "start_date_block",
                    "element": {
                        "type": "datepicker",
                        "action_id": "start_date_input",
                        "initial_date": yesterday.strftime("%Y-%m-%d"),
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select start date"
                        }
                    },
                    "label": {"type": "plain_text", "text": "Start Date"}
                },
                {
                    "type": "input",
                    "block_id": "end_date_block",
                    "element": {
                        "type": "datepicker",
                        "action_id": "end_date_input",
                        "initial_date": yesterday.strftime("%Y-%m-%d"),
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select end date"
                        }
                    },
                    "label": {"type": "plain_text", "text": "End Date"}
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "💡 *Quick tip:* Select the same date for both start and end to generate a single-day report"
                        }
                    ]
                }
            ]
        }
    )


@app.view("trm_modal")
def handle_trm_modal_submission(ack, body, client, view):
    """Handle TRM modal submission - generate and send report."""
    # Extract the date range from the modal
    start_date_str = view["state"]["values"]["start_date_block"]["start_date_input"]["selected_date"]
    end_date_str = view["state"]["values"]["end_date_block"]["end_date_input"]["selected_date"]
    user_id = body["user"]["id"]
    
    # Acknowledge the modal submission immediately
    ack()
    
    # Validate input
    if not start_date_str or not end_date_str:
        client.chat_postMessage(
            channel=user_id,
            text="❌ Please select both start and end dates."
        )
        return
    
    # Send acknowledgment message
    client.chat_postMessage(
        channel=user_id,
        text=f"🔄 Generating TRM report for: *{start_date_str} to {end_date_str}*\n\nFetching messages from #devops-help..."
    )
    
    try:
        # Parse selected dates (format: YYYY-MM-DD)
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        
        # Validate date range
        if end_date < start_date:
            client.chat_postMessage(
                channel=user_id,
                text="❌ End date cannot be before start date. Please try again."
            )
            return
        
        # Set timestamps to cover full days
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Get Unix timestamps
        oldest = start_date.timestamp()
        latest = end_date.timestamp()
        
        # Format dates for display
        start_date_display = start_date.strftime("%b %d")
        end_date_display = end_date.strftime("%b %d")
        week_num = start_date.isocalendar()[1]
        
        # Fetch messages from #devops-help
        messages = fetch_slack_messages(client, DEVOPS_HELP_CHANNEL_ID, oldest, latest)
        
        if not messages:
            client.chat_postMessage(
                channel=user_id,
                text=f"⚠️ No messages found in #devops-help for the period: {start_date_display} to {end_date_display}"
            )
            return
        
        # Update user
        client.chat_postMessage(
            channel=user_id,
            text=f"✅ Found {len(messages)} messages. Generating TRM report with AI..."
        )
        
        # Generate TRM report using Portkey AI
        trm_report = summarize_with_portkey(messages, start_date_display, end_date_display, week_num)
        
        # Post TRM report
        client.chat_postMessage(
            channel=user_id,
            text=trm_report
        )
        
    except Exception as e:
        client.chat_postMessage(
            channel=user_id,
            text=f"❌ Error generating TRM report: {str(e)}\n\nPlease try again or contact support."
        )


if __name__ == "__main__":
    print("⚡️ Slack TRM Bot is starting...")
    print(f"📁 Environment file loaded: .env")
    print(f"📊 Configuration:")
    print(f"   • Channel ID: {DEVOPS_HELP_CHANNEL_ID}")
    print(f"   • AI Model: {PORTKEY_MODEL}")
    print(f"   • SSL Verify: {'Disabled' if os.environ.get('DISABLE_SSL_VERIFY') == '1' else 'Enabled'}")
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    print("✅ Bot is running! Use /trm in your Slack workspace.")
    handler.start()
