#!/usr/bin/env python3
"""Quick test to verify Jira integration works."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import jira integration
from jira_integration import jira

if not jira.enabled:
    print("❌ Jira integration not configured")
    print("\nCheck these variables in .env:")
    print(f"  JIRA_URL: {os.environ.get('JIRA_URL', 'NOT SET')}")
    print(f"  JIRA_USER: {os.environ.get('JIRA_USER', 'NOT SET')}")
    print(f"  JIRA_API_TOKEN: {'SET' if os.environ.get('JIRA_API_TOKEN') else 'NOT SET'}")
    print(f"  JIRA_PROJECT_KEYS: {os.environ.get('JIRA_PROJECT_KEYS', 'NOT SET')}")
    sys.exit(1)

print("✅ Jira integration configured!")
print(f"   URL: {jira.jira_url}")
print(f"   User: {jira.jira_user}")
print(f"   Projects: {', '.join(jira.jira_project_keys)}")
print()

# Test fetching tickets
print("🎫 Testing ticket fetch for last 7 days...")
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=7)

start_str = start_date.strftime("%Y-%m-%d")
end_str = end_date.strftime("%Y-%m-%d")

print(f"   Date range: {start_str} to {end_str}")
print()

ticket_data = jira.fetch_tickets(start_str, end_str)

if ticket_data:
    print(f"✅ Successfully fetched {ticket_data.get('total', 0)} tickets!")
    print()
    print("📊 Summary:")
    print(f"   Total: {ticket_data.get('total', 0)}")
    
    if ticket_data.get('by_status'):
        print(f"   By Status: {ticket_data['by_status']}")
    
    if ticket_data.get('by_priority'):
        print(f"   By Priority: {ticket_data['by_priority']}")
    
    if ticket_data.get('by_type'):
        print(f"   By Type: {ticket_data['by_type']}")
    
    if ticket_data.get('tickets'):
        print()
        print("🎫 Sample tickets (first 5):")
        for i, ticket in enumerate(ticket_data['tickets'][:5], 1):
            print(f"   {i}. {ticket['key']}: {ticket['summary'][:60]}...")
            print(f"      Status: {ticket['status']}, Priority: {ticket['priority']}, Type: {ticket['type']}")
else:
    print("⚠️ No tickets found or error occurred")
