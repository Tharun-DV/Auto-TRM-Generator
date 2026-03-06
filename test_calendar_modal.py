#!/usr/bin/env python3
"""
Test script to visualize the new calendar modal structure
"""

from datetime import datetime, timedelta

def show_modal_structure():
    """Display the new calendar modal structure"""
    
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    
    modal = {
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
    
    print("=" * 60)
    print("NEW CALENDAR MODAL STRUCTURE")
    print("=" * 60)
    print()
    print("📋 Modal Title: TRM Report Generator")
    print()
    print("📅 Start Date Picker:")
    print(f"   - Type: datepicker")
    print(f"   - Default: {yesterday.strftime('%Y-%m-%d')} (yesterday)")
    print(f"   - Label: Start Date")
    print()
    print("📅 End Date Picker:")
    print(f"   - Type: datepicker")
    print(f"   - Default: {yesterday.strftime('%Y-%m-%d')} (yesterday)")
    print(f"   - Label: End Date")
    print()
    print("💡 Tip: Select the same date for single-day reports")
    print()
    print("=" * 60)
    print("VISUAL REPRESENTATION")
    print("=" * 60)
    print()
    print("┌────────────────────────────────────────────────────┐")
    print("│         TRM Report Generator                       │")
    print("├────────────────────────────────────────────────────┤")
    print("│                                                    │")
    print("│  Select Date Range:                               │")
    print("│  Choose start and end dates for your TRM report   │")
    print("│                                                    │")
    print("│  Start Date                                        │")
    print(f"│  [📅 {yesterday.strftime('%Y-%m-%d')} ▼]                         │")
    print("│                                                    │")
    print("│  End Date                                          │")
    print(f"│  [📅 {yesterday.strftime('%Y-%m-%d')} ▼]                         │")
    print("│                                                    │")
    print("│  💡 Quick tip: Select the same date for both      │")
    print("│  start and end to generate a single-day report    │")
    print("│                                                    │")
    print("├────────────────────────────────────────────────────┤")
    print("│                          [Cancel] [Generate Report]│")
    print("└────────────────────────────────────────────────────┘")
    print()
    print("=" * 60)
    print("USAGE EXAMPLES")
    print("=" * 60)
    print()
    print("📌 Example 1: Single Day Report (Yesterday)")
    print("   Start Date: 2026-03-05")
    print("   End Date:   2026-03-05")
    print("   → Generates report for March 5 only")
    print()
    print("📌 Example 2: Weekly Report")
    print("   Start Date: 2026-03-02 (Monday)")
    print("   End Date:   2026-03-08 (Sunday)")
    print("   → Generates report for the entire week")
    print()
    print("📌 Example 3: Custom Date Range")
    print("   Start Date: 2026-02-25")
    print("   End Date:   2026-03-04")
    print("   → Generates report for Feb 25 - Mar 4")
    print()
    print("=" * 60)
    print("VALIDATION")
    print("=" * 60)
    print()
    print("✅ Valid: End date same as or after start date")
    print("❌ Invalid: End date before start date")
    print("   Error: 'End date cannot be before start date. Please try again.'")
    print()
    print("=" * 60)
    print()
    
    return modal

if __name__ == "__main__":
    show_modal_structure()
    print("✅ Calendar modal structure is ready!")
    print()
    print("Next steps:")
    print("1. Run the bot: python app.py")
    print("2. Type /trm in Slack")
    print("3. Use the calendar pickers to select dates")
    print("4. Click 'Generate Report'")
