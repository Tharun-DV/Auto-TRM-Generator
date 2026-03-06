# Modal Closing Fix

**Issue:** After generating TRM report, another TRM manual modal opens instead of closing completely.

**Cause:** The final submission handler was using `ack()` without telling Slack to close the modals.

**Fix Applied:** Changed to `ack(response_action="clear")` which closes all modals in the stack.

## Code Change

```python
# Before (incorrect):
@app.view("trm_category_selection_modal")
def handle_trm_category_selection_modal_submission(ack, body, client):
    user_id = body["user"]["id"]
    ack()  # ❌ Doesn't close modals
    # ... rest of code

# After (correct):
@app.view("trm_category_selection_modal")
def handle_trm_category_selection_modal_submission(ack, body, client):
    user_id = body["user"]["id"]
    ack(response_action="clear")  # ✅ Closes all modals
    # ... rest of code
```

## Slack Response Actions

| Action | Effect |
|--------|--------|
| `ack()` | Keeps modal open |
| `ack(response_action="update", view={...})` | Updates current modal |
| `ack(response_action="push", view={...})` | Pushes new modal onto stack |
| `ack(response_action="clear")` | **Closes all modals** ✅ |

## Expected Behavior Now

1. User clicks **"Finish & Generate"**
2. Modal closes immediately
3. User sees Slack workspace (no modal)
4. User receives DM with Confluence URL or report
5. Done! ✅

## Testing

```bash
# 1. Start bot
python app.py

# 2. In Slack: /trm-manual
# 3. Fill in form
# 4. Add some entries
# 5. Click "Finish & Generate"
# 6. Modal should close completely ✅
# 7. Receive DM with result
```

**Status:** ✅ Fixed  
**File Modified:** `app.py` (line 1225)
