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
from confluence_integration import confluence

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

# In-memory storage for multi-step modal data
# Structure: {user_id: {category: [entries], metadata: {...}}}
trm_session_data = {}


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


def summarize_with_portkey(messages: list, start_date: str, end_date: str, week_num: int, total_messages: int) -> str:
    """Send messages to Portkey AI for TRM summarization."""
    # Limit messages to avoid token overflow
    messages_to_process = messages[:200]
    combined_text = "\n".join(messages_to_process)
    
    prompt = f"""You are a DevOps TRM (Technical Review Meeting) report generator for Swiggy.
Given {len(messages_to_process)} of {total_messages} total Slack messages from #devops-help for Week {week_num} ({start_date} to {end_date}),
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
*📊 Messages Analyzed:* {total_messages} messages from #devops-help
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


@app.command("/trm-manual")
def handle_trm_manual_command(ack, body, client):
    """Handle /trm-manual command - opens initial setup modal."""
    ack()
    user_id = body["user_id"]
    
    # Get today's date for defaults
    today = datetime.now()
    week_num = today.isocalendar()[1]
    days_since_monday = today.weekday()
    monday = today - timedelta(days=days_since_monday)
    sunday = monday + timedelta(days=6)
    
    # Initialize session data
    trm_session_data[user_id] = {
        "metadata": {
            "week_number": str(week_num),
            "date_range": f"{monday.strftime('%b %d')} to {sunday.strftime('%b %d')}",
            "oncall": ""
        },
        "issues": [],
        "metrics": [],
        "alerts": [],
        "cost": [],
        "outages": [],
        "tickets": [],
        "action_items": []
    }
    
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "trm_setup_modal",
            "title": {"type": "plain_text", "text": "TRM Setup"},
            "submit": {"type": "plain_text", "text": "Continue"},
            "close": {"type": "plain_text", "text": "Cancel"},
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*📋 Manual TRM Report Setup*\nFirst, let's set up the basic information"
                    }
                },
                {
                    "type": "input",
                    "block_id": "week_number_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "week_number_input",
                        "initial_value": str(week_num),
                        "placeholder": {"type": "plain_text", "text": "e.g., 10"}
                    },
                    "label": {"type": "plain_text", "text": "Week Number"}
                },
                {
                    "type": "input",
                    "block_id": "date_range_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "date_range_input",
                        "initial_value": f"{monday.strftime('%b %d')} to {sunday.strftime('%b %d')}",
                        "placeholder": {"type": "plain_text", "text": "e.g., Mar 2 to Mar 8"}
                    },
                    "label": {"type": "plain_text", "text": "Date Range"}
                },
                {
                    "type": "input",
                    "block_id": "oncall_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "oncall_input",
                        "placeholder": {"type": "plain_text", "text": "e.g., John Doe"}
                    },
                    "label": {"type": "plain_text", "text": "DevOps Oncall"}
                }
            ]
        }
    )


@app.view("trm_setup_modal")
def handle_trm_setup_modal_submission(ack, body, client):
    """Handle TRM setup modal submission - save metadata and show category selection."""
    user_id = body["user"]["id"]
    values = body["view"]["state"]["values"]
    
    # Ensure session data exists for this user
    if user_id not in trm_session_data:
        trm_session_data[user_id] = {
            "metadata": {},
            "issues": [],
            "metrics": [],
            "alerts": [],
            "cost": [],
            "outages": [],
            "tickets": [],
            "action_items": []
        }
    
    # Save metadata
    trm_session_data[user_id]["metadata"]["week_number"] = values["week_number_block"]["week_number_input"]["value"]
    trm_session_data[user_id]["metadata"]["date_range"] = values["date_range_block"]["date_range_input"]["value"]
    trm_session_data[user_id]["metadata"]["oncall"] = values["oncall_block"]["oncall_input"]["value"]
    
    # Acknowledge and open category selection modal
    ack(response_action="push", view={
        "type": "modal",
        "callback_id": "trm_category_selection_modal",
        "title": {"type": "plain_text", "text": "Select Categories"},
        "submit": {"type": "plain_text", "text": "Finish & Generate"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📝 Add Data to Your TRM Report*\nSelect a category below to add entries:"
                }
            },
            {
                "type": "actions",
                "block_id": "category_actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "➕ Add Issue"},
                        "action_id": "add_issue_button",
                        "style": "primary"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "📊 Add Metric"},
                        "action_id": "add_metric_button"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "🚨 Add Alert"},
                        "action_id": "add_alert_button"
                    }
                ]
            },
            {
                "type": "actions",
                "block_id": "category_actions_2",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "💰 Add Cost"},
                        "action_id": "add_cost_button"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "🔥 Add Outage"},
                        "action_id": "add_outage_button"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "✅ Add Action Item"},
                        "action_id": "add_action_item_button"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": _generate_summary_text(user_id)
                }
            }
        ]
    })


def _generate_summary_text(user_id):
    """Generate summary text showing current entries."""
    if user_id not in trm_session_data:
        return "*Current Entries:* None yet"
    
    data = trm_session_data[user_id]
    summary_parts = ["*Current Entries:*"]
    
    if data["issues"]:
        summary_parts.append(f"• Issues: {len(data['issues'])}")
    if data["metrics"]:
        summary_parts.append(f"• Metrics: {len(data['metrics'])}")
    if data["alerts"]:
        summary_parts.append(f"• Alerts: {len(data['alerts'])}")
    if data["cost"]:
        summary_parts.append(f"• Cost Entries: {len(data['cost'])}")
    if data["outages"]:
        summary_parts.append(f"• Outages: {len(data['outages'])}")
    if data["action_items"]:
        summary_parts.append(f"• Action Items: {len(data['action_items'])}")
    
    if len(summary_parts) == 1:
        summary_parts.append("_No entries added yet. Click a button above to start!_")
    
    return "\n".join(summary_parts)


# Action handlers for category buttons
@app.action("add_issue_button")
def handle_add_issue_button(ack, body, client):
    """Open modal to add an issue - updates the current view."""
    ack()
    # Use views.update instead of views.push to avoid stack limit
    client.views_update(
        view_id=body["view"]["id"],
        view={
            "type": "modal",
            "callback_id": "add_issue_modal",
            "title": {"type": "plain_text", "text": "Add Issue"},
            "submit": {"type": "plain_text", "text": "Add Issue"},
            "close": {"type": "plain_text", "text": "Back"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "theme_block",
                    "element": {
                        "type": "static_select",
                        "action_id": "theme_input",
                        "placeholder": {"type": "plain_text", "text": "Select a theme"},
                        "options": [
                            {"text": {"type": "plain_text", "text": "Compute"}, "value": "Compute"},
                            {"text": {"type": "plain_text", "text": "Infrasec"}, "value": "Infrasec"},
                            {"text": {"type": "plain_text", "text": "Haproxy"}, "value": "Haproxy"},
                            {"text": {"type": "plain_text", "text": "Latency"}, "value": "Latency"},
                            {"text": {"type": "plain_text", "text": "Alerting"}, "value": "Alerting"},
                            {"text": {"type": "plain_text", "text": "Logging"}, "value": "Logging"}
                        ]
                    },
                    "label": {"type": "plain_text", "text": "Theme/Vertical"}
                },
                {
                    "type": "input",
                    "block_id": "description_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "description_input",
                        "multiline": True,
                        "placeholder": {"type": "plain_text", "text": "Describe the issue..."}
                    },
                    "label": {"type": "plain_text", "text": "Description"}
                }
            ]
        }
    )


@app.view("add_issue_modal")
def handle_add_issue_modal_submission(ack, body, client):
    """Save issue entry and return to category selection."""
    user_id = body["user"]["id"]
    values = body["view"]["state"]["values"]
    
    theme = values["theme_block"]["theme_input"]["selected_option"]["value"]
    description = values["description_block"]["description_input"]["value"]
    
    # Save to session
    trm_session_data[user_id]["issues"].append({"theme": theme, "description": description})
    
    # Acknowledge and update parent view
    ack(response_action="update", view={
        "type": "modal",
        "callback_id": "trm_category_selection_modal",
        "title": {"type": "plain_text", "text": "Select Categories"},
        "submit": {"type": "plain_text", "text": "Finish & Generate"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📝 Add Data to Your TRM Report*\n✅ Added {theme} issue!"
                }
            },
            {
                "type": "actions",
                "block_id": "category_actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "➕ Add Issue"},
                        "action_id": "add_issue_button",
                        "style": "primary"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "📊 Add Metric"},
                        "action_id": "add_metric_button"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "🚨 Add Alert"},
                        "action_id": "add_alert_button"
                    }
                ]
            },
            {
                "type": "actions",
                "block_id": "category_actions_2",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "💰 Add Cost"},
                        "action_id": "add_cost_button"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "🔥 Add Outage"},
                        "action_id": "add_outage_button"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "✅ Add Action Item"},
                        "action_id": "add_action_item_button"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": _generate_summary_text(user_id)
                }
            }
        ]
    })


@app.action("add_alert_button")
def handle_add_alert_button(ack, body, client):
    """Open modal to add an alert - updates the current view."""
    ack()
    # Use views.update instead of views.push to avoid stack limit
    client.views_update(
        view_id=body["view"]["id"],
        view={
            "type": "modal",
            "callback_id": "add_alert_modal",
            "title": {"type": "plain_text", "text": "Add Alert"},
            "submit": {"type": "plain_text", "text": "Add Alert"},
            "close": {"type": "plain_text", "text": "Back"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "component_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "component_input",
                        "placeholder": {"type": "plain_text", "text": "e.g., API Gateway"}
                    },
                    "label": {"type": "plain_text", "text": "Component"}
                },
                {
                    "type": "input",
                    "block_id": "alert_name_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "alert_name_input",
                        "placeholder": {"type": "plain_text", "text": "e.g., High Error Rate"}
                    },
                    "label": {"type": "plain_text", "text": "Alert Name"}
                },
                {
                    "type": "input",
                    "block_id": "frequency_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "frequency_input",
                        "placeholder": {"type": "plain_text", "text": "e.g., 15 times/hour"}
                    },
                    "label": {"type": "plain_text", "text": "Frequency"}
                },
                {
                    "type": "input",
                    "block_id": "alert_description_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "alert_description_input",
                        "multiline": True,
                        "placeholder": {"type": "plain_text", "text": "Describe the alert..."}
                    },
                    "label": {"type": "plain_text", "text": "Description"}
                }
            ]
        }
    )


@app.view("add_alert_modal")
def handle_add_alert_modal_submission(ack, body, client):
    """Save alert entry and return to category selection."""
    user_id = body["user"]["id"]
    values = body["view"]["state"]["values"]
    
    component = values["component_block"]["component_input"]["value"]
    alert_name = values["alert_name_block"]["alert_name_input"]["value"]
    frequency = values["frequency_block"]["frequency_input"]["value"]
    description = values["alert_description_block"]["alert_description_input"]["value"]
    
    # Save to session
    trm_session_data[user_id]["alerts"].append({
        "component": component,
        "alert_name": alert_name,
        "frequency": frequency,
        "description": description
    })
    
    # Acknowledge and update parent view
    ack(response_action="update", view={
        "type": "modal",
        "callback_id": "trm_category_selection_modal",
        "title": {"type": "plain_text", "text": "Select Categories"},
        "submit": {"type": "plain_text", "text": "Finish & Generate"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📝 Add Data to Your TRM Report*\n✅ Added alert: {alert_name}"
                }
            },
            {
                "type": "actions",
                "block_id": "category_actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "➕ Add Issue"},
                        "action_id": "add_issue_button",
                        "style": "primary"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "📊 Add Metric"},
                        "action_id": "add_metric_button"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "🚨 Add Alert"},
                        "action_id": "add_alert_button"
                    }
                ]
            },
            {
                "type": "actions",
                "block_id": "category_actions_2",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "💰 Add Cost"},
                        "action_id": "add_cost_button"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "🔥 Add Outage"},
                        "action_id": "add_outage_button"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "✅ Add Action Item"},
                        "action_id": "add_action_item_button"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": _generate_summary_text(user_id)
                }
            }
        ]
    })


@app.action("add_outage_button")
def handle_add_outage_button(ack, body, client):
    """Open modal to add an outage - updates the current view."""
    ack()
    # Use views.update instead of views.push to avoid stack limit
    client.views_update(
        view_id=body["view"]["id"],
        view={
            "type": "modal",
            "callback_id": "add_outage_modal",
            "title": {"type": "plain_text", "text": "Add Outage"},
            "submit": {"type": "plain_text", "text": "Add Outage"},
            "close": {"type": "plain_text", "text": "Back"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "outage_name_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "outage_name_input",
                        "placeholder": {"type": "plain_text", "text": "e.g., Payment Service Outage"}
                    },
                    "label": {"type": "plain_text", "text": "Outage/RCA Name"}
                },
                {
                    "type": "input",
                    "block_id": "severity_block",
                    "element": {
                        "type": "static_select",
                        "action_id": "severity_input",
                        "placeholder": {"type": "plain_text", "text": "Select severity"},
                        "options": [
                            {"text": {"type": "plain_text", "text": "S1"}, "value": "S1"},
                            {"text": {"type": "plain_text", "text": "S2"}, "value": "S2"},
                            {"text": {"type": "plain_text", "text": "S3"}, "value": "S3"}
                        ]
                    },
                    "label": {"type": "plain_text", "text": "Severity"}
                },
                {
                    "type": "input",
                    "block_id": "reason_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "reason_input",
                        "multiline": True,
                        "placeholder": {"type": "plain_text", "text": "Reason for outage..."}
                    },
                    "label": {"type": "plain_text", "text": "Reason"}
                },
                {
                    "type": "input",
                    "block_id": "owner_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "owner_input",
                        "placeholder": {"type": "plain_text", "text": "e.g., DevOps Team"}
                    },
                    "label": {"type": "plain_text", "text": "Owner"}
                },
                {
                    "type": "input",
                    "block_id": "outage_date_block",
                    "element": {
                        "type": "datepicker",
                        "action_id": "outage_date_input",
                        "placeholder": {"type": "plain_text", "text": "Select date"}
                    },
                    "label": {"type": "plain_text", "text": "Date"}
                }
            ]
        }
    )


@app.action("add_cost_button")
def handle_add_cost_button(ack, body, client):
    """Open modal to add a cost entry - updates the current view."""
    ack()
    # Use views.update instead of views.push to avoid stack limit
    client.views_update(
        view_id=body["view"]["id"],
        view={
            "type": "modal",
            "callback_id": "add_cost_modal",
            "title": {"type": "plain_text", "text": "Add Cost Entry"},
            "submit": {"type": "plain_text", "text": "Add Cost"},
            "close": {"type": "plain_text", "text": "Back"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "resource_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "resource_input",
                        "placeholder": {"type": "plain_text", "text": "e.g., WAF, CloudFront, RDS"}
                    },
                    "label": {"type": "plain_text", "text": "Resource"}
                },
                {
                    "type": "input",
                    "block_id": "last_week_cost_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "last_week_cost_input",
                        "placeholder": {"type": "plain_text", "text": "e.g., $1200"}
                    },
                    "label": {"type": "plain_text", "text": "Last Week Cost"}
                },
                {
                    "type": "input",
                    "block_id": "this_week_cost_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "this_week_cost_input",
                        "placeholder": {"type": "plain_text", "text": "e.g., $1350"}
                    },
                    "label": {"type": "plain_text", "text": "This Week Cost"}
                }
            ]
        }
    )


@app.action("add_action_item_button")
def handle_add_action_item_button(ack, body, client):
    """Open modal to add an action item - updates the current view."""
    ack()
    # Use views.update instead of views.push to avoid stack limit
    client.views_update(
        view_id=body["view"]["id"],
        view={
            "type": "modal",
            "callback_id": "add_action_item_modal",
            "title": {"type": "plain_text", "text": "Add Action Item"},
            "submit": {"type": "plain_text", "text": "Add Action Item"},
            "close": {"type": "plain_text", "text": "Back"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "ai_description_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "ai_description_input",
                        "multiline": True,
                        "placeholder": {"type": "plain_text", "text": "e.g., Upgrade Redis cluster"}
                    },
                    "label": {"type": "plain_text", "text": "Description"}
                },
                {
                    "type": "input",
                    "block_id": "ai_owner_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "ai_owner_input",
                        "placeholder": {"type": "plain_text", "text": "e.g., DevOps Team"}
                    },
                    "label": {"type": "plain_text", "text": "Owner"}
                },
                {
                    "type": "input",
                    "block_id": "eta_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "eta_input",
                        "placeholder": {"type": "plain_text", "text": "e.g., Mar 15"}
                    },
                    "label": {"type": "plain_text", "text": "ETA"}
                }
            ]
        }
    )


@app.action("add_metric_button")
def handle_add_metric_button(ack, body, client):
    """Open modal to add a P0 metric - updates the current view."""
    ack()
    # Use views.update instead of views.push to avoid stack limit
    client.views_update(
        view_id=body["view"]["id"],
        view={
            "type": "modal",
            "callback_id": "add_metric_modal",
            "title": {"type": "plain_text", "text": "Add P0 Metric"},
            "submit": {"type": "plain_text", "text": "Add Metric"},
            "close": {"type": "plain_text", "text": "Back"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "p1_alerts_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "p1_alerts_input",
                        "placeholder": {"type": "plain_text", "text": "e.g., 5"}
                    },
                    "label": {"type": "plain_text", "text": "P1 Alerts"}
                },
                {
                    "type": "input",
                    "block_id": "infrasec_p0_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "infrasec_p0_input",
                        "placeholder": {"type": "plain_text", "text": "e.g., 2"}
                    },
                    "label": {"type": "plain_text", "text": "Infrasec P0"}
                },
                {
                    "type": "input",
                    "block_id": "s1_rcas_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "s1_rcas_input",
                        "placeholder": {"type": "plain_text", "text": "e.g., 1"}
                    },
                    "label": {"type": "plain_text", "text": "S1 RCAs"}
                },
                {
                    "type": "input",
                    "block_id": "s23_rcas_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "s23_rcas_input",
                        "placeholder": {"type": "plain_text", "text": "e.g., 3"}
                    },
                    "label": {"type": "plain_text", "text": "S2/S3 RCAs"}
                }
            ]
        }
    )


@app.view("add_outage_modal")
def handle_add_outage_modal_submission(ack, body, client):
    """Save outage entry and return to category selection."""
    user_id = body["user"]["id"]
    values = body["view"]["state"]["values"]
    
    outage_name = values["outage_name_block"]["outage_name_input"]["value"]
    severity = values["severity_block"]["severity_input"]["selected_option"]["value"]
    reason = values["reason_block"]["reason_input"]["value"]
    owner = values["owner_block"]["owner_input"]["value"]
    date = values["outage_date_block"]["outage_date_input"]["selected_date"]
    
    # Save to session
    trm_session_data[user_id]["outages"].append({
        "outage_name": outage_name,
        "severity": severity,
        "reason": reason,
        "owner": owner,
        "date": date
    })
    
    # Acknowledge and return to category selection
    ack(response_action="update", view=_build_category_selection_view(user_id, f"✅ Added outage: {outage_name}"))


@app.view("add_cost_modal")
def handle_add_cost_modal_submission(ack, body, client):
    """Save cost entry and return to category selection."""
    user_id = body["user"]["id"]
    values = body["view"]["state"]["values"]
    
    resource = values["resource_block"]["resource_input"]["value"]
    last_week_cost = values["last_week_cost_block"]["last_week_cost_input"]["value"]
    this_week_cost = values["this_week_cost_block"]["this_week_cost_input"]["value"]
    
    # Save to session
    trm_session_data[user_id]["cost"].append({
        "resource": resource,
        "last_week_cost": last_week_cost,
        "this_week_cost": this_week_cost
    })
    
    # Acknowledge and return to category selection
    ack(response_action="update", view=_build_category_selection_view(user_id, f"✅ Added cost entry for {resource}"))


@app.view("add_action_item_modal")
def handle_add_action_item_modal_submission(ack, body, client):
    """Save action item entry and return to category selection."""
    user_id = body["user"]["id"]
    values = body["view"]["state"]["values"]
    
    description = values["ai_description_block"]["ai_description_input"]["value"]
    owner = values["ai_owner_block"]["ai_owner_input"]["value"]
    eta = values["eta_block"]["eta_input"]["value"]
    
    # Save to session
    trm_session_data[user_id]["action_items"].append({
        "description": description,
        "owner": owner,
        "eta": eta
    })
    
    # Acknowledge and return to category selection
    ack(response_action="update", view=_build_category_selection_view(user_id, "✅ Added action item"))


@app.view("add_metric_modal")
def handle_add_metric_modal_submission(ack, body, client):
    """Save metric entry and return to category selection."""
    user_id = body["user"]["id"]
    values = body["view"]["state"]["values"]
    
    p1_alerts = values["p1_alerts_block"]["p1_alerts_input"]["value"]
    infrasec_p0 = values["infrasec_p0_block"]["infrasec_p0_input"]["value"]
    s1_rcas = values["s1_rcas_block"]["s1_rcas_input"]["value"]
    s23_rcas = values["s23_rcas_block"]["s23_rcas_input"]["value"]
    
    # Save to session (override existing since metrics are singular)
    trm_session_data[user_id]["metrics"] = [{
        "p1_alerts": p1_alerts,
        "infrasec_p0": infrasec_p0,
        "s1_rcas": s1_rcas,
        "s23_rcas": s23_rcas
    }]
    
    # Acknowledge and return to category selection
    ack(response_action="update", view=_build_category_selection_view(user_id, "✅ Updated P0 Metrics"))


def _build_category_selection_view(user_id, message="*📝 Add Data to Your TRM Report*\nSelect a category below to add entries:"):
    """Helper function to build the category selection modal view."""
    return {
        "type": "modal",
        "callback_id": "trm_category_selection_modal",
        "title": {"type": "plain_text", "text": "Select Categories"},
        "submit": {"type": "plain_text", "text": "Finish & Generate"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message
                }
            },
            {
                "type": "actions",
                "block_id": "category_actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "➕ Add Issue"},
                        "action_id": "add_issue_button",
                        "style": "primary"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "📊 Add Metric"},
                        "action_id": "add_metric_button"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "🚨 Add Alert"},
                        "action_id": "add_alert_button"
                    }
                ]
            },
            {
                "type": "actions",
                "block_id": "category_actions_2",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "💰 Add Cost"},
                        "action_id": "add_cost_button"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "🔥 Add Outage"},
                        "action_id": "add_outage_button"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "✅ Add Action Item"},
                        "action_id": "add_action_item_button"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": _generate_summary_text(user_id)
                }
            }
        ]
    }


@app.view("trm_category_selection_modal")
def handle_trm_category_selection_modal_submission(ack, body, client):
    """Handle final submission - generate and post TRM report."""
    user_id = body["user"]["id"]
    
    # Acknowledge
    ack()
    
    # Generate TRM report from session data
    if user_id not in trm_session_data:
        client.chat_postMessage(
            channel=user_id,
            text="❌ Session data not found. Please start over with /trm-manual."
        )
        return
    
    data = trm_session_data[user_id]
    metadata = data["metadata"]
    
    # Build Issues section
    issues_section = ""
    themes = {"Compute": [], "Infrasec": [], "Haproxy": [], "Latency": [], "Alerting": [], "Logging": []}
    
    for issue in data["issues"]:
        theme = issue["theme"]
        if theme in themes:
            themes[theme].append(issue["description"])
    
    for theme, descriptions in themes.items():
        if descriptions:
            issues_section += f"| {theme} | {'; '.join(descriptions)} |\n"
        else:
            issues_section += f"| {theme} | None |\n"
    
    # Build Metrics section
    metrics_section = ""
    if data["metrics"]:
        metrics = data["metrics"][0]
        metrics_section = f"""| 1 | P1 Alerts | {metrics['p1_alerts']} |
