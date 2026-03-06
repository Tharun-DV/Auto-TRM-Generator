# TRM Bot Architecture & Flow

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User (Slack)                             │
│                                                                   │
│                    Sends: /trm week 8                            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TRM Bot (app.py)                              │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 1. handle_trm_command()                                   │  │
│  │    - Parse date range                                     │  │
│  │    - Validate input                                       │  │
│  └──────────────────┬───────────────────────────────────────┘  │
│                     │                                            │
│                     ▼                                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 2. parse_date_range()                                     │  │
│  │    - Handle "week N" format                               │  │
│  │    - Handle "date to date" format                         │  │
│  │    - Return Unix timestamps                               │  │
│  └──────────────────┬───────────────────────────────────────┘  │
│                     │                                            │
│                     ▼                                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 3. fetch_slack_messages()                                 │  │
│  │    - Query Slack API                                      │  │
│  │    - Paginate through results                             │  │
│  │    - Return message list                                  │  │
│  └──────────────────┬───────────────────────────────────────┘  │
│                     │                                            │
│                     ▼                                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 4. summarize_with_portkey()                               │  │
│  │    - Format messages                                      │  │
│  │    - Create AI prompt                                     │  │
│  │    - Call Portkey API                                     │  │
│  │    - Return formatted TRM report                          │  │
│  └──────────────────┬───────────────────────────────────────┘  │
│                     │                                            │
└─────────────────────┼────────────────────────────────────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │   External Services    │
         ├────────────────────────┤
         │ • Slack API            │
         │ • Portkey AI           │
         │ • OpenAI (via Portkey) │
         └────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    User receives report                          │
│                                                                   │
│  📋 ProdEngg TRM — Week 8 | Feb 25 to Mar 4                     │
│  🔴 Issues                                                       │
│  📊 P0 Metrics                                                   │
│  🚨 Alerts Summary                                               │
│  💰 Cost Highlights                                              │
│  🔥 Outages Summary                                              │
│  🎫 Ticket Data                                                  │
│  ✅ Action Items                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Input Processing
```
User Input: "/trm week 8"
     │
     ├─→ Extract command text: "week 8"
     │
     ├─→ parse_date_range("week 8")
     │       │
     │       ├─→ Calculate: Week 8 = Jan 1 + 7 weeks
     │       ├─→ Start: Feb 25, 2026 00:00:00
     │       ├─→ End: Mar 4, 2026 23:59:59
     │       └─→ Return: (oldest_ts, latest_ts, "Feb 25", "Mar 4", 8)
     │
     └─→ Continue to message fetching
```

### Message Fetching
```
fetch_slack_messages(client, "C6P2C6938", oldest_ts, latest_ts)
     │
     ├─→ Call: conversations_history()
     │       │
     │       ├─→ Batch 1: 200 messages
     │       ├─→ Batch 2: 200 messages (if cursor exists)
     │       └─→ Batch 3: 150 messages (final)
     │
     └─→ Return: 550 messages total
             │
             └─→ Format: ["[2026-02-25] Issue with prod", ...]
```

### AI Summarization
```
summarize_with_portkey(messages, "Feb 25", "Mar 4", 8)
     │
     ├─→ Limit to 200 messages (to avoid token overflow)
     │
     ├─→ Build prompt with:
     │       ├─→ System context
     │       ├─→ TRM format instructions
     │       └─→ Message data
     │
     ├─→ POST https://api.portkey.ai/v1/chat/completions
     │       │
     │       ├─→ Header: x-portkey-api-key
     │       ├─→ Body: model=pilot-poc/claude-sonnet-4-5, messages=[...]
     │       └─→ Timeout: 60s
     │
     └─→ Return: Formatted TRM report (Slack mrkdwn)
```

### Report Delivery
```
TRM Report String
     │
     └─→ client.chat_postMessage(
             channel=user_id,
             text=trm_report
         )
             │
             └─→ User receives DM with report
```

---

## Component Interaction Diagram

