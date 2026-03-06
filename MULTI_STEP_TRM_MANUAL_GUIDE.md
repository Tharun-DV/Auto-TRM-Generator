# Multi-Step TRM Manual Entry Guide

**Date:** March 6, 2026  
**Status:** ✅ Implemented  
**Feature:** Category-Based Multi-Step Modal Flow

## Overview

The `/trm-manual` command now uses a **multi-step modal flow** that allows you to add multiple entries for each category (Issues, Alerts, Outages, etc.) through an interactive interface.

## How It Works

### Step 1: Basic Setup
When you type `/trm-manual`, you'll see a setup modal asking for:
- **Week Number** (auto-filled)
- **Date Range** (auto-filled)
- **DevOps Oncall** (required)

### Step 2: Category Selection
After submitting the setup, you'll see a screen with buttons to add entries:

#### Available Categories:
- **➕ Add Issue** - Add issues by theme (Compute, Latency, Infrasec, etc.)
- **📊 Add Metric** - Set P0 metrics (P1 Alerts, Infrasec P0, RCAs)
- **🚨 Add Alert** - Add alerts with component, frequency, description
- **💰 Add Cost** - Add cost entries (resource, last week, this week)
- **🔥 Add Outage** - Add outages with severity, reason, owner, date
- **✅ Add Action Item** - Add action items with description, owner, ETA

#### Summary Display:
The modal shows a live count of entries you've added:
```
Current Entries:
• Issues: 3
• Alerts: 2
• Outages: 1
• Action Items: 2
```

### Step 3: Add Entries Per Category

#### Adding an Issue:
1. Click "➕ Add Issue"
2. Select **Theme** from dropdown:
   - Compute
   - Infrasec
   - Haproxy
   - Latency
   - Alerting
   - Logging
3. Enter **Description**
4. Click "Add Issue"
5. Returns to category selection (you can add more!)

#### Adding an Alert:
1. Click "🚨 Add Alert"
2. Enter:
   - **Component** (e.g., "API Gateway")
   - **Alert Name** (e.g., "High Error Rate")
   - **Frequency** (e.g., "15 times/hour")
   - **Description**
3. Click "Add Alert"
4. Returns to category selection

#### Adding an Outage:
1. Click "🔥 Add Outage"
2. Enter:
   - **Outage/RCA Name**
   - **Severity** (dropdown: S1, S2, S3)
   - **Reason**
   - **Owner**
   - **Date** (date picker)
3. Click "Add Outage"
4. Returns to category selection

#### Adding a Cost Entry:
1. Click "💰 Add Cost"
2. Enter:
   - **Resource** (e.g., "WAF", "CloudFront")
   - **Last Week Cost** (e.g., "$1200")
   - **This Week Cost** (e.g., "$1350")
3. Click "Add Cost"
4. Returns to category selection

#### Adding an Action Item:
1. Click "✅ Add Action Item"
2. Enter:
   - **Description**
   - **Owner**
   - **ETA**
3. Click "Add Action Item"
4. Returns to category selection

#### Adding Metrics:
1. Click "📊 Add Metric"
2. Enter all metrics:
   - **P1 Alerts** count
   - **Infrasec P0** count
   - **S1 RCAs** count
   - **S2/S3 RCAs** count
3. Click "Add Metric"
4. Returns to category selection

**Note:** Metrics can only have one set of values (they replace previous values).

### Step 4: Generate Report
Once you've added all your entries, click **"Finish & Generate"** to post the TRM report.

## Example Flow

### Scenario: Weekly TRM Report

1. **Start:** Type `/trm-manual` in Slack
2. **Setup:**
   - Week Number: `10`
   - Date Range: `Mar 2 to Mar 8`
   - DevOps Oncall: `Alice`
   - Click "Continue"

3. **Add Issues:**
   - Click "➕ Add Issue" → Theme: `Compute` → Description: `High CPU on prod servers` → Submit
   - Click "➕ Add Issue" → Theme: `Latency` → Description: `API response time increased` → Submit
   - Click "➕ Add Issue" → Theme: `Compute` → Description: `Memory leak in service X` → Submit

4. **Add Alerts:**
   - Click "🚨 Add Alert" → Component: `API Gateway` → Alert: `High Error Rate` → Frequency: `15 times/hour` → Description: `5xx errors increased` → Submit
   - Click "🚨 Add Alert" → Component: `Database` → Alert: `Connection Pool` → Frequency: `3 times/day` → Description: `Max connections reached` → Submit

5. **Add Outage:**
   - Click "🔥 Add Outage" → Name: `Payment Service` → Severity: `S1` → Reason: `Database timeout` → Owner: `Bob` → Date: `Mar 5` → Submit

6. **Add Metrics:**
   - Click "📊 Add Metric" → P1: `8` → Infrasec P0: `3` → S1 RCAs: `2` → S2/S3 RCAs: `5` → Submit

