# Step-by-Step Slack App Setup Guide

## Part 1: Create Your Slack App

### 1. Go to Slack API Website
- Open your browser and go to: **https://api.slack.com/apps**
- Sign in with your Slack account

### 2. Create a New App
- Click the green **"Create New App"** button
- Select **"From scratch"**
- Fill in the details:
  - **App Name**: `TRM Bot` (or any name you prefer)
  - **Pick a workspace**: Select your Slack workspace
- Click **"Create App"**

---

## Part 2: Enable Socket Mode

### 3. Enable Socket Mode (IMPORTANT - Do this first!)
- In the left sidebar, scroll down and click **"Socket Mode"**
- Toggle **"Enable Socket Mode"** to **ON**
- A popup will appear asking you to create an app-level token:
  - **Token Name**: `TRM App Token` (or any name)
  - Click **"Generate"**
- **IMPORTANT**: You'll see a token starting with `xapp-`
  - **Copy this token immediately** and save it somewhere safe
  - This is your `SLACK_APP_TOKEN`

---

## Part 3: Create the Slash Command

### 4. Add Slash Command
- In the left sidebar, click **"Slash Commands"**
- Click **"Create New Command"**
- Fill in the form:
  - **Command**: `/trm`
  - **Request URL**: Leave blank or put any placeholder like `https://example.com` (not used in Socket Mode)
  - **Short Description**: `Trigger TRM greeting bot`
  - **Usage Hint**: Leave empty (optional)
- Click **"Save"**

---

## Part 4: Add Bot Permissions

### 5. Configure OAuth & Permissions
- In the left sidebar, click **"OAuth & Permissions"**
- Scroll down to **"Scopes"** section
- Under **"Bot Token Scopes"**, click **"Add an OAuth Scope"**
- Add these two scopes:
  1. `chat:write` - (Allows bot to send messages)
  2. `commands` - (Allows bot to respond to slash commands)

---

## Part 5: Install the App to Your Workspace

### 6. Install to Workspace
- Scroll back to the top of the **"OAuth & Permissions"** page
- Click the **"Install to Workspace"** button
- Review the permissions and click **"Allow"**
- **IMPORTANT**: You'll see a **Bot User OAuth Token** starting with `xoxb-`
  - **Copy this token immediately** and save it
  - This is your `SLACK_BOT_TOKEN`

---

## Part 6: Set Up Your Environment Variables

### 7. Configure Your Local Environment

Create a `.env` file or export the tokens:

```bash
export SLACK_BOT_TOKEN="xoxb-your-actual-token-here"
export SLACK_APP_TOKEN="xapp-your-actual-token-here"
```

**Or create a `.env` file** (recommended):
```bash
# In the project directory
cat > .env << 'EOF'
SLACK_BOT_TOKEN=xoxb-your-actual-token-here
SLACK_APP_TOKEN=xapp-your-actual-token-here
EOF
```

Then load it:
```bash
source .env  # or: export $(cat .env | xargs)
```

---

## Part 7: Run Your Bot

### 8. Start the Bot
```bash
# Make sure you're in the project directory
cd /Users/tharun.dv_int/src/tries/Auto-TRM-Generator

# Activate virtual environment
source venv/bin/activate

# Install dependencies (if not done already)
pip install -r requirements.txt

# Run the bot
python3 app.py
```

You should see:
```
⚡️ Slack TRM Bot is starting...
✅ Bot is running! Use /trm in your Slack workspace.
```

---

## Part 8: Test Your Bot

### 9. Use the `/trm` Command
- Open your Slack workspace
- Go to any channel (or DM yourself)
- Type: `/trm`
- Press Enter
- A modal should pop up asking for your name
- Enter your name and click **"Submit"**
- You should receive a DM from the bot saying: `Hello, [your name]`

---

## Troubleshooting

### Issue: `/trm` command not showing up
- **Solution**: Make sure you created the slash command in Step 4
- Wait a few seconds and try typing `/trm` again
- Try refreshing your Slack app (Cmd+R on Mac, Ctrl+R on Windows)

### Issue: "dispatch_failed" error
- **Solution**: Make sure Socket Mode is enabled (Step 3)
- Verify your `SLACK_APP_TOKEN` starts with `xapp-`

### Issue: "not_authed" or authentication errors
- **Solution**: Check your `SLACK_BOT_TOKEN` starts with `xoxb-`
- Make sure the app is installed to your workspace (Step 6)

### Issue: Bot doesn't respond
- **Solution**: Make sure your Python bot is running (`python3 app.py`)
- Check the terminal for any error messages
- Verify both tokens are correctly set as environment variables

### Issue: SSL Certificate errors
- **Solution**: See the SSL troubleshooting section in SETUP.md
- Try using `python3 app_no_ssl_verify.py` if behind corporate proxy

---

## Quick Checklist

✅ Created Slack app at api.slack.com/apps  
✅ Enabled Socket Mode and got `SLACK_APP_TOKEN` (xapp-...)  
✅ Created `/trm` slash command  
✅ Added `chat:write` and `commands` scopes  
✅ Installed app to workspace and got `SLACK_BOT_TOKEN` (xoxb-...)  
✅ Set environment variables  
✅ Installed dependencies with `pip install -r requirements.txt`  
✅ Running bot with `python3 app.py`  
✅ Bot shows "✅ Bot is running!" message  

---

## Need More Help?

If you're still having issues:
1. Check the terminal where you're running `python3 app.py` for error messages
2. Verify your tokens are correct and start with the right prefixes
3. Make sure Socket Mode is enabled
4. Try reinstalling the app to your workspace