| 2 | Infra sec P0 | {metrics['infrasec_p0']} |
| 3 | S1 RCAs | {metrics['s1_rcas']} |
| 4 | S2/S3 RCAs | {metrics['s23_rcas']} |"""
    else:
        metrics_section = "| 1 | P1 Alerts | 0 |\n| 2 | Infra sec P0 | 0 |\n| 3 | S1 RCAs | 0 |\n| 4 | S2/S3 RCAs | 0 |"
    
    # Build Alerts section
    alerts_section = ""
    if data["alerts"]:
        for alert in data["alerts"]:
            alerts_section += f"| {alert['component']} | {alert['alert_name']} | {alert['frequency']} | {alert['description']} |\n"
    else:
        alerts_section = "No alerts reported"
    
    # Build Cost section
    cost_section = ""
    if data["cost"]:
        for cost in data["cost"]:
            cost_section += f"| {cost['resource']} | {cost['last_week_cost']} | {cost['this_week_cost']} |\n"
    else:
        cost_section = "No cost data mentioned"
    
    # Build Outages section
    outages_section = ""
    if data["outages"]:
        for outage in data["outages"]:
            outages_section += f"| {outage['outage_name']} | {outage['severity']} | {outage['reason']} | {outage['owner']} | {outage['date']} |\n"
    else:
        outages_section = "No outages reported"
    
    # Build Action Items section
    action_items_section = ""
    if data["action_items"]:
        for ai in data["action_items"]:
            action_items_section += f"| {ai['description']} | {ai['owner']} | {ai['eta']} |\n"
    else:
        action_items_section = "No action items"
    
    # Build complete TRM report
    trm_report = f"""*📋 ProdEngg TRM — Week {metadata['week_number']} | {metadata['date_range']}*
