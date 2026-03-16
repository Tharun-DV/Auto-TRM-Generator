# Auto-TRM-Generator

An AI-powered Slack bot that generates Technical Review Meeting (TRM) reports for the Swiggy DevOps team. Creates professional Confluence pages with structured data.

## Features

- 📅 **Calendar Date Picker**: Interactive calendar UI to select date ranges
- ✍️ **Manual Entry Mode**: Create TRM reports with structured multi-step forms via `/trm-manual`
- 💾 **Draft Management**: Save drafts and continue later (NEW!)
- 🎫 **Jira Integration**: Automatically fetch tickets from Jira projects (NEW!)
- 🎨 **Custom Themes**: Add unlimited custom themes for issues (Networking, Database, Security, etc.)
- 📊 **Enhanced Metrics**: Week-over-week comparison with delta tracking
- 🤖 **AI-Powered Summarization**: Uses Claude Sonnet 4.5 via Portkey AI for `/trm` command
- 📄 **Confluence Integration**: Creates professional pages with Table of Contents
- 💬 **Slack Integration**: Fetches messages and sends Confluence URLs
- ⚙️ **Configurable**: AI model, channel ID, Confluence space, Jira projects

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

# Confluence Integration (Optional)
export CONFLUENCE_URL='https://your-company.atlassian.net/wiki'
export CONFLUENCE_USER='your.email@company.com'
export CONFLUENCE_API_TOKEN='your-confluence-api-token'
export CONFLUENCE_SPACE_KEY='DEVOPS'

# Jira Integration (Optional)
export JIRA_URL='https://your-company.atlassian.net'
export JIRA_USER='your.email@company.com'
export JIRA_API_TOKEN='your-jira-api-token'
export JIRA_PROJECT_KEYS='DEVOPS,INFRA,SRE'
```

See **[CONFLUENCE_SETUP.md](CONFLUENCE_SETUP.md)** for Confluence setup.  
See **[JIRA_INTEGRATION.md](JIRA_INTEGRATION.md)** for Jira setup.

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
Type `/trm-manual` in Slack - a multi-step modal flow will guide you.

**🆕 Draft Management:**
- Work is **automatically saved** after each entry
- Can safely close and continue later
- When reopening, choose "📂 Continue Draft" or "🆕 Start Fresh"
- Manual save with "💾 Save Draft" button
- Clear draft with "🗑️ Clear Draft" button
- See "Last saved" timestamp in modal

**Step 1: Setup**
1. Fill in **Week Number** (auto-filled)
2. Fill in **Date Range** (auto-filled)
3. Fill in **DevOps Oncall** name
4. Click **Continue** → *Auto-saved!*

**Step 2: Add Entries**
- **➕ Add Issue**: Select theme (or custom) + description → *Auto-saved!*
- **📊 Add Metric**: Name, Last Week, Current Week, Delta/Comments → *Auto-saved!*
- **🚨 Add Alert**: Component, alert name, frequency, description → *Auto-saved!*
- **💰 Add Cost**: Resource, last week cost, this week cost → *Auto-saved!*
- **🔥 Add Outage**: Name, severity, reason, owner, date → *Auto-saved!*
- **✅ Add Action Item**: Description, owner, ETA → *Auto-saved!*

Add as many entries as needed for each category!

**Step 3: Save or Generate**
- Click **💾 Save Draft** to save and exit (continue later)
- Click **🗑️ Clear Draft** to delete saved draft
- Click **Finish & Generate** to create Confluence page

**Draft saved at:** `drafts/{user_id}.json`

## New Features (v4.1)

### 🎫 Jira Integration (NEW!)
Automatically fetch tickets from Jira and include in TRM reports!

**Features:**
- Fetches tickets from specified Jira projects
- Filters by TRM date range (created OR updated)
- Shows total count, breakdown by status/priority/type
- Displays top 50 tickets with clickable links
- Embedded directly in Confluence TRM report

**Setup:**
```bash
export JIRA_URL='https://your-company.atlassian.net'
export JIRA_USER='your.email@company.com'
export JIRA_API_TOKEN='your-jira-api-token'
export JIRA_PROJECT_KEYS='DEVOPS,INFRA,SRE'  # Comma-separated
```

**Output:**
```
Ticket Data
• Total Tickets: 45
• Date Range: Mar 2 to Mar 8
• By Status: Open: 12 | In Progress: 15 | Closed: 18
• By Priority: P1: 3 | P2: 15 | P3: 27
• By Type: Bug: 18 | Task: 20 | Story: 7

