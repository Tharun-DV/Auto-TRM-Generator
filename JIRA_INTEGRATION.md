# Jira Integration for TRM Reports

**Date:** March 6, 2026  
**Status:** ✅ Implemented  
**Version:** 4.1

---

## Overview

The TRM bot now automatically fetches tickets from Jira during the report's time period and includes them directly in the Confluence TRM report. This provides a comprehensive view of all work items during the TRM week.

---

## Features

### 🎫 Automatic Ticket Fetching
- Fetches tickets from specified Jira projects
- Filters by TRM date range (created OR updated during the period)
- Supports Jira Cloud (atlassian.net)

### 📊 Comprehensive Statistics
- **Total ticket count**
- **By Status** (Open, In Progress, Closed, etc.)
- **By Priority** (P1, P2, P3, etc.)
- **By Type** (Bug, Task, Story, Epic, etc.)

### 📋 Detailed Ticket List
- Shows top 50 tickets with clickable Jira links
- Includes: Key, Summary, Status, Priority, Type, Assignee
- Indicates if more tickets exist beyond the displayed 50

### 🔗 Embedded in TRM Report
- Tickets appear in "Ticket Data" section
- Part of the main TRM Confluence page
- Automatically included with table of contents

---

## Setup

### 1. Get Jira API Token

**Jira Cloud:**
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name (e.g., "TRM Bot")
4. Copy the token (save it securely!)

### 2. Set Environment Variables

Add to your `.env` file:

```bash
# Jira Integration (Optional)
JIRA_URL=https://your-company.atlassian.net
JIRA_USER=your.email@company.com
JIRA_API_TOKEN=your-jira-api-token-here
JIRA_PROJECT_KEYS=DEVOPS,INFRA,SRE  # Comma-separated project keys
```

**Required:**
- `JIRA_URL` - Your Jira instance URL (without /wiki or trailing slash)
- `JIRA_USER` - Your Jira email address
- `JIRA_API_TOKEN` - API token from step 1
- `JIRA_PROJECT_KEYS` - Comma-separated list of project keys to search

### 3. Test Configuration

```bash
# Start the bot
python app.py

# Look for this message in logs:
# ✅ Jira integration configured
#  OR
# ⚠️ Jira integration not configured
```

---

## Usage

### Automatic Integration

Once configured, Jira tickets are automatically included when you generate a TRM report:

```
1. Run /trm-manual
2. Fill in setup (week, dates, oncall)
3. Add entries as normal
4. Click "Finish & Generate"
   ↓
🎫 Fetching tickets from 2026-03-02 to 2026-03-08
✅ Fetched 45 tickets from Jira
📄 Confluence page created with tickets!
```

### What Gets Fetched

**JQL Query Used:**
```jql
(project = DEVOPS OR project = INFRA OR project = SRE) 
AND (created >= '2026-03-02' OR updated >= '2026-03-02') 
AND (created <= '2026-03-08' OR updated <= '2026-03-08')
```

**Includes tickets that were:**
- Created during the TRM period, OR
- Updated during the TRM period

This ensures you capture both new tickets and active work on existing tickets.

---

## Confluence Output

### Ticket Data Section

**Summary:**
```
Ticket Data
===========
• Total Tickets: 45
• Date Range: Mar 2 to Mar 8
• By Status: Open: 12 | In Progress: 15 | Closed: 18
• By Priority: P1: 3 | P2: 15 | P3: 27
• By Type: Bug: 18 | Task: 20 | Story: 7

Ticket Details (Top 50)
-----------------------
| Key      | Summary                    | Status      | Priority | Type | Assignee    |
|----------|----------------------------|-------------|----------|------|-------------|
| DEV-123  | Fix login timeout issue... | Closed      | P1       | Bug  | John Doe    |
| DEV-124  | Update API documentation.. | In Progress | P2       | Task | Jane Smith  |
| ...      | ...                        | ...         | ...      | ...  | ...         |
```

**Features:**
- ✅ Ticket keys are clickable links to Jira
- ✅ Summaries truncated to 80 characters for readability
- ✅ Shows top 50 tickets
- ✅ Indicates if more tickets exist

---

## Examples

### Example 1: Small Number of Tickets

**Input:** 8 tickets during the week

**Output:**
```
Ticket Data
• Total Tickets: 8
• Date Range: Mar 2 to Mar 8
• By Status: Open: 3 | Closed: 5
• By Priority: P1: 1 | P2: 4 | P3: 3
• By Type: Bug: 3 | Task: 5

Ticket Details (Top 50)
[All 8 tickets displayed in table]
```

### Example 2: Large Number of Tickets

**Input:** 127 tickets during the week

**Output:**
```
Ticket Data
• Total Tickets: 127
• Date Range: Mar 2 to Mar 8
• By Status: Open: 45 | In Progress: 32 | Closed: 50
• By Priority: P1: 5 | P2: 42 | P3: 80
• By Type: Bug: 38 | Task: 65 | Story: 24

Ticket Details (Top 50)
[First 50 tickets displayed]
... and 77 more tickets
```

### Example 3: No Tickets Found

**Input:** 0 tickets

**Output:**
```
Ticket Data
• Total Tickets: 0
• Date Range: Mar 2 to Mar 8
• Status: No tickets found
```

---

## Project Keys Configuration

### Multiple Projects

To fetch from multiple projects, use comma-separated list:

```bash
JIRA_PROJECT_KEYS=DEVOPS,INFRA,SRE,PLATFORM
```

