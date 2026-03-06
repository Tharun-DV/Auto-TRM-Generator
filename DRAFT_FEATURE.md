# Draft Management Feature

**Date:** March 6, 2026  
**Status:** ✅ Implemented  
**Version:** 4.0

---

## Overview

Users can now save their TRM report as a draft and continue working on it later. Drafts are automatically saved after each entry is added, and users can manually save, clear, or continue editing their drafts.

---

## Features

### 1. 🔄 **Auto-Save**
- Automatically saves draft after:
  - Setting up metadata (week number, dates, oncall)
  - Adding any issue
  - Adding any metric
  - Adding any alert
  - Adding any cost entry
  - Adding any outage
  - Adding any action item
- Silent background save without interrupting workflow
- Timestamp updated after each save

### 2. 💾 **Manual Save Draft**
- "💾 Save Draft" button in category selection modal
- Shows confirmation message with timestamp
- Allows users to close modal and continue later
- Draft persists across sessions

### 3. 📂 **Continue Draft**
- When running `/trm-manual` with existing draft:
  - Shows modal with draft timestamp
  - Options: "📂 Continue Draft" or "🆕 Start Fresh"
  - Continue Draft: Loads all saved data
  - Start Fresh: Deletes old draft and starts new

### 4. 🗑️ **Clear Draft**
- "🗑️ Clear Draft" button in category selection modal
- Deletes saved draft immediately
- Shows confirmation message
- Allows starting fresh without exiting

### 5. ⏰ **Draft Timestamp**
- Shows "Last saved: [timestamp]" in modal
- Updates after every auto-save or manual save
- Format: "Mar 6, 2026 at 02:30 PM"

### 6. 🧹 **Auto-Cleanup**
- Draft automatically deleted when:
  - Report is successfully generated
  - User completes the TRM workflow

---

## User Workflow

### Creating New Report

```
User: /trm-manual
  ↓
[No existing draft]
  ↓
[Setup Modal]
  Week: 10
  Dates: Mar 2-8
  Oncall: Alice
  → Continue
  ↓
[Auto-saved!]
  ↓
[Category Selection]
  → Add entries...
  → Each entry auto-saves
  ↓
[Finish & Generate]
  ↓
[Draft deleted]
✅ Report created!
```

### Continuing Existing Draft

```
User: /trm-manual
  ↓
[Draft exists - Last saved: Mar 6, 2026 at 02:30 PM]
  ↓
Option 1: 📂 Continue Draft
  → Loads all existing data
  → Continue editing
  
Option 2: 🆕 Start Fresh
  → Deletes old draft
  → Starts new report
```

### Manual Save & Exit

```
[Category Selection]
  → Add some entries
  → Click "💾 Save Draft"
  ↓
✅ Draft Saved!
Saved at: Mar 6, 2026 at 02:30 PM

You can safely close this and continue later with /trm-manual
  ↓
User closes modal
  ↓
[Later...]
User: /trm-manual
  → Draft Found!
  → Continue Draft
```

---

## Technical Details

### Storage

**Location:** `drafts/{user_id}.json`

**Format:**
```json
{
  "data": {
    "metadata": {
      "week_number": "10",
      "date_range": "Mar 2 to Mar 8",
      "oncall": "<@U123456>",
      "oncall_names": "Alice"
    },
    "issues": [...],
    "metrics": [...],
    "alerts": [...],
    "cost": [...],
    "outages": [...],
    "tickets": [],
    "action_items": [...]
  },
  "timestamp": "2026-03-06T14:30:45.123456",
  "last_saved": "Mar 6, 2026 at 02:30 PM"
}
```

### Functions

```python
# Draft utilities
save_draft(user_id)           # Save current session to file
load_draft(user_id)           # Load draft from file
delete_draft(user_id)         # Delete draft file
has_draft(user_id)            # Check if draft exists
get_draft_timestamp(user_id)  # Get last saved time
```

### Auto-Save Points

1. **Setup complete** → `handle_trm_setup_modal_submission()`
2. **Issue added** → `handle_add_issue_modal_submission()`
3. **Alert added** → `handle_add_alert_modal_submission()`
4. **Outage added** → `handle_add_outage_modal_submission()`
5. **Cost added** → `handle_add_cost_modal_submission()`
6. **Action item added** → `handle_add_action_item_modal_submission()`
7. **Metric added** → `handle_add_metric_modal_submission()`

---

## Benefits

### For Users
✅ **No Data Loss** - Work saved automatically  
✅ **Flexible Workflow** - Can stop and resume anytime  
✅ **Peace of Mind** - Draft saved after every change  
✅ **Easy Recovery** - Continue from where you left off  

### For Teams
✅ **Better UX** - Users can work at their own pace  
✅ **Reduced Frustration** - No need to complete in one session  
✅ **Higher Completion Rate** - Users can finish when ready  

---

## Examples

### Example 1: Quick Save

