import os
import sys
import ssl
import certifi
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.web.client import WebClient

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")

ssl_context = ssl.create_default_context(cafile=certifi.where())

if not SLACK_BOT_TOKEN:
    print("Error: SLACK_BOT_TOKEN environment variable is not set.")
    print("\nPlease set your environment variables:")
    print("  export SLACK_BOT_TOKEN='xoxb-your-bot-token'")
    print("  export SLACK_APP_TOKEN='xapp-your-app-token'")
    print("\nSee SETUP.md for detailed instructions.")
    sys.exit(1)

if not SLACK_APP_TOKEN:
    print("Error: SLACK_APP_TOKEN environment variable is not set.")
    print("\nPlease set your environment variables:")
    print("  export SLACK_BOT_TOKEN='xoxb-your-bot-token'")
    print("  export SLACK_APP_TOKEN='xapp-your-app-token'")
    print("\nSee SETUP.md for detailed instructions.")
    sys.exit(1)

client = WebClient(token=SLACK_BOT_TOKEN, ssl=ssl_context)
app = App(token=SLACK_BOT_TOKEN, client=client)


@app.command("/trm")
def handle_trm_command(ack, body, client):
    ack()
    
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "trm_modal",
            "title": {"type": "plain_text", "text": "TRM Bot"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "close": {"type": "plain_text", "text": "Cancel"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "name_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "name_input",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Enter your name"
                        }
                    },
                    "label": {"type": "plain_text", "text": "Name"}
                }
            ]
        }
    )


@app.view("trm_modal")
def handle_trm_modal_submission(ack, body, client, view):
    name = view["state"]["values"]["name_block"]["name_input"]["value"]
    user_id = body["user"]["id"]
    
    ack()
    
    client.chat_postMessage(
        channel=user_id,
        text=f"Hello, {name}"
    )


if __name__ == "__main__":
    print("⚡️ Slack TRM Bot is starting...")
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    print("✅ Bot is running! Use /trm in your Slack workspace.")
    handler.start()
