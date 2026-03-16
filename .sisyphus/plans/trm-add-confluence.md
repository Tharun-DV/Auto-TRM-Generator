# Work Plan: Add Confluence + Jira to /trm Command

## TL;DR

> **Quick Summary**: Modify `/trm` command to fetch Jira tickets and create Confluence page with structured data from AI JSON output
> 
> **Deliverables**:
> - `/trm` command creates Confluence page with ticket data
> - AI outputs structured JSON (instead of plain text)
> - Slack DM sends only Confluence link
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 2 waves
> **Critical Path**: Modify AI prompt → Parse JSON → Add Jira/Confluence integration

---

## Context

### Original Request
User wants `/trm` command to:
1. Open modal with date pickers (already exists ✅)
2. Fetch Jira tickets for selected dates
3. Create Confluence page with ticket data pre-filled

### Metis Review Findings
- **Critical Issue**: `/trm` produces plain text, `/trm-manual` produces structured dicts
- `create_trm_page()` expects structured data (metadata, issues, metrics, etc.)
- **Solution**: Modify AI to output JSON → parse → use existing Confluence method

### User Decisions Confirmed
- **Page Format**: Structured JSON from AI (modify prompt to output JSON)
- **Slack Post**: Confluence link only (no AI text in Slack)
- **Oncall**: Use placeholder "AI-Generated"

---

## Work Objectives

### Core Objective
Modify `/trm` command to create Confluence pages with Jira ticket data

### Concrete Deliverables
1. Modified AI prompt in `summarize_with_portkey()` to output structured JSON
2. Modified `handle_trm_modal_submission()` to:
   - Parse AI JSON response
   - Fetch Jira tickets for date range
   - Create Confluence page using existing `create_trm_page()`
   - Send Confluence link to user (no Slack text)
3. Graceful fallback if Jira/Confluence not configured

### Must Have
- [ ] `/trm` creates Confluence page with ticket data
- [ ] AI outputs structured JSON format
- [ ] Oncall shown as "AI-Generated" in Confluence
- [ ] Graceful fallback if Jira/Confluence unavailable

### Must NOT Have
- [ ] Don't modify `/trm-manual` handler or behavior
- [ ] Don't modify existing integration files (jira_integration.py, confluence_integration.py)
- [ ] Don't post AI text to Slack (Confluence link only)

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (test_bot.py, test_jira_integration.py - manual scripts)
- **Automated tests**: Tests-after (modify existing manual tests)
- **Framework**: Manual testing in Slack

### QA Policy
Every task includes agent-executed QA:
- Test in Slack: `/trm` → select dates → verify Confluence page created
- Verify Jira tickets appear in page
- Verify oncall shows "AI-Generated"

---

## Execution Strategy

### Parallel Waves

```
Wave 1 (Foundation):
├── Task 1: Modify AI prompt to output structured JSON
├── Task 2: Add JSON parsing in /trm handler
└── Task 3: Add Jira ticket fetch to /trm handler

Wave 2 (Integration):
├── Task 4: Add Confluence page creation
├── Task 5: Add progress messages & graceful fallback
└── Task 6: Test end-to-end in Slack
```

### Dependency Matrix
- Task 1: — — 2, 4
- Task 2: 1 — 4, 5
- Task 3: — — 4, 5
- Task 4: 1, 2, 3 — 5, 6
- Task 5: 2, 3, 4 — 6
- Task 6: 4, 5 — —

---

## TODOs

- [x] 1. **Modify AI prompt to output structured JSON**

  **What to do**:
  - Find `summarize_with_portkey()` function in app.py (~line 250)
  - Modify the AI prompt to request JSON output with structure:
    ```json
    {
      "week_number": 10,
      "date_range": "Mar 2 to Mar 8", 
      "oncall": "AI-Generated",
      "issues": [{"theme": "...", "description": "..."}],
      "metrics": [{"metric_name": "...", "last_week": "...", "current_week": "...", "delta": "..."}],
      "alerts": [{"component": "...", "alert_name": "...", "frequency": "...", "description": "..."}],
      "cost": [{"resource": "...", "last_week_cost": "...", "this_week_cost": "..."}],
      "outages": [{"outage_name": "...", "severity": "...", "reason": "...", "owner": "...", "date": "..."}],
      "action_items": [{"description": "...", "owner": "...", "eta": "..."}]
    }
    ```
  - Add instruction to output ONLY JSON, no markdown code blocks
  
  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 2, 3)
  - **Blocks**: Task 2, 4
  - **Blocked By**: None

  **References**:
  - `app.py:250-300` - Current `summarize_with_portkey()` function

  **QA Scenarios**:
  - Test AI with sample messages → verify JSON output format
  - Verify JSON can be parsed by json.loads()

