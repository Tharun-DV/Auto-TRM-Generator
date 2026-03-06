# TRM Bot - Modal Interface Guide

## Visual Flow

```
┌─────────────────────────────────────────┐
│  User in Slack                          │
│  Types: /trm                            │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  🖼️  Modal Appears                                      │
│  ┌───────────────────────────────────────────────────┐  │
│  │  TRM Report Generator                      [X]    │  │
│  ├───────────────────────────────────────────────────┤  │
│  │                                                   │  │
│  │  Week or Date Range                              │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │ e.g., week 8, Feb 25 to Mar 4 2026...     │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  │                                                   │  │
│  │  Examples:                                        │  │
│  │  • week 8 - Week 8 of current year               │  │
│  │  • Feb 25 to Mar 4 2026 - Specific date range    │  │
│  │  • last week - Previous week                     │  │
│  │  • yesterday - Yesterday only                    │  │
│  │                                                   │  │
│  ├───────────────────────────────────────────────────┤  │
│  │                          [Cancel] [Generate Report]│  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
              │
              │ User enters: "week 8"
              │ User clicks: "Generate Report"
              ▼
┌─────────────────────────────────────────┐
│  Modal closes                           │
│  Bot sends DM to user                   │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────┐
│  🔄 Generating TRM report for: week 8               │
│                                                      │
│  Fetching messages from #devops-help...            │
└─────────────┬───────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────┐
│  ✅ Found 150 messages.                             │
│                                                      │
│  Generating TRM report with AI...                  │
└─────────────┬───────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────┐
│  📋 ProdEngg TRM — Week 8 | Feb 25 to Mar 4        │
│  DevOps Oncall: John Doe                           │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━                      │
│                                                      │
│  🔴 Issues (from #devops-help)                     │
│  | Theme/Vertical | Description |                   │
│  |---|---|                                          │
│  | Compute | High CPU usage on prod-3... |         │
│  ...                                                │
│                                                      │
│  📊 P0 Metrics                                      │
│  ...                                                │
└─────────────────────────────────────────────────────┘
```

## Modal Fields Explained

### Input Field: "Week or Date Range"

**Purpose:** Where users enter the time period for the report

**Accepts:**
- Week numbers: `week 8`, `week 10`
- Relative dates: `last week`, `yesterday`, `today`
- Date ranges: `Feb 25 to Mar 4 2026`, `March 1 to March 7`
- Single dates: `March 1`, `yesterday`

**Validation:**
- Cannot be empty
- Must be parseable by `dateparser` library
- Shows error if invalid format

### Context Section: "Examples"

**Purpose:** Help users understand what to enter

**Shows:**
- 4 example formats
- Brief explanation of each
- Uses Slack markdown formatting

### Buttons

**"Generate Report"** (Primary)
- Submits the form
- Triggers report generation
- Modal closes on click

**"Cancel"** (Secondary)
- Closes modal without action
- No report generated
- No side effects

## Input Examples with Expected Behavior

### ✅ Valid Inputs

| Input | Parsed As | Output |
|-------|-----------|--------|
| `week 8` | Week 8 of 2026 (Feb 25 - Mar 4) | Report for that week |
| `week 10` | Week 10 of 2026 | Report for that week |
| `Feb 25 to Mar 4 2026` | Exact date range | Report for Feb 25-Mar 4 |
| `last week` | Previous calendar week | Report for last week |
| `yesterday` | Yesterday's date | Report for yesterday |
| `March 1` | March 1, 2026 (full day) | Report for March 1 |
| `2 weeks ago` | Two weeks before today | Report for that week |

### ❌ Invalid Inputs

| Input | Error | Reason |
|-------|-------|--------|
| (empty) | ❌ Please provide a date range | No input |
| `xyz123` | ❌ Date parsing error | Not a valid date format |
| `week` | ❌ Could not parse date | Missing week number |
| `next year` | ❌ Could not parse date | Too ambiguous |

## Error Handling

### User Sees:

1. **Empty Input**
   ```
   ❌ Please provide a date range.

   Examples:
   • week 8
   • Feb 25 to Mar 4 2026
   • last week
   ```

2. **Invalid Date Format**
   ```
   ❌ Date parsing error: Could not parse date range from: xyz123

   Please use formats like:
   • week 8
   • Feb 25 to Mar 4 2026
   • last week
   ```

3. **No Messages Found**
   ```
   ⚠️ No messages found in #devops-help for the period: Feb 25 to Mar 4
   ```

4. **API Error**
   ```
   ❌ Error generating TRM report: Connection timeout

   Please check your Portkey API configuration and try again.
   ```

## Modal Design Details

### Colors & Styling
- Uses Slack's default modal styling
- Primary button: Green (Slack default)
- Secondary button: Gray (Slack default)
- Context text: Gray, smaller font

### Accessibility
- Input field is keyboard accessible
- Tab order: Input → Cancel → Generate Report
- Enter key submits form (clicks Generate Report)
- Escape key closes modal (same as Cancel)

### Mobile Support
- Modal is responsive
- Works on Slack mobile apps (iOS/Android)
- Input field uses native mobile keyboards

## Code Snippet: Modal Definition

```python
{
    "type": "modal",
    "callback_id": "trm_modal",
    "title": {"type": "plain_text", "text": "TRM Report Generator"},
    "submit": {"type": "plain_text", "text": "Generate Report"},
    "close": {"type": "plain_text", "text": "Cancel"},
    "blocks": [
        {
            "type": "input",
            "block_id": "date_range_block",
            "element": {
                "type": "plain_text_input",
                "action_id": "date_range_input",
                "placeholder": {
                    "type": "plain_text",
                    "text": "e.g., week 8, Feb 25 to Mar 4 2026, last week"
                }
            },
            "label": {"type": "plain_text", "text": "Week or Date Range"}
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "*Examples:*\n• `week 8` - Week 8 of current year\n• `Feb 25 to Mar 4 2026` - Specific date range\n• `last week` - Previous week\n• `yesterday` - Yesterday only"
                }
            ]
        }
    ]
}
```

## Testing Checklist

- [ ] Type `/trm` - modal appears
- [ ] Enter "week 8" - report generates
- [ ] Enter "yesterday" - report generates
- [ ] Leave empty - error message shown
- [ ] Enter invalid text - error message shown
- [ ] Click Cancel - modal closes, no action
- [ ] Test on mobile - modal works correctly
- [ ] Test with long input - handles gracefully

## Tips for Users

### 💡 Quick Tips

1. **Use Week Numbers for Consistency**
   - `week 8` is clearer than "Feb 25 to Mar 4"
   - Easier for team communication

2. **Test with "yesterday" First**
   - Quick way to verify bot is working
   - Faster than waiting for a full week's data

3. **Be Specific with Date Ranges**
   - Include the year: "Feb 25 to Mar 4 2026"
   - Avoids ambiguity

4. **Use Relative Dates for Recurring Reports**
   - "last week" always works for weekly reports
   - No need to calculate dates

## Troubleshooting

### Modal doesn't appear
1. Check bot is running: `ps aux | grep app.py`
2. Verify Slack app has `commands` scope
3. Re-install bot in Slack workspace

### "Generate Report" doesn't do anything
1. Check bot logs for errors
2. Verify all env vars are set
3. Test with simple input: "yesterday"

### Modal appears but with different fields
1. Check you're using the updated `app.py`
2. Restart the bot: `python app.py`
3. Clear Slack cache (logout/login)

---

*Last updated: March 6, 2026*
