# Fixes Applied & Testing Guide

**Date:** March 6, 2026  
**Status:** ✅ Fixed - Ready for Testing

## Issues Encountered & Fixes Applied

### Issue 1: Slack Modal Stack Limit ❌ → ✅ FIXED

**Error:**
```
SlackApiError: push_limit_reached
```

**Cause:**
Slack only allows **2 modals** in the stack at once:
1. Setup Modal
2. Category Selection Modal
3. ❌ **Can't push a 3rd modal** (add_issue, add_alert, etc.)

**Fix Applied:**
Changed from `views.push()` to `views.update()` in all button handlers:

```python
# ❌ BEFORE (caused error)
client.views_push(
    trigger_id=body["trigger_id"],
    view={...}
)

# ✅ AFTER (works!)
client.views_update(
    view_id=body["view"]["id"],
    view={...}
)
```

**Updated Handlers:**
- ✅ `handle_add_issue_button`
- ✅ `handle_add_alert_button`
- ✅ `handle_add_outage_button`
- ✅ `handle_add_cost_button`
- ✅ `handle_add_action_item_button`
- ✅ `handle_add_metric_button`

---

### Issue 2: Portkey API Rate Limit ⚠️

**Error:**
```
429 Portkey Error: apikey 2e********rpm rate limit exceeded. Error Code: 05
```

**Cause:**
Your Portkey API key has hit its rate limit (requests per minute).

**Solutions:**

#### Option A: Wait and Retry
The rate limit typically resets after 1 minute. Wait 60 seconds and try again.

#### Option B: Use a Different API Key
If you have multiple Portkey API keys:
```bash
export PORTKEY_API_KEY='your-other-api-key'
```

#### Option C: Upgrade Portkey Plan
Contact Portkey to upgrade your plan for higher rate limits.

#### Option D: Test Without AI Generation
You can test the `/trm-manual` flow without hitting the API limit since **manual entry doesn't use Portkey AI**.

**The `/trm-manual` command does NOT call Portkey API** - it only uses structured forms!

---

## New Modal Flow (After Fix)

### How It Works Now:

```
/trm-manual
    ↓
[Modal 1: Setup]
  Week: 10
  Date Range: Mar 2-8
  Oncall: Alice
  → Click "Continue"
    ↓
[Modal 2: Category Selection] ← REPLACES Modal 1
  ➕ Add Issue  📊 Add Metric  🚨 Add Alert
  💰 Add Cost  🔥 Add Outage  ✅ Add Action Item
  → Click "Add Issue"
    ↓
[Modal 2: Add Issue Form] ← UPDATES Modal 2 (not pushing new!)
  Theme: [Dropdown]
  Description: [Text]
  → Click "Add Issue"
    ↓
[Modal 2: Category Selection] ← UPDATES back
  ✅ Added Compute issue!
  Current Entries: • Issues: 1
  → Click "Add Issue" again or other buttons
    ↓
[Repeat adding entries...]
    ↓
[Modal 2: Category Selection]
  → Click "Finish & Generate"
    ↓
TRM Report Posted! ✅
```

**Key Change:** We now **update** the same modal instead of **pushing** new ones onto the stack.

---

## Testing Guide

### Test 1: Basic Flow (No API Calls)

1. **Start the bot:**
   ```bash
   python app.py
   ```

2. **In Slack, type:** `/trm-manual`

3. **Fill in setup:**
   - Week Number: `10`
   - Date Range: `Mar 2 to Mar 8`
   - DevOps Oncall: `Your Name`
   - Click **"Continue"**

4. **Add an issue:**
   - Click **"➕ Add Issue"**
   - Select Theme: **Compute**
   - Enter Description: `Test issue for compute`
   - Click **"Add Issue"**

5. **Verify:**
   - ✅ Should see: "✅ Added Compute issue!"
   - ✅ Should see: "Current Entries: • Issues: 1"
   - ✅ Should be back at category selection

6. **Add another issue:**
   - Click **"➕ Add Issue"** again
   - Select Theme: **Latency**
   - Enter Description: `Test latency issue`
   - Click **"Add Issue"**

7. **Verify:**
   - ✅ Should see: "✅ Added Latency issue!"
   - ✅ Should see: "Current Entries: • Issues: 2"