Ticket Details (Top 50)
[Table with Key, Summary, Status, Priority, Type, Assignee]
```

See **[JIRA_INTEGRATION.md](JIRA_INTEGRATION.md)** for complete documentation.

### 💾 Draft Management
Never lose your work! Save drafts and continue later.

**Auto-Save:**
- Automatically saves after every entry
- No manual save needed (but available)
- Shows "Last saved: [timestamp]" in modal

**Manual Controls:**
- **💾 Save Draft** button - Save and exit
- **🗑️ Clear Draft** button - Delete saved draft
- **📂 Continue Draft** - Resume from where you left off

**Example Workflow:**
```
1. Run /trm-manual
2. Setup: Week 10, dates, oncall → Auto-saved!
3. Add 2 issues → Auto-saved!
4. Need to leave? Click "💾 Save Draft"
5. Close modal safely

[Later...]
6. Run /trm-manual
7. "Draft Found! (Last saved: Mar 6, 2026 at 02:30 PM)"
8. Click "📂 Continue Draft"
9. Continue adding entries...
10. Finish & Generate → Draft auto-deleted!
```

See **[DRAFT_FEATURE.md](DRAFT_FEATURE.md)** for complete documentation.

### 🎨 Custom Themes for Issues
Not limited to predefined themes! Add your own:
- Networking
- Database
- Security
- CI/CD
- Monitoring
- Or any theme you need!

**Usage:**
```
Click "Add Issue"
→ Theme: Custom
→ Custom Theme: "Networking"
→ Description: "DNS timeouts in prod"
```

### 📊 Enhanced Metrics
Track week-over-week changes with context:

| Metric Name | Last Week | Current Week | Delta/Comments |
|-------------|-----------|--------------|----------------|
| P1 Alerts | 5 | 8 | +3 (↑60%), Feature rollout |
| API Latency | 120ms | 95ms | -25ms (↓21%), Optimized |

**Usage:**
```
Click "Add Metric"
→ Metric Name: "API Latency (p95)"
→ Last Week: "120ms"
→ Current Week: "95ms"
→ Delta: "-25ms (↓21%), Query optimization"
```

See **[NEW_FEATURES.md](NEW_FEATURES.md)** for detailed examples.

## Report Structure

### Confluence Page Output:
```
ProdEngg TRM — Week 10 | Mar 2 to Mar 8
DevOps Oncall: Alice

Table of Contents:
• Issues
• Metrics
• Alerts Summary
• Cost Highlights
• Outages Summary
• Ticket Data
• Action Items

━━━━━━━━━━━━━━━━━━━━━━━━━━

Issues
┌─────────────┬──────────────────────────┐
│ Theme       │ Description              │
├─────────────┼──────────────────────────┤
│ Compute     │ High CPU on servers      │
│ Database    │ Slow queries             │
│ Networking  │ DNS timeouts             │
└─────────────┴──────────────────────────┘

Metrics
┌────────────────┬───────────┬──────────────┬─────────────────┐
│ Metric Name    │ Last Week │ Current Week │ Delta/Comments  │
├────────────────┼───────────┼──────────────┼─────────────────┤
│ P1 Alerts      │ 5         │ 8            │ +3, Rollout     │
│ API Latency    │ 120ms     │ 95ms         │ -25ms, Better   │
└────────────────┴───────────┴──────────────┴─────────────────┘

