#!/usr/bin/env python3
"""
Test script to verify .env file loading
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, '/Users/tharun.dv_int/src/tries/Auto-TRM-Generator')

from dotenv import load_dotenv

print("=" * 60)
print("Testing .env File Loading")
print("=" * 60)
print()

# Test 1: Load .env file
print("1️⃣ Loading .env file...")
load_dotenv()
print("   ✅ .env file loaded")
print()

# Test 2: Check required variables
print("2️⃣ Checking environment variables:")
required_vars = [
    "SLACK_BOT_TOKEN",
    "SLACK_APP_TOKEN",
    "PORTKEY_API_KEY",
]

optional_vars = [
    ("PORTKEY_MODEL", "pilot-poc/claude-sonnet-4-5"),
    ("DEVOPS_HELP_CHANNEL_ID", "C6P2C6938"),
    ("DISABLE_SSL_VERIFY", None)
]

all_good = True

for var in required_vars:
    value = os.environ.get(var)
    if value:
        # Mask sensitive data
        if len(value) > 20:
            masked = value[:10] + "..." + value[-4:]
        else:
            masked = value[:5] + "..."
        print(f"   ✅ {var}: {masked}")
    else:
        print(f"   ❌ {var}: Not set")
        all_good = False

print()
print("3️⃣ Checking optional variables:")
for var, default in optional_vars:
    value = os.environ.get(var)
    if value:
        print(f"   ✅ {var}: {value}")
    else:
        print(f"   ℹ️  {var}: Not set (default: {default})")

print()
print("=" * 60)

if all_good:
    print("✅ All required environment variables are set!")
    print()
    print("📊 Configuration Summary:")
    print(f"   • Channel ID: {os.environ.get('DEVOPS_HELP_CHANNEL_ID', 'C6P2C6938')}")
    print(f"   • AI Model: {os.environ.get('PORTKEY_MODEL', 'pilot-poc/claude-sonnet-4-5')}")
    print(f"   • SSL Verify: {'Disabled' if os.environ.get('DISABLE_SSL_VERIFY') == '1' else 'Enabled'}")
    print()
    print("🚀 Ready to start the bot!")
    print("   Run: python app.py")
else:
    print("❌ Some required environment variables are missing!")
    print("   Check your .env file")

print("=" * 60)
