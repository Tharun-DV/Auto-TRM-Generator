#!/usr/bin/env python3
"""Test fetching tickets from PRODENGG project."""

import os
from dotenv import load_dotenv
from jira_integration import jira
from datetime import datetime, timedelta

load_dotenv()

if not jira.enabled:
    print("❌ Jira not configured")
    exit(1)

print("🎫 Testing PRODENGG project...")
print(f"   Project keys: {jira.jira_project_keys}")
print()

# Try last 30 days to increase chance of finding tickets
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

start_str = start_date.strftime("%Y-%m-%d")
end_str = end_date.strftime("%Y-%m-%d")

print(f"📅 Searching tickets from {start_str} to {end_str} (last 30 days)")
print()

ticket_data = jira.fetch_tickets(start_str, end_str)

print(f"📊 Results:")
print(f"   Total tickets found: {ticket_data.get('total', 0)}")

if ticket_data.get('total', 0) > 0:
    print()
    print("✅ SUCCESS! Found tickets in PRODENGG/SYSENGG")
    print()
    print(f"   By Status: {ticket_data.get('by_status', {})}")
    print(f"   By Priority: {ticket_data.get('by_priority', {})}")
    print(f"   By Type: {ticket_data.get('by_type', {})}")
    
    if ticket_data.get('tickets'):
        print()
        print("🎫 Sample tickets:")
        for ticket in ticket_data['tickets'][:3]:
            print(f"   • {ticket['key']}: {ticket['summary'][:60]}...")
else:
    print()
    print("⚠️  No tickets found in the last 30 days")
    print()
    print("Possible reasons:")
    print("1. No tickets were created/updated in PRODENGG or SYSENGG in last 30 days")
    print("2. Your Jira user doesn't have access to these projects")
    print("3. The project keys might be incorrect")
    print()
    print("To verify:")
    print("1. Go to https://swiggy.atlassian.net/jira/software/projects/PRODENGG")
    print("2. Check if you can see tickets")
    print("3. Look at a ticket URL to confirm the project key")