8. **Add an alert:**
   - Click **"🚨 Add Alert"**
   - Component: `API Gateway`
   - Alert Name: `High Error Rate`
   - Frequency: `10/min`
   - Description: `Test alert`
   - Click **"Add Alert"**

9. **Verify:**
   - ✅ Should see: "✅ Added alert: High Error Rate"
   - ✅ Should see: "Current Entries: • Issues: 2 • Alerts: 1"

10. **Generate report:**
    - Click **"Finish & Generate"**
    - ✅ Should receive TRM report in DM!

### Expected Report Output:

```
📋 ProdEngg TRM — Week 10 | Mar 2 to Mar 8
DevOps Oncall: Your Name
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 Issues (from #devops-help)
| Theme/Vertical | Description |
|---|---|
| Compute | Test issue for compute |
| Infrasec | None |
| Haproxy | None |
| Latency | Test latency issue |
| Alerting | None |
| Logging | None |

📊 P0 Metrics
| # | Metric | Value |
|---|---|---|
| 1 | P1 Alerts | 0 |
| 2 | Infra sec P0 | 0 |
| 3 | S1 RCAs | 0 |
| 4 | S2/S3 RCAs | 0 |

🚨 Alerts Summary
| Component | Alert | Frequency | Description |
|---|---|---|---|
| API Gateway | High Error Rate | 10/min | Test alert |

💰 Cost Highlights
| Resource | Last Week | This Week |
|---|---|---|
No cost data mentioned

🔥 Outages Summary
| Outage/RCA | Severity | Reason | Owner | Date |
|---|---|---|---|---|
No outages reported

🎫 Ticket Data
- Total Tickets: Not specified
- Date Range: Mar 2 to Mar 8
- Status: Closed: 0 | Blocked: 0 | Open: 0

✅ Action Items (TRM AIs)
| Description | Owner | ETA |
|---|---|---|
No action items
```

---

## Test 2: Multiple Entries Per Category

1. **Add 3 Compute issues**
2. **Add 2 Latency issues**
3. **Add 2 Alerts**
4. **Add 1 Outage**
5. **Add 1 Cost entry**
6. **Add 2 Action items**

**Expected Result:**
All entries should be grouped and displayed in the report.

---

## Test 3: Click "Back" Button

1. Click **"➕ Add Issue"**
2. **Don't fill anything**
3. Click **"Back"** (close button)

**Expected:** Should return to category selection without adding anything.

**Current Limitation:** The "Back" button will close the modal entirely. We'd need to add a `view_closed` handler to properly handle this, but it's not critical for v1.

---

## Troubleshooting

### Error: `push_limit_reached`
- ✅ **Fixed!** We now use `views.update` instead of `views.push`

### Error: Portkey rate limit
- ⚠️ **Not applicable** to `/trm-manual` - it doesn't use AI!
- Only affects `/trm` (auto-generate from messages)

### Modal doesn't update
- Check bot is running
- Verify you clicked a button (not typed a command)
- Check logs for errors

### Entries not saving
- Verify you clicked the "Add" button in the sub-modal
- Check for success message ("✅ Added...")
- Look at "Current Entries" summary

### Report not generating
- Check you clicked "Finish & Generate"
- Verify at least basic info was entered
- Check bot logs

---

## What's Different from Original Design

| Aspect | Original Plan | Actual Implementation |
|--------|--------------|----------------------|
| **Modal stack** | Push 3 levels | Update 2 levels |
| **Navigation** | Push → Update → Pop | Update ⇄ Update |
| **Back button** | Returns to previous | Closes modal |
| **User experience** | Slightly smoother | Still very good! |

The change from **push/pop** to **update/update** doesn't affect the user experience significantly - it just means we're replacing the current modal instead of stacking them.

---

## Next Steps

1. **Test the bot** with the steps above
2. **Verify** all handlers work correctly
3. **Try** adding multiple entries per category
4. **Check** the generated report format
5. **Report** any issues you encounter

---

## Summary

✅ **Fixed:** Slack modal stack limit  
⚠️ **Note:** Portkey rate limit doesn't affect `/trm-manual`  
✅ **Status:** Ready for testing  
📝 **Action:** Run tests above and verify functionality

The implementation is complete and the modal stack limit is fixed. You can now test the `/trm-manual` command without encountering the `push_limit_reached` error!
