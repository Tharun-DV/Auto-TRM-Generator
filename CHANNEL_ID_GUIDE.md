# How to Find Your Slack Channel ID

## Quick Method

### Step 1: Open the Slack Channel
Navigate to the channel you want to use (e.g., `#devops-help`)

### Step 2: Click Channel Name
Click the channel name at the top of the screen

### Step 3: Scroll to Find Channel ID
In the details panel that opens, scroll down to find the Channel ID

### Step 4: Copy Channel ID
Copy the ID (format: `C01234ABCDE`)

## Visual Guide

```
┌─────────────────────────────────────────────────────┐
│  #devops-help                                [⋮]   │  ← Click here
├─────────────────────────────────────────────────────┤
│                                                     │
│  Channel messages appear here...                   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

After clicking, you'll see:

```
┌──────────────────────────────────┐
│  About                           │
│  ┌────────────────────────────┐  │
│  │ #devops-help               │  │
│  │                            │  │
│  │ Purpose:                   │  │
│  │ DevOps team help           │  │
│  │                            │  │
│  │ Channel ID                 │  │ ← Look for this
│  │ C6P2C6938                  │  │ ← Copy this
│  │                            │  │
│  │ Created                    │  │
│  │ January 15, 2020           │  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘
```

## Alternative Methods

### Method 1: Right-Click on Channel
1. Right-click (or Ctrl+Click) on the channel name in the sidebar
2. Select "Copy link"
3. The link will look like: `https://yourteam.slack.com/archives/C6P2C6938`
4. The Channel ID is the part after `/archives/`: `C6P2C6938`

### Method 2: Via Slack API
```bash
# List all channels
curl -X GET "https://slack.com/api/conversations.list" \
  -H "Authorization: Bearer YOUR_BOT_TOKEN" \
  | jq '.channels[] | select(.name=="devops-help") | .id'
```

### Method 3: Using Slack's Web Interface
1. Go to `https://app.slack.com/client/YOUR_WORKSPACE_ID`
2. Open the channel
3. Look at the URL: `https://app.slack.com/client/T01ABC/C6P2C6938`
4. The Channel ID is `C6P2C6938`

## Channel ID Format

### Valid Format
- Starts with `C` (for channels) or `G` (for groups)
- Followed by 8-10 alphanumeric characters
- Examples:
  - `C6P2C6938` ✅
  - `C01234ABCDE` ✅
  - `G02WXYZ9876` ✅ (private channel)

### Invalid Format
- `devops-help` ❌ (this is the channel name, not ID)
- `#devops-help` ❌ (includes hashtag)
- `c6p2c6938` ❌ (lowercase - channel IDs are uppercase)

## Using Channel ID in Bot

### Update .env File
```bash
# Open .env file
nano .env

# Find this line:
DEVOPS_HELP_CHANNEL_ID=C6P2C6938

# Replace with your channel ID:
DEVOPS_HELP_CHANNEL_ID=C01234ABCDE

# Save and exit
```

### Verify It Works
```bash
# Test environment loading
python test_env.py

# You should see:
# ✅ DEVOPS_HELP_CHANNEL_ID: C01234ABCDE

# Start the bot
python app.py

# You should see:
# 📊 Configuration:
#    • Channel ID: C01234ABCDE
```

## Common Channels

Here are some common Swiggy channels you might use:

| Channel | ID (Example) | Purpose |
|---------|--------------|---------|
| #devops-help | `C6P2C6938` | DevOps support |
| #sre-help | `C02XXXXX` | SRE support |
| #platform-help | `C03XXXXX` | Platform engineering |
| #oncall-alerts | `C04XXXXX` | Oncall notifications |

*Note: Replace with actual channel IDs from your workspace*

## Testing Different Channels

### Test Temporarily
```bash
# Override .env for one run
DEVOPS_HELP_CHANNEL_ID=C01234ABCDE python app.py
```

### Switch Channels
```bash
# Edit .env
nano .env

# Change channel ID
DEVOPS_HELP_CHANNEL_ID=C01234ABCDE

# Restart bot
python app.py
```

### Multiple Channel Support (Future)
Currently the bot supports one channel. To support multiple channels:

1. Create separate .env files:
   - `.env.devops`
   - `.env.sre`
   - `.env.platform`

2. Run bot with specific env file:
   ```bash
   # Load specific env file
   ENV_FILE=.env.devops python app.py
   ```

## Troubleshooting

### "Channel not found" error
```
❌ Error: channel_not_found
```
**Solutions:**
- Verify channel ID is correct
- Check bot has access to channel
- Invite bot to private channels: `/invite @TRM-Bot`

### "Need channels:history scope" error
```
❌ Error: missing_scope - need channels:history
```
**Solutions:**
- Add `channels:history` scope in Slack app settings
- Reinstall the app in your workspace

### Bot sees no messages
```
⚠️ No messages found in #devops-help for the period: Feb 25 to Mar 4
```
**Check:**
1. Channel ID is correct
2. Date range has messages
3. Bot was added to channel before those dates
4. Bot has `channels:history` permission

## Best Practices

### 1. Use Correct Channel
- ✅ Use channel where issues are reported
- ✅ Verify channel is active
- ❌ Don't use announcement-only channels

### 2. Bot Permissions
- ✅ Invite bot to channel: `/invite @TRM-Bot`
- ✅ Verify bot can read history
- ✅ Test with recent messages first

### 3. Privacy
- ⚠️ Public channels: Anyone can see
- ⚠️ Private channels: Only members can see
- ⚠️ Consider data sensitivity when choosing channel

## Quick Reference Card

```
┌─────────────────────────────────────────┐
│  Finding Channel ID                     │
├─────────────────────────────────────────┤
│  1. Click channel name                  │
│  2. Scroll to "Channel ID"              │
│  3. Copy ID (e.g., C6P2C6938)          │
│  4. Update .env:                        │
│     DEVOPS_HELP_CHANNEL_ID=C6P2C6938   │
│  5. Restart bot                         │
└─────────────────────────────────────────┘
```

---

*Last updated: March 6, 2026*
*Default Channel: C6P2C6938 (#devops-help)*