```
┌─────────────┐
│   Slack     │
│  Workspace  │
└──────┬──────┘
       │
       │ 1. User sends /trm command
       ▼
┌─────────────────────────────────┐
│      Socket Mode Handler        │
│   (handles real-time events)    │
└────────────┬────────────────────┘
             │
             │ 2. Routes to command handler
             ▼
┌─────────────────────────────────┐
│   handle_trm_command()          │
│   • ack() immediately           │
│   • Parse input                 │
└────────────┬────────────────────┘
             │
             │ 3. Fetch messages
             ▼
┌─────────────────────────────────┐
│   Slack Web API                 │
│   • conversations_history       │
│   • Pagination with cursors     │
└────────────┬────────────────────┘
             │
             │ 4. Process with AI
             ▼
┌─────────────────────────────────┐
│   Portkey AI Gateway            │
│   • Routes to Claude/OpenAI     │
│   • Handles auth & rate limits  │
└────────────┬────────────────────┘
             │
             │ 5. AI generates report
             ▼
┌─────────────────────────────────┐
│   Claude Sonnet 4.5             │
│   (via Portkey)                 │
│   • Categorizes issues          │
│   • Extracts metrics            │
│   • Formats as TRM report       │
└────────────┬────────────────────┘
             │
             │ 6. Return formatted report
             ▼
┌─────────────────────────────────┐
│   Bot posts to Slack            │
│   • chat_postMessage            │
│   • Send to user DM             │
└────────────┬────────────────────┘
             │
             │ 7. User sees report
             ▼
┌─────────────────────────────────┐
│   User (Slack Client)           │
│   • Reads TRM report            │
│   • Can share with team         │
└─────────────────────────────────┘
```

---

## Error Handling Flow

```
User Input
    │
    ├─→ Empty input?
    │       └─→ YES → Send help message with examples
    │
    ├─→ Can parse date?
    │       └─→ NO → ValueError → Send error + format examples
    │
    ├─→ Slack API error?
    │       └─→ YES → Exception → Send "Check permissions" message
    │
    ├─→ No messages found?
    │       └─→ YES → Send "No messages found for period"
    │
    ├─→ Portkey API error?
    │       └─→ YES → Send "API error: check key & quota"
    │
    └─→ SUCCESS → Post TRM report
```

---

## State Machine

```
┌─────────────┐
│   IDLE      │ ← Bot running, waiting for commands
└──────┬──────┘
       │ /trm command received
       ▼
┌─────────────┐
│  PARSING    │ ← Parsing date range
└──────┬──────┘
       │ Date parsed
       ▼
┌─────────────┐
│  FETCHING   │ ← Fetching Slack messages
└──────┬──────┘
       │ Messages fetched
       ▼
┌─────────────┐
│ GENERATING  │ ← AI generating report
└──────┬──────┘
       │ Report generated
       ▼
┌─────────────┐
│  POSTING    │ ← Posting report to Slack
└──────┬──────┘
       │ Report posted
       ▼
┌─────────────┐
│   IDLE      │ ← Ready for next command
└─────────────┘

Error at any stage:
    └─→ Send error message → Return to IDLE
```

---

## Security & Authentication

```
Environment Variables (Required)
├── SLACK_BOT_TOKEN
│   └─→ Used for: Slack Web API authentication
│       └─→ Scopes: commands, channels:history, channels:read, chat:write
│
├── SLACK_APP_TOKEN
│   └─→ Used for: Socket Mode connection
│       └─→ Required for: Real-time event handling
│
├── PORTKEY_API_KEY
│   └─→ Used for: Portkey AI authentication
│       └─→ Header: x-portkey-api-key
│       └─→ Routes to: Claude Sonnet 4.5 (or configured model)
│
└── PORTKEY_MODEL (Optional)
    └─→ AI model to use (default: pilot-poc/claude-sonnet-4-5)
        └─→ Examples: gpt-4o, claude-3-opus-20240229

SSL/TLS
└─→ certifi: Provides SSL certificates for secure connections
```

---

## Performance Considerations

### Message Batching
- Fetch up to 200 messages per API call
- Use pagination cursor for additional batches
- Limit to 200 messages for AI processing (configurable)

### Timeout Handling
- Portkey API timeout: 60 seconds
- Slack API: Default timeout (handled by SDK)
- User gets progress updates during processing

### Rate Limits
- Slack API: Tier 3 (~50 requests/minute)
- Portkey AI: Depends on plan
- Consider implementing retry logic for production

---

*For detailed implementation, see app.py*
