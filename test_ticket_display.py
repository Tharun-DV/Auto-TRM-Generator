#!/usr/bin/env python3
"""Test to show how tickets will be displayed in Confluence."""

import os
from confluence_integration import confluence

# Mock ticket data (like the example you provided)
mock_ticket_data = {
    "total": 7,
    "by_status": {"Done": 3, "To Do": 4},
    "by_priority": {},
    "by_type": {},
    "tickets": [
        {
            "key": "PRODENGG-7373",
            "summary": "Whitelist preprod.singapore for the mumbai deployments",
            "status": "Done",
            "priority": "Medium",
            "type": "Task",
            "assignee": "John Doe",
            "created": "2026-03-01",
            "updated": "2026-03-05"
        },
        {
            "key": "PRODENGG-7374",
            "summary": "Remove the private subnet attached to the load balancer for the ephemeral to access the service from local",
            "status": "To Do",
            "priority": "High",
            "type": "Task",
            "assignee": "Jane Smith",
            "created": "2026-03-02",
            "updated": "2026-03-02"
        },
        {
            "key": "PRODENGG-7375",
            "summary": "Explore to scale the istio grpc dynamically",
            "status": "To Do",
            "priority": "Medium",
            "type": "Story",
            "assignee": "Bob Wilson",
            "created": "2026-03-02",
            "updated": "2026-03-02"
        },
        {
            "key": "PRODENGG-7376",
            "summary": "Replicas are reaching max due to cpu optimisation cron",
            "status": "Done",
            "priority": "High",
            "type": "Bug",
            "assignee": "Alice Brown",
            "created": "2026-03-03",
            "updated": "2026-03-06"
        },
        {
            "key": "PRODENGG-7377",
            "summary": "Sync the gateguard code and add the logs for the better debugging",
            "status": "To Do",
            "priority": "Medium",
            "type": "Task",
            "assignee": "Charlie Davis",
            "created": "2026-03-03",
            "updated": "2026-03-03"
        },
        {
            "key": "PRODENGG-7378",
            "summary": "Debug the alert gatekeeper--CPUUtilization--Critical",
            "status": "Done",
            "priority": "Critical",
            "type": "Bug",
            "assignee": "Eve Martinez",
            "created": "2026-03-04",
            "updated": "2026-03-05"
        },
        {
            "key": "PRODENGG-7379",
            "summary": "Limit the access for the quartz bastion for the RoCK Admin role",
            "status": "To Do",
            "priority": "High",
            "type": "Task",
            "assignee": "Frank Lee",
            "created": "2026-03-05",
            "updated": "2026-03-05"
        }
    ]
}

print("=" * 70)
print("CONFLUENCE OUTPUT PREVIEW - TRM AI Tickets")
print("=" * 70)
print()

# Generate the HTML section
html_output = confluence._build_ticket_section(mock_ticket_data, "Mar 2 to Mar 8")

print("HTML Output:")
print("-" * 70)
print(html_output)
print()

print("=" * 70)
print("HOW IT WILL LOOK IN CONFLUENCE:")
print("=" * 70)
print()
print("TRM AI Tickets")
print("-" * 70)
print()

for ticket in mock_ticket_data['tickets']:
    print(f"{ticket['key']}: {ticket['summary']}")
    print(f"{ticket['status']}")
    print()

print("=" * 70)
print("✅ This is the format that will appear in your Confluence page!")
print("=" * 70)
