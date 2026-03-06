# /trm-manual Command Guide

**Date:** March 6, 2026  
**Status:** ✅ Complete

## Overview

The `/trm-manual` command allows you to manually create TRM reports by filling out a form with all the necessary data. This is useful when you want to create a report with custom information or when you don't want to rely on automatic message parsing from Slack.

## How to Use

### Step 1: Open the Manual Entry Modal
Type `/trm-manual` in any Slack channel

### Step 2: Fill Out the Form
A modal will appear with the following fields:

#### Required Fields ⚠️
1. **Week Number** - e.g., `10` (auto-filled with current week)
2. **Date Range** - e.g., `Mar 2 to Mar 8` (auto-filled with current week)
3. **DevOps Oncall** - e.g., `John Doe`

#### Optional Fields
4. **Issues (by theme)** - Format: `Theme: Description` (one per line)
5. **P0 Metrics** - Format: `P1 Alerts: 5, Infrasec P0: 2, S1 RCAs: 1, S2/S3 RCAs: 3`
6. **Alerts Summary** - Format: `Component | Alert | Frequency | Description`
7. **Cost Highlights** - Format: `WAF: $100 → $120`
8. **Outages Summary** - Format: `Outage | Severity | Reason | Owner | Date`
9. **Ticket Data** - Format: `Total: 25, Closed: 15, Blocked: 3, Open: 7`
10. **Action Items** - Format: `Description | Owner | ETA`

### Step 3: Submit
Click **Post TRM Report** button

### Step 4: View Report
The bot will post the formatted TRM report to your DM

## Input Format Examples

### Issues (by theme)
```
Compute: High CPU usage on prod servers
Infrasec: SSL certificate expiring soon
Haproxy: Load balancer configuration updated
Latency: API response time increased
Alerting: New alert rules deployed
Logging: Log retention policy updated
```

### P0 Metrics
```
P1 Alerts: 8, Infrasec P0: 3, S1 RCAs: 2, S2/S3 RCAs: 5
```

### Alerts Summary
Option 1 - Pipe-separated:
```
API Gateway | High Error Rate | 15 times/hour | 5xx errors increased
Database | Connection Pool Exhausted | 3 times/day | Max connections reached
```

Option 2 - Plain text (auto-formatted):
```
High CPU alerts on production servers
Memory usage exceeded threshold
```

### Cost Highlights
```
WAF: $1200 → $1350
CloudFront: $800 → $750
RDS: $2500 → $2600
```

### Outages Summary
Option 1 - Pipe-separated:
```
Payment Service | S1 | Database connection timeout | Alice | Mar 5
Search API | S2 | Memory leak | Bob | Mar 6
```

Option 2 - Plain text (auto-formatted):
```
Payment service outage due to database issues
Search API degraded performance
```

### Ticket Data
```
Total: 45, Closed: 28, Blocked: 5, Open: 12
```

Or:
```
- Total Tickets: 45
- Date Range: Mar 2 to Mar 8
- Status: Closed: 28 | Blocked: 5 | Open: 12
```

### Action Items
Option 1 - Pipe-separated:
```
Upgrade Redis cluster | DevOps Team | Mar 15
Review alert thresholds | SRE Team | Mar 20
Update runbooks | Documentation Team | Mar 25
```

Option 2 - Comma-separated:
```
Upgrade Redis cluster, DevOps Team, Mar 15
Review alert thresholds, SRE Team, Mar 20
```

## Output Format

The bot will generate a formatted TRM report like this:

```
📋 ProdEngg TRM — Week 10 | Mar 2 to Mar 8
DevOps Oncall: John Doe
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 Issues (from #devops-help)
| Theme/Vertical | Description |
|---|---|
| Compute | High CPU usage on prod servers |
| Infrasec | SSL certificate expiring soon |
| Haproxy | Load balancer configuration updated |
| Latency | API response time increased |
| Alerting | New alert rules deployed |
| Logging | Log retention policy updated |

📊 P0 Metrics
| # | Metric | Value |
|---|---|---|
| 1 | P1 Alerts | 8 |
| 2 | Infra sec P0 | 3 |
| 3 | S1 RCAs | 2 |
| 4 | S2/S3 RCAs | 5 |

🚨 Alerts Summary
| Component | Alert | Frequency | Description |
|---|---|---|---|
| API Gateway | High Error Rate | 15 times/hour | 5xx errors increased |
| Database | Connection Pool Exhausted | 3 times/day | Max connections reached |

💰 Cost Highlights
| Resource | Last Week | This Week |
|---|---|---|
| WAF | $1200 | $1350 |
| CloudFront | $800 | $750 |
| RDS | $2500 | $2600 |

🔥 Outages Summary
| Outage/RCA | Severity | Reason | Owner | Date |
|---|---|---|---|---|
| Payment Service | S1 | Database connection timeout | Alice | Mar 5 |
| Search API | S2 | Memory leak | Bob | Mar 6 |

🎫 Ticket Data
Total: 45, Closed: 28, Blocked: 5, Open: 12

✅ Action Items (TRM AIs)
| Description | Owner | ETA |
|---|---|---|
| Upgrade Redis cluster | DevOps Team | Mar 15 |
| Review alert thresholds | SRE Team | Mar 20 |
| Update runbooks | Documentation Team | Mar 25 |
```