- [x] 2. **Add JSON parsing in /trm handler**

  **What to do**:
  - In `handle_trm_modal_submission()` after AI call (~line 1800)
  - Add JSON parsing:
    ```python
    try:
        data = json.loads(trm_report)
        metadata = {
            'week_number': data.get('week_number', week_num),
            'date_range': f"{start_date_display} to {end_date_display}",
            'oncall': 'AI-Generated'
        }
        # Build data dict from JSON
        trm_data = {
            'issues': data.get('issues', []),
            'metrics': data.get('metrics', []),
            'alerts': data.get('alerts', []),
            'cost': data.get('cost', []),
            'outages': data.get('outages', []),
            'action_items': data.get('action_items', [])
        }
    except json.JSONDecodeError:
        # Fallback: post original text to Slack if JSON parsing fails
        client.chat_postMessage(channel=user_id, text=f"⚠️ Could not parse AI response. Posting text instead:\n{trm_report}")
        return
    ```
  
  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 1, 3)
  - **Blocks**: Task 4, 5
  - **Blocked By**: Task 1

  **References**:
  - `app.py:1800` - Where trm_report is generated
  - `app.py:1560-1600` - Example of metadata/data dict structure from /trm-manual

  **QA Scenarios**:
  - Test with valid JSON → Confluence page created
  - Test with invalid JSON → Falls back to Slack text

- [x] 3. **Add Jira ticket fetch to /trm handler**

  **What to do**:
  - In `handle_trm_modal_submission()` after date extraction (~line 1775)
  - Add Jira fetch (similar to /trm-manual lines ~1696):
    ```python
    ticket_data = jira.fetch_tickets(start_date_str, end_date_str)
    ```
  - Add progress message: "🎫 Fetching Jira tickets..."
  
  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 1, 2)
  - **Blocks**: Task 4, 5
  - **Blocked By**: None

  **References**:
  - `app.py:1696` - Jira fetch in /trm-manual
  - `jira_integration.py:29` - fetch_tickets() method

  **QA Scenarios**:
  - Test with Jira configured → tickets fetched
  - Test with Jira not configured → continues without tickets

- [x] 4. **Add Confluence page creation**

  **What to do**:
  - In `handle_trm_modal_submission()` after JSON parsing and Jira fetch
  - Call existing Confluence method:
    ```python
    confluence_url = confluence.create_trm_page(metadata, trm_data, ticket_data)
    ```
  - Send Confluence link to user (NOT the AI text):
    ```python
    if confluence_url:
        client.chat_postMessage(
            channel=user_id,
            text=f"✅ TRM Report Created!\n\n📄 *Confluence Page:* {confluence_url}\n\n*Week {metadata['week_number']} | {metadata['date_range']}*"
        )
    else:
        # Fallback: post AI text if Confluence fails
        client.chat_postMessage(channel=user_id, text=trm_report)
    ```
  
  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 5, 6
  - **Blocked By**: Task 1, 2, 3

  **References**:
  - `app.py:1701` - Confluence create in /trm-manual
  - `confluence_integration.py:30` - create_trm_page() method

  **QA Scenarios**:
  - Test with Confluence configured → page created, link sent
  - Test with Confluence not configured → falls back to Slack text

- [x] 5. **Add progress messages & graceful fallback**

  **What to do**:
  - Add progress messages at each stage:
    - "🔄 Generating TRM report..." (already exists)
    - "🎫 Fetching Jira tickets..." (add)
    - "🤖 Generating AI summary..." (add)  
    - "📄 Creating Confluence page..." (add)
  - Ensure graceful fallback if any integration fails:
    - Jira fails → continue without tickets
    - Confluence fails → post AI text to Slack
    - JSON parse fails → post AI text to Slack
  
  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 6
  - **Blocked By**: Task 2, 3, 4

  **References**:
  - `app.py:1751-1753` - Existing progress messages

  **QA Scenarios**:
  - Test each failure scenario → correct fallback behavior

- [ ] 6. **Test end-to-end in Slack**

  **What to do**:
  - Run `/trm` command in Slack
  - Select date range via modal
  - Verify Confluence page is created
  - Verify Jira tickets appear in page
  - Verify oncall shows "AI-Generated"
  - Verify Slack DM has Confluence link only (no long text)
  
  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: None
  - **Blocked By**: Task 4, 5

  **QA Scenarios**:
  - Full flow test in Slack → Confluence page with tickets created

---

## Final Verification Wave

- [x] F1. **Verify /trm-manual unchanged**
  - Run existing test scripts
  - Check no modifications to /trm-manual handlers

- [x] F2. **Code quality check**
  - No syntax errors
  - JSON parsing has try/except

- [ ] F3. **Manual Slack test**
  - Execute /trm in Slack
  - Verify Confluence page created

---

## Commit Strategy

- Commit 1: `feat(/trm): Add JSON output to AI prompt`
- Commit 2: `feat(/trm): Add Jira fetch and Confluence page creation`

---

## Success Criteria

- [ ] `/trm` creates Confluence page
- [ ] Jira tickets appear in page
- [ ] Oncall shows "AI-Generated"
- [ ] Slack sends only Confluence link
- [ ] Graceful fallback when integrations unavailable
- [ ] `/trm-manual` works unchanged