[... other sections ...]
```

### Sections Included:
- 📋 **Header** - Week number, date range, oncall name
- 📑 **Table of Contents** - Clickable section links (Confluence only)
- 🔴 **Issues** - Categorized by theme/vertical (custom themes supported)
- 📊 **Metrics** - Week-over-week comparison with delta tracking
- 🚨 **Alerts Summary** - Component, alert name, frequency
- 💰 **Cost Highlights** - Week-over-week comparison
- 🔥 **Outages Summary** - Severity, reason, owner
- 🎫 **Ticket Data** - Total, status breakdown
- ✅ **Action Items** - Description, owner, ETA

## Configuration

### AI Model (Default: Claude Sonnet 4.5)
```bash
export PORTKEY_MODEL='pilot-poc/claude-sonnet-4-5'  # Default
export PORTKEY_MODEL='gpt-4o'                        # OpenAI GPT-4o
export PORTKEY_MODEL='claude-3-opus-20240229'        # Claude 3 Opus
```

### Channel ID (Default: #devops-help)
Edit `app.py` or set environment variable:
```bash
export DEVOPS_HELP_CHANNEL_ID='C6P2C6938'
```

### Message Limit for AI (Default: 200)
Edit `app.py` line ~240:
```python
combined_text = "\n".join(messages[:200])
```

### Confluence Space & Parent Page
```bash
export CONFLUENCE_SPACE_KEY='DEVOPS'           # Space key
export CONFLUENCE_PARENT_ID='123456789'        # Optional: Parent page ID
```

## Required Slack Permissions

- `commands` - For /trm and /trm-manual slash commands
- `channels:history` - Read messages from #devops-help
- `channels:read` - Access channel info
- `chat:write` - Send Confluence URLs to users

## Testing

Run the test suite:
```bash
venv/bin/python test_bot.py
```

Test manually in Slack:
1. `/trm-manual`
2. Fill in basic info
3. Add 1-2 issues with custom themes
4. Add 1-2 metrics with delta
5. Generate and verify Confluence page

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No messages found | Check channel ID, bot permissions, date range |
| API error | Verify PORTKEY_API_KEY, check quota |
| Permission denied | Add `channels:history` scope, re-install app |
| Confluence page not created | Check CONFLUENCE_URL, CONFLUENCE_USER, CONFLUENCE_API_TOKEN |
| Modal errors | Restart bot, check Slack app configuration |

See [CONFLUENCE_SETUP.md](CONFLUENCE_SETUP.md) for Confluence-specific troubleshooting.

## Documentation

- **[SETUP.md](SETUP.md)** - Initial setup instructions
- **[CONFLUENCE_SETUP.md](CONFLUENCE_SETUP.md)** - Confluence integration guide
- **[JIRA_INTEGRATION.md](JIRA_INTEGRATION.md)** - Jira integration guide (NEW!)
- **[DRAFT_FEATURE.md](DRAFT_FEATURE.md)** - Draft management guide
- **[NEW_FEATURES.md](NEW_FEATURES.md)** - Custom themes & enhanced metrics guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture & flow
- **[FINAL_SUMMARY.md](FINAL_SUMMARY.md)** - Complete implementation summary

## Development

### File Structure
```
Auto-TRM-Generator/
├── app.py                        # Main bot application
├── confluence_integration.py     # Confluence page creation
├── jira_integration.py           # Jira ticket fetching (NEW!)
├── requirements.txt              # Python dependencies
├── env.example                   # Environment variable template
├── test_bot.py                   # Test suite
├── test_draft.py                 # Draft feature tests
├── drafts/                       # Draft storage (user_id.json)
├── SETUP.md                      # Setup guide
├── CONFLUENCE_SETUP.md           # Confluence setup
├── JIRA_INTEGRATION.md           # Jira integration guide (NEW!)
├── DRAFT_FEATURE.md              # Draft management guide
├── NEW_FEATURES.md               # Latest features
├── ARCHITECTURE.md               # System architecture
├── FINAL_SUMMARY.md              # Complete summary
└── venv/                         # Virtual environment
```

### Key Functions

**app.py:**
- `fetch_slack_messages()` - Fetches messages from Slack with pagination
- `parse_date_range()` - Parses date input into timestamps
- `summarize_with_portkey()` - Generates TRM report via AI (for `/trm`)
- `handle_trm_command()` - `/trm` command handler
- `handle_trm_manual_command()` - `/trm-manual` command handler with draft detection
- `save_draft()` - Save current session to file (NEW!)
- `load_draft()` - Load draft from file (NEW!)
- `delete_draft()` - Delete draft file (NEW!)
- `has_draft()` - Check if draft exists (NEW!)
- `handle_add_issue_button()` - Add issue with custom theme + auto-save
- `handle_add_metric_button()` - Add metric with week-over-week data + auto-save
- `handle_save_draft_button()` - Manual save draft handler (NEW!)
- `handle_clear_draft_button()` - Clear draft handler (NEW!)
- `handle_trm_category_selection_modal_submission()` - Final report generation + draft cleanup

**confluence_integration.py:**
- `create_trm_page()` - Creates Confluence page via REST API (with ticket data)
- `_build_confluence_content()` - Builds HTML content with tables and TOC
- `_build_ticket_section()` - Builds Jira ticket section (NEW!)

**jira_integration.py:** (NEW!)
- `fetch_tickets()` - Fetches tickets from Jira for date range
- `_process_tickets()` - Categorizes tickets by status/priority/type
- `_empty_result()` - Returns empty structure when no tickets found

## Support

1. Check documentation in this repo
2. Review Slack bot logs (`python app.py` output)
3. Check Portkey AI dashboard for API issues
4. Verify Slack app configuration
5. Check Confluence page permissions

## License

Internal tool for Swiggy DevOps team.

---

**Version:** 4.1  
**Last Updated:** March 6, 2026  
**Default AI Model:** Claude Sonnet 4.5 (`pilot-poc/claude-sonnet-4-5`)  
**Output:** Confluence Pages with Table of Contents  
**New:** Draft Management with Auto-Save + Jira Ticket Integration