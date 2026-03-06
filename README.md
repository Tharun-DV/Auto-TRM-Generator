# Auto-TRM-Generator

A simple Slack bot that responds to the `/trm` slash command with a personalized greeting.

## Quick Start

1. Follow the setup instructions in [SETUP.md](SETUP.md)
2. Install dependencies: `pip install -r requirements.txt`
3. Set your environment variables (see `.env.example`)
4. Run the bot: `python app.py`

## How It Works

- User types `/trm` in Slack
- A modal appears asking for their name
- User enters name and clicks Submit
- Bot sends a DM: "Hello, <name>"