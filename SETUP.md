# Slack TRM Bot Setup Instructions

## Prerequisites
- Python 3.7 or higher
- A Slack workspace where you have permission to install apps

## Step 1: Create a Slack App
1. Go to https://api.slack.com/apps
2. Click **"Create New App"** → **"From scratch"**
3. Enter App Name: `TRM Bot`
4. Select your workspace
5. Click **"Create App"**

## Step 2: Configure Slash Command
1. In your app settings, go to **"Slash Commands"** in the sidebar
2. Click **"Create New Command"**
3. Enter the following:
   - **Command**: `/trm`
   - **Request URL**: (not needed for Socket Mode)
   - **Short Description**: `Trigger TRM greeting`
   - **Usage Hint**: (leave empty)
4. Click **"Save"**

## Step 3: Enable Socket Mode
1. Go to **"Socket Mode"** in the sidebar
2. Toggle **"Enable Socket Mode"** to ON
3. Give your token a name (e.g., `TRM App Token`)
4. Click **"Generate"**
5. **IMPORTANT**: Copy the `xapp-...` token and save it (this is your `SLACK_APP_TOKEN`)

## Step 4: Configure OAuth & Permissions
1. Go to **"OAuth & Permissions"** in the sidebar
2. Under **"Scopes"** → **"Bot Token Scopes"**, add:
   - `chat:write`
   - `commands`
3. Scroll up and click **"Install to Workspace"**
4. Click **"Allow"**
5. **IMPORTANT**: Copy the `xoxb-...` token (this is your `SLACK_BOT_TOKEN`)

## Step 5: Set Up Environment Variables
Create a `.env` file in the project directory or export the variables:

```bash
export SLACK_BOT_TOKEN="xoxb-your-bot-token"
export SLACK_APP_TOKEN="xapp-your-app-token"
```

## Step 6: Install Dependencies and Run
```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python app.py
```

### SSL Certificate Issues (Corporate Networks)
If you encounter SSL certificate errors, you have two options:

**Option 1: Use certifi (recommended)**
The app now uses certifi for proper SSL certificate handling. Make sure it's installed:
```bash
pip install -r requirements.txt
python app.py
```

**Option 2: Disable SSL verification (testing only)**
If you're behind a corporate proxy and still have issues:
```bash
python app_no_ssl_verify.py
```
⚠️ **Warning**: This disables SSL verification and should only be used for testing in controlled environments.

## Testing the Bot
1. Go to any channel in your Slack workspace
2. Type `/trm` and press Enter
3. A modal will appear asking for your name
4. Enter your name and click **"Submit"**
5. You'll receive a direct message: `Hello, <your name>`

## Troubleshooting
- Make sure both tokens are correctly set as environment variables
- Ensure the app is installed in your workspace
- Check that Socket Mode is enabled
- Verify the slash command is created and saved
