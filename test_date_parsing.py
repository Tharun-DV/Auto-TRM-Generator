#!/usr/bin/env python3
"""
Test date parsing for TRM bot
"""

import sys
import os
sys.path.insert(0, '/Users/tharun.dv_int/src/tries/Auto-TRM-Generator')

from dotenv import load_dotenv
load_dotenv()

from datetime import datetime, timedelta
import re
import dateparser

def parse_date_range(text: str):
    """Parse user input like 'Feb 25 to Mar 4 2026' or 'week 8' into Unix timestamps."""
    text = text.strip().lower()
    
    # Handle "last week" - return full week range (Monday to Sunday)
    if text in ['last week', 'lastweek', 'previous week']:
        today = datetime.now()
        # Get Monday of last week
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday + 7)
        start_date = last_monday.replace(hour=0, minute=0, second=0, microsecond=0)
        # Get Sunday of last week
        end_date = start_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
        week_num = start_date.isocalendar()[1]
        return start_date.timestamp(), end_date.timestamp(), start_date.strftime("%b %d"), end_date.strftime("%b %d"), week_num
    
    # Handle "this week" - return full week range (Monday to Sunday)
    if text in ['this week', 'thisweek', 'current week']:
        today = datetime.now()
        # Get Monday of this week
        days_since_monday = today.weekday()
        this_monday = today - timedelta(days=days_since_monday)
        start_date = this_monday.replace(hour=0, minute=0, second=0, microsecond=0)
        # Get Sunday of this week
        end_date = start_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
        week_num = start_date.isocalendar()[1]
        return start_date.timestamp(), end_date.timestamp(), start_date.strftime("%b %d"), end_date.strftime("%b %d"), week_num
    
    # Handle "week N" format
    week_match = re.match(r'week\s+(\d+)', text, re.IGNORECASE)
    if week_match:
        week_num = int(week_match.group(1))
        # Calculate week dates (assuming week 1 starts on Jan 1)
        year = datetime.now().year
        start_date = datetime(year, 1, 1) + timedelta(weeks=week_num - 1)
        # Adjust to Monday if Jan 1 is not Monday
        days_to_monday = (7 - start_date.weekday()) % 7
        if start_date.weekday() != 0:  # If not Monday
            start_date = start_date + timedelta(days=days_to_monday)
        end_date = start_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
        return start_date.timestamp(), end_date.timestamp(), start_date.strftime("%b %d"), end_date.strftime("%b %d"), week_num
    
    # Handle "date to date" format
    parts = re.split(r'\s+to\s+', text, flags=re.IGNORECASE)
    if len(parts) == 2:
        start_date = dateparser.parse(parts[0].strip())
        end_date = dateparser.parse(parts[1].strip())
        
        if start_date and end_date:
            # Set start date to beginning of day
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            # Set end date to end of day
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            week_num = start_date.isocalendar()[1]
            return start_date.timestamp(), end_date.timestamp(), start_date.strftime("%b %d"), end_date.strftime("%b %d"), week_num
    
    # Try to parse as a single date (for "yesterday", specific dates, etc.)
    parsed = dateparser.parse(text)
    if parsed:
        start_date = parsed.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = parsed.replace(hour=23, minute=59, second=59, microsecond=999999)
        week_num = start_date.isocalendar()[1]
        return start_date.timestamp(), end_date.timestamp(), start_date.strftime("%b %d"), end_date.strftime("%b %d"), week_num
    
    raise ValueError(f"Could not parse date range from: {text}")


print("=" * 70)
print("Testing Date Parsing")
print("=" * 70)
print()

test_inputs = [
    "last week",
    "this week",
    "week 8",
    "yesterday",
    "Feb 24 to Mar 2 2026",
    "March 1"
]

for test_input in test_inputs:
    try:
        oldest, latest, start_str, end_str, week_num = parse_date_range(test_input)
        start_dt = datetime.fromtimestamp(oldest)
        end_dt = datetime.fromtimestamp(latest)
        
        print(f"✅ Input: '{test_input}'")
        print(f"   Week: {week_num}")
        print(f"   Range: {start_str} to {end_str}")
        print(f"   Full dates: {start_dt.strftime('%Y-%m-%d %H:%M')} to {end_dt.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Duration: {(end_dt - start_dt).days + 1} days")
        print()
    except Exception as e:
        print(f"❌ Input: '{test_input}'")
        print(f"   Error: {e}")
        print()

print("=" * 70)
print("Today's date:", datetime.now().strftime("%Y-%m-%d (Week %V)"))
print("=" * 70)