*DevOps Oncall:* {metadata['oncall']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*🔴 Issues (from #devops-help)*
| Theme/Vertical | Description |
|---|---|
{issues_section.rstrip()}

*📊 P0 Metrics*
| # | Metric | Value |
|---|---|---|
{metrics_section.rstrip()}

*🚨 Alerts Summary*
| Component | Alert | Frequency | Description |
|---|---|---|---|
{alerts_section.rstrip()}

*💰 Cost Highlights*
| Resource | Last Week | This Week |
|---|---|---|
{cost_section.rstrip()}

*🔥 Outages Summary*
| Outage/RCA | Severity | Reason | Owner | Date |
|---|---|---|---|---|
{outages_section.rstrip()}

*🎫 Ticket Data*
- Total Tickets: Not specified
- Date Range: {metadata['date_range']}
- Status: Closed: 0 | Blocked: 0 | Open: 0

*✅ Action Items (TRM AIs)*
| Description | Owner | ETA |
|---|---|---|
{action_items_section.rstrip()}
"""
    
    try:
        # Create Confluence page
        confluence_url = confluence.create_trm_page(metadata, data)
        
        if confluence_url:
            # Post success message with Confluence link
            client.chat_postMessage(
                channel=user_id,
                text=f"✅ TRM Report Created!\n\n📄 *Confluence Page:* {confluence_url}\n\n*Week {metadata['week_number']} | {metadata['date_range']}*\n*Oncall:* {metadata['oncall']}"
            )
        else:
            # Fallback: Post TRM report to Slack if Confluence fails
            client.chat_postMessage(
                channel=user_id,
                text=trm_report
            )
            client.chat_postMessage(
                channel=user_id,
                text="⚠️ Confluence page creation failed. Report posted to Slack instead."
            )
        
        # Clean up session data
        del trm_session_data[user_id]
        
    except Exception as e:
        client.chat_postMessage(
            channel=user_id,
            text=f"❌ Error generating TRM report: {str(e)}"
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
        
        # Update user with message count
        total_messages = len(messages)
        client.chat_postMessage(
            channel=user_id,
            text=f"✅ Found {total_messages} messages from #devops-help. Generating TRM report with AI..."
        )
        
        # Generate TRM report using Portkey AI
        trm_report = summarize_with_portkey(messages, start_date_display, end_date_display, week_num, total_messages)
        
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


# OLD HANDLER - Replaced by new multi-step flow above
# @app.view("trm_manual_modal")
# def handle_trm_manual_modal_submission(ack, body, client, view):
#     """Handle manual TRM modal submission - format and post report."""
#     # Extract all values from the modal
#     values = view["state"]["values"]
#     user_id = body["user"]["id"]
#     
#     # Acknowledge the modal submission immediately
#     ack()
#     
#     # (Old single-form implementation commented out)
#     # ... rest of function commented out ...


if __name__ == "__main__":
    print("⚡️ Slack TRM Bot is starting...")
    print(f"📁 Environment file loaded: .env")
    print(f"📊 Configuration:")
    print(f"   • Channel ID: {DEVOPS_HELP_CHANNEL_ID}")
    print(f"   • AI Model: {PORTKEY_MODEL}")
    print(f"   • SSL Verify: {'Disabled' if os.environ.get('DISABLE_SSL_VERIFY') == '1' else 'Enabled'}")
    print(f"\n📋 Available Commands:")
    print(f"   • /trm - Auto-generate TRM from Slack messages")
    print(f"   • /trm-manual - Manual TRM entry with custom data")
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    print("\n✅ Bot is running! Use /trm or /trm-manual in your Slack workspace.")
    handler.start()
