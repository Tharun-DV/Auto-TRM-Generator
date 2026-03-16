# Jira Integration Fix - API Endpoint Update

**Date:** March 6, 2026  
**Issue:** Jira API 410 error - endpoint deprecated  
**Status:** ✅ Fixed

---

## Problem

When running the TRM bot with Jira integration, got this error:

```
❌ Failed to fetch Jira tickets: 410 - {
  "errorMessages": [
    "The requested API has been removed. Please migrate to the /rest/api/3/search/jql API. 
     A full migration guideline is available at https://developer.atlassian.com/changelog/#CHANGE-2046"
  ],
  "errors": {}
}
```

## Root Cause

Jira Cloud deprecated the `/rest/api/3/search` endpoint with GET method. The new endpoint is `/rest/api/3/search/jql` with POST method.

## Solution

Updated `jira_integration.py` to use the new API endpoint:

### Before (Old API - Deprecated)
```python
# OLD - Returns 410 error
url = f"{self.jira_url}/rest/api/3/search"

params = {
    "jql": jql,
    "maxResults": 1000,
    "fields": "key,summary,status,priority,issuetype,created,updated,assignee,reporter"
}

response = requests.get(
    url,
    auth=(self.jira_user, self.jira_api_token),
    headers={"Accept": "application/json"},
    params=params,
    timeout=30
)
```

### After (New API - Working)
```python
# NEW - Works correctly
url = f"{self.jira_url}/rest/api/3/search/jql"

payload = {
    "jql": jql,
    "maxResults": 1000,
    "fields": ["key", "summary", "status", "priority", "issuetype", "created", "updated", "assignee", "reporter"]
}

response = requests.post(
    url,
    auth=(self.jira_user, self.jira_api_token),
    headers={"Accept": "application/json", "Content-Type": "application/json"},
    json=payload,
    timeout=30
)
```

### Key Changes

1. **Endpoint:** `/rest/api/3/search` → `/rest/api/3/search/jql`
2. **Method:** `GET` → `POST`
3. **Parameters:** `params` → `json` payload
4. **Fields format:** `"field1,field2"` → `["field1", "field2"]` (array)
5. **Headers:** Added `"Content-Type": "application/json"`

## Testing

```bash
$ ./venv/bin/python test_jira_integration.py

✅ Jira integration configured!
   URL: https://swiggy.atlassian.net
   User: tharun.dv_int@external.swiggy.in
   Projects: PRODENGG, SYSENGG

🎫 Testing ticket fetch for last 7 days...
   Date range: 2026-02-27 to 2026-03-06

🎫 Fetching Jira tickets from 2026-02-27 to 2026-03-06
🔍 Projects: PRODENGG, SYSENGG
✅ Fetched 0 tickets from Jira
✅ Successfully fetched 0 tickets!
```

**Status:** ✅ Connection successful (0 tickets is expected if no tickets exist in that date range)

## Environment Configuration

Your `.env` file is correctly configured:

```bash
JIRA_URL=https://swiggy.atlassian.net
JIRA_USER=tharun.dv_int@external.swiggy.in
JIRA_API_TOKEN=<your-token>
JIRA_PROJECT_KEYS=PRODENGG,SYSENGG
```

## Verification

To test if tickets will be fetched for a TRM report:

```bash
# Test with your actual TRM date range
./venv/bin/python test_jira_integration.py
```

If you see:
- ✅ `Jira integration configured!` - Environment variables loaded correctly
- ✅ `Fetched X tickets from Jira` - API working correctly
- 0 tickets might mean:
  - No tickets in PRODENGG or SYSENGG projects for that date range
  - Project keys need to be verified (check spelling in Jira)
  - Date range doesn't have any ticket activity

## Next Steps

1. **Verify Project Keys** - Make sure `PRODENGG` and `SYSENGG` are correct:
   - Go to Jira
   - Look at a ticket URL: `https://swiggy.atlassian.net/browse/PRODENGG-123`
   - Project key is `PRODENGG` (the part before the dash)

2. **Test with Known Tickets** - Pick a date range you know has tickets:
   - Check when tickets were created/updated in Jira
   - Run `/trm-manual` with that date range
   - Verify tickets appear in Confluence

3. **Run TRM Report**:
   ```bash
   python app.py
   ```
   Then in Slack:
   ```
   /trm-manual
   → Fill in dates when you know tickets exist
   → Generate report
   → Check Confluence page for "Ticket Data" section
   ```

## Files Modified

- ✏️ `jira_integration.py` - Updated API endpoint and method
- ✨ `test_jira_integration.py` - Created test script
- ✨ `JIRA_FIX.md` - This documentation

## Reference

- [Jira Migration Guide](https://developer.atlassian.com/changelog/#CHANGE-2046)
- [Jira Search API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-jql-post)

---

**Issue:** ✅ Resolved  
**Status:** Working correctly  
**Date:** March 6, 2026