7. **Add Cost:**
   - Click "💰 Add Cost" → Resource: `WAF` → Last Week: `$1200` → This Week: `$1350` → Submit

8. **Add Action Items:**
   - Click "✅ Add Action Item" → Description: `Upgrade Redis cluster` → Owner: `DevOps Team` → ETA: `Mar 15` → Submit
   - Click "✅ Add Action Item" → Description: `Review alert thresholds` → Owner: `SRE Team` → ETA: `Mar 20` → Submit

9. **Generate:** Click "Finish & Generate"

### Generated Report:

```
📋 ProdEngg TRM — Week 10 | Mar 2 to Mar 8
DevOps Oncall: Alice
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 Issues (from #devops-help)
| Theme/Vertical | Description |
|---|---|
| Compute | High CPU on prod servers; Memory leak in service X |
| Infrasec | None |
| Haproxy | None |
| Latency | API response time increased |
| Alerting | None |
| Logging | None |

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
| Database | Connection Pool | 3 times/day | Max connections reached |

💰 Cost Highlights
| Resource | Last Week | This Week |
|---|---|---|
| WAF | $1200 | $1350 |

🔥 Outages Summary
| Outage/RCA | Severity | Reason | Owner | Date |
|---|---|---|---|---|
| Payment Service | S1 | Database timeout | Bob | Mar 5 |

🎫 Ticket Data
- Total Tickets: Not specified
- Date Range: Mar 2 to Mar 8
- Status: Closed: 0 | Blocked: 0 | Open: 0

✅ Action Items (TRM AIs)
| Description | Owner | ETA |
|---|---|---|
| Upgrade Redis cluster | DevOps Team | Mar 15 |
| Review alert thresholds | SRE Team | Mar 20 |
```

## Key Features

### ✅ Multiple Entries Per Category
- Add **multiple issues** for different themes (Compute, Latency, etc.)
- Add **multiple alerts** with different components
- Add **multiple outages** for the week
- Add **multiple cost entries** for different resources
- Add **multiple action items**

### ✅ Structured Input
- **Dropdowns** for predefined options (Theme, Severity)
- **Date pickers** for dates (Outage dates)
- **Multi-line text** for descriptions
- **Validation** at each step

### ✅ Real-Time Summary
- See count of entries as you add them
- Clear feedback after each addition ("✅ Added Compute issue!")

### ✅ Flexible Workflow
- Add categories in any order
- Skip categories you don't need
- No minimum required entries

## Technical Implementation

### Session Management
- Uses in-memory `trm_session_data` dictionary
- Stores data per user ID
- Cleans up after report generation

### Modal Stack
The flow uses Slack's modal view stack:
1. **trm_setup_modal** → Initial setup
2. **trm_category_selection_modal** → Central hub (push)
3. **add_issue_modal**, **add_alert_modal**, etc. → Sub-modals (push)
4. Return to category selection modal (update)
5. **trm_category_selection_modal** → Final submission

### Handlers Implemented
```python
# Command handler
@app.command("/trm-manual")

# View submission handlers
@app.view("trm_setup_modal")
@app.view("trm_category_selection_modal")
@app.view("add_issue_modal")
@app.view("add_alert_modal")
@app.view("add_outage_modal")
@app.view("add_cost_modal")
@app.view("add_action_item_modal")
@app.view("add_metric_modal")

# Action handlers (buttons)
@app.action("add_issue_button")
@app.action("add_alert_button")
@app.action("add_outage_button")
@app.action("add_cost_button")
@app.action("add_action_item_button")
@app.action("add_metric_button")

# Helper functions
_generate_summary_text(user_id)
_build_category_selection_view(user_id, message)
```

## Advantages Over Old Single-Form Approach

| Feature | Old (Single Form) | New (Multi-Step) |
|---------|------------------|------------------|
| **Multiple entries per category** | ❌ No | ✅ Yes |
| **Structured input** | Text-only | Dropdowns, date pickers, structured fields |
| **Entry validation** | After submission | Per entry |
| **Flexibility** | Fill all fields upfront | Add entries as needed |
| **User experience** | Overwhelming form | Guided step-by-step |
| **Data quality** | Free-form text | Structured data |

## Troubleshooting

### Modal doesn't open
- Check bot is running
- Verify `/trm-manual` command is registered

### Session lost error
- Don't close/cancel the modal and restart
- Complete the flow in one session
- Session data is cleared after successful submission

### Entries not appearing
- Check you clicked the appropriate "Add" button
- Verify you see the success message ("✅ Added...")
- Check the "Current Entries" summary

## Future Enhancements

Potential improvements:
- [ ] Edit/delete existing entries
- [ ] Preview report before submitting
- [ ] Save drafts
- [ ] Template management
- [ ] Import from previous week
- [ ] Ticket data input fields

---

**Last Updated:** March 6, 2026  
**Version:** 3.0 (Multi-Step Flow)