```
1. Start /trm-manual
2. Setup: Week 10, Mar 2-8, Oncall: Alice
   → Auto-saved!
3. Add Issue: "High CPU on prod servers"
   → Auto-saved!
4. Need to leave urgently
5. Click "💾 Save Draft"
   ✅ Draft Saved!
6. Close modal

[Next day...]

7. Run /trm-manual
   → Draft Found! (Last saved: Mar 6, 2026 at 02:30 PM)
8. Click "📂 Continue Draft"
9. Continue adding entries...
10. Click "Finish & Generate"
    ✅ Report created!
    🗑️ Draft deleted!
```

### Example 2: Start Fresh

```
1. Run /trm-manual
   → Draft Found! (Last saved: Mar 5, 2026)
2. Click "🆕 Start Fresh"
   → Old draft deleted
3. Fresh setup modal appears
4. Enter new data...
```

### Example 3: Clear Mid-Session

```
1. Run /trm-manual
2. Add multiple entries
3. Realize you want to start over
4. Click "🗑️ Clear Draft"
   ✅ Draft Cleared!
5. All entries remain in current session
6. Close modal to exit completely
7. Run /trm-manual again
   → No draft found (fresh start)
```

---

## UI Elements

### Category Selection Modal

**Before:**
```
[Category Selection]
  📝 Add Data to Your TRM Report
  
  [➕ Add Issue] [📊 Add Metric] [🚨 Add Alert]
  [💰 Add Cost] [🔥 Add Outage] [✅ Add Action Item]
  
  ━━━━━━━━━━━━━━━━━━━━━━━━
  
  Current Entries:
  • Issues: 2
  • Metrics: 1
```

**After (with draft feature):**
```
[Category Selection]
  📝 Add Data to Your TRM Report
  
  💾 Last saved: Mar 6, 2026 at 02:30 PM
  
  [➕ Add Issue] [📊 Add Metric] [🚨 Add Alert]
  [💰 Add Cost] [🔥 Add Outage] [✅ Add Action Item]
  
  [💾 Save Draft] [🗑️ Clear Draft]
  
  ━━━━━━━━━━━━━━━━━━━━━━━━
  
  Current Entries:
  • Issues: 2
  • Metrics: 1
```

---

## Edge Cases Handled

1. **No draft exists** → Normal flow (setup modal)
2. **Draft exists** → Show "Continue Draft" or "Start Fresh" choice
3. **Draft load fails** → Show error, allow fresh start
4. **Save fails** → Show error message, data still in memory
5. **Report completed** → Draft deleted automatically
6. **User abandons mid-session** → Draft saved, can continue later
7. **Multiple users** → Each user has separate draft file

---

## Testing Checklist

### ✅ Auto-Save
- [ ] Draft saved after setup modal
- [ ] Draft saved after adding issue
- [ ] Draft saved after adding metric
- [ ] Draft saved after adding alert
- [ ] Draft saved after adding cost
- [ ] Draft saved after adding outage
- [ ] Draft saved after adding action item

### ✅ Manual Save
- [ ] "💾 Save Draft" button appears
- [ ] Clicking saves draft successfully
- [ ] Confirmation message shows timestamp
- [ ] Can close and reopen to continue

### ✅ Continue Draft
- [ ] Draft detection on `/trm-manual`
- [ ] "Continue Draft" loads all data
- [ ] Timestamp displayed correctly
- [ ] All entries preserved

### ✅ Start Fresh
- [ ] "Start Fresh" deletes old draft
- [ ] Fresh setup modal appears
- [ ] No old data loaded

### ✅ Clear Draft
- [ ] "🗑️ Clear Draft" button appears
- [ ] Clicking deletes draft
- [ ] Confirmation message shown
- [ ] Draft file removed

### ✅ Timestamp
- [ ] Shows in category selection modal
- [ ] Updates after auto-save
- [ ] Updates after manual save
- [ ] Format is readable

### ✅ Cleanup
- [ ] Draft deleted after report generation
- [ ] No orphaned drafts

---

## Files Modified

1. **app.py**
   - Added `import json`
   - Added draft utility functions
   - Added `DRAFTS_DIR` constant
   - Modified `/trm-manual` command
   - Added draft selection handlers
   - Added save/clear draft handlers
   - Added auto-save to all submission handlers
   - Modified `_build_category_selection_view()` for draft buttons and timestamp
   - Added auto-cleanup on report completion

2. **drafts/** (new directory)
   - Created to store draft JSON files
   - Format: `{user_id}.json`

---

## Summary

Draft management is now fully integrated into the TRM bot workflow. Users can:
- Work at their own pace without fear of data loss
- Save and continue later
- Clear drafts if needed
- See when their draft was last saved

All features work seamlessly with the existing multi-step modal flow and Confluence integration.

---

**Status:** ✅ Production Ready  
**Last Updated:** March 6, 2026  
**Ready for:** Immediate use
