# Confluence Integration Setup Guide

**Feature:** Create TRM Reports as Confluence Pages  
**Status:** ✅ Implemented  
**Date:** March 6, 2026

## Overview

The TRM bot now creates **Confluence pages** instead of posting markdown to Slack. When you use `/trm-manual`, the report is created as a formatted Confluence page with tables and proper styling.

## Setup Instructions

### Step 1: Get Confluence API Token

1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **"Create API token"**
3. Give it a name (e.g., "TRM Bot")
4. Copy the token (you won't be able to see it again!)

### Step 2: Find Your Confluence Details

#### Confluence URL:
```
https://your-company.atlassian.net/wiki
```
Or your self-hosted URL:
```
https://confluence.your-company.com
```

#### Space Key:
1. Go to your Confluence space
2. Look at the URL: `https://your-company.atlassian.net/wiki/spaces/DEVOPS/...`
3. The space key is `DEVOPS` (the part after `/spaces/`)

#### Parent Page ID (Optional):
If you want all TRM reports under a specific page:
1. Go to that page in Confluence
2. Click **"..."** → **"Page Information"**
3. Look at the URL: `https://your-company.atlassian.net/wiki/pages/viewinfo.action?pageId=123456789`
4. The page ID is `123456789`

### Step 3: Set Environment Variables

Add these to your `.env` file:

```bash
# Confluence Configuration
CONFLUENCE_URL=https://your-company.atlassian.net/wiki
CONFLUENCE_USER=your.email@company.com
CONFLUENCE_API_TOKEN=your-api-token-here
CONFLUENCE_SPACE_KEY=DEVOPS
CONFLUENCE_PARENT_ID=123456789  # Optional - omit to create at space root
```

### Step 4: Install Confluence Library

The bot uses the `requests` library which is already installed, so no additional dependencies are needed!

### Step 5: Test the Integration

```bash
# Start the bot
python app.py

# In Slack, type:
/trm-manual

# Fill in the form and submit
# You should receive a Slack message with the Confluence page URL!
```

## Example Output

After submitting the TRM report, you'll receive:

```
✅ TRM Report Created!

📄 Confluence Page: https://your-company.atlassian.net/wiki/spaces/DEVOPS/pages/123456789

Week 10 | Mar 2 to Mar 8
Oncall: Alice
```

## Confluence Page Format

The created page will have:

### ✅ Structured Sections
- 📋 Header with week number, date range, oncall
- 🔴 Issues table (grouped by theme)
- 📊 P0 Metrics table
- 🚨 Alerts Summary table
- 💰 Cost Highlights table
- 🔥 Outages Summary table
- 🎫 Ticket Data list
- ✅ Action Items table

### ✅ Professional Formatting
- HTML tables with headers
- Bold section titles
- Emoji icons for visual clarity
- Proper spacing and layout

### ✅ Easy to Edit
- Standard Confluence page
- Can be edited like any other page
- Version history tracked
- Can add comments and mentions

## Fallback Behavior

If Confluence is **not configured** or **fails**:
1. The bot will post the TRM report to Slack (as markdown)
2. You'll receive a warning message
3. No errors - the bot continues to work

**Example fallback message:**
```
⚠️ Confluence page creation failed. Report posted to Slack instead.
```

## Troubleshooting

### Error: "Confluence not configured"

**Cause:** Environment variables not set  
**Fix:** Add `CONFLUENCE_URL`, `CONFLUENCE_USER`, and `CONFLUENCE_API_TOKEN` to `.env`

### Error: 401 Unauthorized

**Cause:** Invalid API token or email  
**Fix:** 
- Verify your email matches your Confluence account
- Regenerate API token if needed
- Check for extra spaces in `.env` file

### Error: 403 Forbidden

**Cause:** Insufficient permissions  
**Fix:**
- Verify you have permission to create pages in the space
- Ask Confluence admin to grant "Create" permission
- Try a different space where you have access

### Error: 404 Space Not Found

**Cause:** Invalid space key  
**Fix:**
- Double-check the space key (case-sensitive!)
- Visit the space in browser to verify it exists
- Use the exact key from the URL

### Error: Parent page not found

**Cause:** Invalid parent page ID  
**Fix:**
- Remove `CONFLUENCE_PARENT_ID` to create at space root
- Verify the page ID is correct
- Check you have access to the parent page

### Page created but looks wrong

**Cause:** Confluence rendering issue  
**Fix:**
- Edit the page manually to fix formatting
- Check if your Confluence version supports HTML storage format
- Contact support if issue persists

## Configuration Options

### Option 1: Create at Space Root (Recommended)

```bash
CONFLUENCE_URL=https://your-company.atlassian.net/wiki
CONFLUENCE_USER=your.email@company.com
CONFLUENCE_API_TOKEN=your-token
CONFLUENCE_SPACE_KEY=DEVOPS
# No CONFLUENCE_PARENT_ID - creates at space root
```

### Option 2: Create Under Parent Page

```bash
CONFLUENCE_URL=https://your-company.atlassian.net/wiki
CONFLUENCE_USER=your.email@company.com
CONFLUENCE_API_TOKEN=your-token
CONFLUENCE_SPACE_KEY=DEVOPS
CONFLUENCE_PARENT_ID=123456789  # All TRMs under this page
```

### Option 3: Self-Hosted Confluence

```bash
CONFLUENCE_URL=https://confluence.your-company.com
CONFLUENCE_USER=your-username  # May be username instead of email
CONFLUENCE_API_TOKEN=your-token
CONFLUENCE_SPACE_KEY=DEVOPS
```

## Security Best Practices

1. **Never commit `.env` file** - It contains your API token!
2. **Use API tokens, not passwords** - More secure and can be revoked
3. **Limit token permissions** - Use a dedicated token for the bot
4. **Rotate tokens regularly** - Update every 90 days
5. **Monitor usage** - Check Confluence audit log for bot activity

## Advanced: Customizing the Page Template

The page format is defined in `confluence_integration.py` in the `_build_confluence_content()` method. You can customize:

- HTML structure
- CSS styling (if supported)
- Table layouts
- Section order
- Additional metadata

## API Rate Limits

Confluence Cloud has rate limits:
- **Free:** 10 requests/minute
- **Standard:** 100 requests/minute
- **Premium:** 1000 requests/minute

The bot makes **1 request per TRM report**, so rate limits shouldn't be an issue for normal use.

## Support

### Confluence API Documentation
- https://developer.atlassian.com/cloud/confluence/rest/v1/intro/
- https://developer.atlassian.com/cloud/confluence/rest/v2/intro/

### Getting Help
1. Check bot logs for detailed error messages
2. Verify all environment variables are set correctly
3. Test Confluence API access with curl:
   ```bash
   curl -u "your.email@company.com:your-api-token" \
     https://your-company.atlassian.net/wiki/rest/api/space
   ```

---

**Version:** 3.1 (Confluence Integration)  
**Last Updated:** March 6, 2026