## Comparison: /trm vs /trm-manual

| Feature | /trm (Automatic) | /trm-manual (Manual) |
|---------|-----------------|---------------------|
| **Data Source** | Slack #devops-help messages | Manual user input |
| **Date Selection** | Calendar date pickers | Text input (pre-filled) |
| **AI Processing** | Yes - Portkey AI analyzes messages | No - Direct formatting |
| **Time Required** | 30-60 seconds (AI processing) | Instant (no AI) |
| **Customization** | Limited to AI interpretation | Full control over content |
| **Best For** | Weekly automated reports | Custom/edited reports |
| **Message Count** | Shows message count analyzed | N/A |
| **Oncall Detection** | Auto-detected from messages | Manual entry required |

## When to Use /trm-manual

✅ **Use /trm-manual when:**
- You want full control over report content
- You need to add information not in Slack messages
- You want to create a report for a future week
- You need to correct/edit AI-generated content
- You're creating a template or example report
- The automatic report missed important details
- You don't have access to #devops-help channel

❌ **Use /trm (automatic) when:**
- You want to analyze actual Slack conversation
- You want AI to summarize and categorize issues
- You trust AI to extract relevant information
- You want message count statistics
- You have access to #devops-help channel

## Tips & Best Practices

### 1. Use Consistent Formatting
Stick to the suggested formats for easier parsing and cleaner output.

### 2. Pre-fill Week Data
The modal auto-fills the current week number and date range - adjust if needed for past/future weeks.

### 3. Use Pipe Separators for Tables
For complex tables (Alerts, Outages, Action Items), use pipe `|` separators for better formatting.

### 4. Leave Optional Fields Empty
If a section doesn't apply (e.g., no outages), leave it empty - the bot will show "No outages reported".

### 5. Copy from Previous Reports
Use a previous week's report as a template and modify the values.

### 6. Combine with /trm
1. Run `/trm` to get AI-generated report
2. Copy relevant sections
3. Use `/trm-manual` to customize and repost

## Error Handling

### Validation Errors

**Missing Required Fields:**
```
❌ Please provide Week Number, Date Range, and DevOps Oncall.
```
**Solution:** Fill in all three required fields before submitting.

### Formatting Issues

**Issue:** Tables not aligned properly  
**Solution:** Use consistent pipe `|` separators or stick to plain text.

**Issue:** Multiple themes in one line  
**Solution:** Put each theme on a separate line:
```
Compute: Issue 1
Infrasec: Issue 2
```

## Keyboard Shortcuts

While in the modal:
- **Tab** - Move to next field
- **Shift + Tab** - Move to previous field
- **Enter** (in single-line fields) - Move to next field
- **Cmd/Ctrl + Enter** - Submit form

## Example: Quick Weekly Report

Minimal input for a quick report:

**Week Number:** `10`  
**Date Range:** `Mar 2 to Mar 8`  
**DevOps Oncall:** `Alice`  
**Issues:** 
```
Compute: Minor CPU spikes resolved
Infrasec: All systems secure
```
**P0 Metrics:** `P1 Alerts: 2, Infrasec P0: 0, S1 RCAs: 0, S2/S3 RCAs: 1`  
**Ticket Data:** `Total: 15, Closed: 12, Blocked: 1, Open: 2`

Leave all other fields empty → Submit → Clean, concise report!

## Troubleshooting

### Modal doesn't open
- Check bot is running
- Verify `/trm-manual` command is registered in Slack
- Try `/trm` to see if bot responds at all

### Report formatting looks wrong
- Check for special characters in your input
- Verify pipe separators are used correctly
- Try simpler formatting without pipes

### Bot doesn't respond after submission
- Check bot logs for errors
- Verify bot has permission to send DMs
- Try with minimal input first

## Integration with Slack

### Posting to Channel
Currently, `/trm-manual` posts to your DM. To share with team:
1. Generate report with `/trm-manual`
2. Copy the bot's message
3. Paste in your team channel

### Future Enhancement Ideas
- Option to post directly to a channel
- Save templates for recurring reports
- Import previous week's report for editing
- Export report to different formats

---

*Last updated: March 6, 2026*