This will search:
- `project = DEVOPS`
- `project = INFRA`
- `project = SRE`
- `project = PLATFORM`

### Single Project

```bash
JIRA_PROJECT_KEYS=DEVOPS
```

### Finding Your Project Keys

1. Go to your Jira instance
2. Navigate to a project
3. Look at the URL: `https://company.atlassian.net/browse/DEVOPS-123`
4. The project key is `DEVOPS` (before the dash)

---

## Troubleshooting

### No Tickets Showing

**Check 1: Configuration**
```bash
# Make sure all 4 variables are set:
echo $JIRA_URL
echo $JIRA_USER
echo $JIRA_API_TOKEN
echo $JIRA_PROJECT_KEYS
```

**Check 2: Bot Logs**
Look for these messages:
```
✅ Jira integration configured  # Good!
⚠️ Jira integration not configured  # Need to set variables
```

**Check 3: Project Keys**
- Verify project keys are correct (case-sensitive)
- Check you have access to these projects in Jira

**Check 4: Date Range**
- Tickets must be created OR updated during TRM period
- Check the date range in your TRM setup

### API Authentication Errors

**Error:** `401 Unauthorized`

**Solution:**
1. Verify `JIRA_USER` is your correct email
2. Regenerate API token if needed
3. Check token has not expired

**Error:** `403 Forbidden`

**Solution:**
- Your Jira user needs read access to the projects
- Contact Jira admin to grant project access

### Connection Errors

**Error:** `Connection timeout`

**Solution:**
1. Check JIRA_URL is correct (no /wiki, no trailing slash)
2. Verify network connectivity to Jira
3. Check if behind corporate proxy

**Error:** `SSL verification failed`

**Solution:**
Set `DISABLE_SSL_VERIFY=1` if behind corporate proxy (not recommended for production)

---

## Technical Details

### API Endpoints Used

**Jira Search API:**
```
GET /rest/api/3/search
```

**Parameters:**
- `jql` - JQL query for ticket search
- `maxResults` - Maximum 1000 tickets
- `fields` - Specific fields to return

### Fields Fetched

- `key` - Ticket key (e.g., DEV-123)
- `summary` - Ticket title
- `status` - Current status
- `priority` - Priority level
- `issuetype` - Type (Bug, Task, etc.)
- `created` - Creation date
- `updated` - Last update date
- `assignee` - Assigned user
- `reporter` - Reporter user

### Data Structure

```python
{
    "total": 45,
    "by_status": {
        "Open": 12,
        "In Progress": 15,
        "Closed": 18
    },
    "by_priority": {
        "P1": 3,
        "P2": 15,
        "P3": 27
    },
    "by_type": {
        "Bug": 18,
        "Task": 20,
        "Story": 7
    },
    "tickets": [
        {
            "key": "DEV-123",
            "summary": "Fix login timeout",
            "status": "Closed",
            "priority": "P1",
            "type": "Bug",
            "assignee": "John Doe",
            "created": "2026-03-03T10:00:00Z",
            "updated": "2026-03-05T15:30:00Z"
        },
        ...
    ]
}
```

---

## Files Modified/Created

### New Files
- ✨ `jira_integration.py` - Jira API integration module
- ✨ `JIRA_INTEGRATION.md` - This documentation

### Modified Files
- ✏️ `app.py` - Import jira module, fetch tickets before creating report
- ✏️ `confluence_integration.py` - Accept ticket_data parameter, build ticket section
- ✏️ `env.example` - Added Jira configuration variables

---

## Security Considerations

### API Token Storage
- ✅ Store in `.env` file (not committed to git)
- ✅ Use environment variables
- ❌ Never hardcode in source code

### Permissions
- Use a service account if possible
- Grant minimum required permissions (read-only)
- Limit to specific projects

### Data Privacy
- Ticket data is transient (not stored permanently)
- Only included in Confluence pages
- Respects Jira permissions (users see what they have access to)

---

## Benefits

### For Users
✅ **Complete View** - See all tickets in one report  
✅ **No Manual Work** - Automatic fetching  
✅ **Up-to-Date** - Always current data  
✅ **Organized** - Categorized by status, priority, type

### For Teams
✅ **Better Insights** - See team workload at a glance  
✅ **Trend Analysis** - Compare weeks easily  
✅ **Accountability** - Track ticket completion  
✅ **Planning** - Data-driven decisions

---

## Optional: Disabling Jira Integration

To disable Jira integration (tickets won't be fetched):

**Option 1:** Don't set Jira environment variables

**Option 2:** Comment out variables in `.env`:
```bash
# JIRA_URL=https://your-company.atlassian.net
# JIRA_USER=your.email@company.com
# JIRA_API_TOKEN=your-jira-api-token-here
# JIRA_PROJECT_KEYS=DEVOPS,INFRA
```

The bot will work normally, just without ticket data.

---

## Future Enhancements

Potential improvements for future versions:

1. **Custom JQL** - Allow custom JQL queries via env var
2. **Ticket Filters** - Filter by specific criteria
3. **Charts** - Add visual charts for ticket data
4. **Separate Page** - Option to create separate "TRM AI Tickets" page
5. **Slack Preview** - Show ticket summary in Slack before Confluence
6. **Historical Comparison** - Compare with previous weeks

---

## Summary

Jira integration is now fully functional and will automatically include ticket data in your TRM reports. Configure the environment variables, and tickets will appear in the "Ticket Data" section of your Confluence pages.

**Status:** ✅ Ready for Production  
**Last Updated:** March 6, 2026
