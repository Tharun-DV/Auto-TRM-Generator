#!/usr/bin/env python3
"""
Debug script to diagnose Jira ticket fetching issues.
Run this to understand why you're only getting 100 tickets.
"""

import os
from jira_integration import JiraIntegration

def debug_jira_query(start_date="2024-03-08", end_date="2024-03-14"):
    """Debug Jira queries to understand ticket count limitations."""
    
    print("🔍 JIRA DEBUGGING TOOL")
    print("=" * 50)
    
    # Check environment
    required_vars = ["JIRA_URL", "JIRA_USER", "JIRA_API_TOKEN", "JIRA_PROJECT_KEYS"]
    missing = [var for var in required_vars if not os.environ.get(var)]
    
    if missing:
        print(f"❌ Missing environment variables: {missing}")
        print("Please set them first:")
        for var in missing:
            print(f"   export {var}='your-value'")
        return
    
    jira = JiraIntegration()
    if not jira.enabled:
        print("❌ Jira integration not properly configured")
        return
    
    print(f"✅ Jira configured: {jira.jira_url}")
    print(f"📋 Projects: {jira.jira_project_keys}")
    print(f"📅 Date range: {start_date} to {end_date}")
    print()
    
    try:
        jira_client = jira._get_jira_client()
        project_filter = " OR ".join([f'project = "{key}"' for key in jira.jira_project_keys])
        
        # Test different query variations
        queries = {
            "Original (created only)": f'({project_filter}) AND created >= "{start_date}" AND created <= "{end_date} 23:59"',
            "Updated only": f'({project_filter}) AND updated >= "{start_date}" AND updated <= "{end_date} 23:59"',
            "Created OR Updated (current)": f'({project_filter}) AND (created >= "{start_date}" OR updated >= "{start_date}") AND (created <= "{end_date} 23:59" OR updated <= "{end_date} 23:59")',
            "No date filter": f'({project_filter})',
            "Last 30 days": f'({project_filter}) AND updated >= "-30d"'
        }
        
        print("🧪 TESTING DIFFERENT QUERIES:")
        print("-" * 50)
        
        for name, jql in queries.items():
            try:
                result = jira_client.search_issues(jql, maxResults=1)
                print(f"{name:25} | {result.total:6d} tickets | {jql[:60]}...")
            except Exception as e:
                print(f"{name:25} | ERROR  | {str(e)[:50]}...")
        
        print()
        
        # Recommend next steps
        current_jql = queries["Created OR Updated (current)"]
        current_result = jira_client.search_issues(current_jql, maxResults=1)
        
        if current_result.total <= 100:
            print("🚨 DIAGNOSIS: Low ticket count detected")
            print("💡 POSSIBLE CAUSES:")
            print("   1. Date range too narrow (only 7 days)")
            print("   2. Low activity week (holidays, etc.)")
            print("   3. Wrong project keys")
            print("   4. Permission restrictions")
            print()
            print("🛠️  SOLUTIONS TO TRY:")
            print("   1. Extend date range: Use last 14-30 days instead of 7")
            print("   2. Check project activity on Jira web interface")
            print("   3. Verify project keys in JIRA_PROJECT_KEYS")
            print("   4. Test with admin account to check permissions")
        else:
            print("✅ Query looks good! Fetching full dataset...")
            result = jira.fetch_tickets(start_date, end_date)
            print(f"Final result: {result['total']} tickets")
            
    except Exception as e:
        print(f"❌ Error during debugging: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3:
        debug_jira_query(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python debug_jira.py 2024-03-08 2024-03-14")
        print("Or just run with default dates:")
        debug_jira_query()