"""
Jira Integration Module for TRM Reports

This module handles fetching tickets from Jira for inclusion in TRM reports.
"""

import os
import requests
from datetime import datetime
from typing import Dict, List, Optional


class JiraIntegration:
    """Handle Jira ticket fetching for TRM reports."""
    
    def __init__(self):
        """Initialize Jira client with credentials from environment."""
        self.jira_url = os.environ.get("JIRA_URL")
        self.jira_user = os.environ.get("JIRA_USER")
        self.jira_api_token = os.environ.get("JIRA_API_TOKEN")
        self.jira_project_keys = os.environ.get("JIRA_PROJECT_KEYS", "").split(",")
        self.jira_project_keys = [key.strip() for key in self.jira_project_keys if key.strip()]
        
        self.enabled = all([self.jira_url, self.jira_user, self.jira_api_token, self.jira_project_keys])
        
        if not self.enabled:
            print("⚠️  Jira integration not configured. Set JIRA_URL, JIRA_USER, JIRA_API_TOKEN, and JIRA_PROJECT_KEYS to enable.")
    
    def fetch_tickets(self, start_date: str, end_date: str) -> Dict:
        """
        Fetch tickets from Jira within the specified date range.
        
        Args:
            start_date: Start date in format "YYYY-MM-DD"
            end_date: End date in format "YYYY-MM-DD"
        
        Returns:
            dict: {
                "total": int,
                "by_status": {"Open": 5, "Closed": 10, ...},
                "by_priority": {"P1": 3, "P2": 7, ...},
                "by_type": {"Bug": 5, "Task": 8, ...},
                "tickets": [{"key": "DEV-123", "summary": "...", ...}]
            }
        """
        if not self.enabled:
            print("❌ Jira not configured. Skipping ticket fetch.")
            return self._empty_result()
        
        try:
            print(f"🎫 Fetching Jira tickets from {start_date} to {end_date}")
            print(f"🔍 Projects: {', '.join(self.jira_project_keys)}")
            print(f"🔍 Jira URL: {self.jira_url}")
            print(f"🔍 Jira User: {self.jira_user}")
            
            # Test with simple JQL first (no date filter) to verify project key works
            # Project keys might need quotes in JQL
            project_filter = " OR ".join([f'project = "{key}"' for key in self.jira_project_keys])
            
            # Try simple query first
            simple_jql = f'project = "{self.jira_project_keys[0]}" ORDER BY created DESC'
            print(f"🔍 Testing simple JQL: {simple_jql}")
            
            url = f"{self.jira_url}/rest/api/3/search/jql"
            payload = {
                "jql": simple_jql,
                "maxResults": 5,
                "fields": ["key", "summary", "created", "updated"]
            }
            
            response = requests.post(
                url,
                auth=(self.jira_user, self.jira_api_token),
                headers={"Accept": "application/json", "Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                test_tickets = result.get("issues", [])
                print(f"🔍 Simple query result: {len(test_tickets)} tickets")
                if test_tickets:
                    for t in test_tickets:
                        fields = t.get("fields", {})
                        print(f"  - {t.get('key')}: created={fields.get('created')}, updated={fields.get('updated')}")
            
            # Build JQL query - search by created OR updated date (with proper parentheses for OR)
            # Add 1 day to end_date to include the full end day
            from datetime import datetime, timedelta
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            end_date_inclusive = end_date_obj.strftime("%Y-%m-%d")
            
            jql = f"({project_filter}) AND ((created >= '{start_date}' AND created < '{end_date_inclusive}') OR (updated >= '{start_date}' AND updated < '{end_date_inclusive}'))"
            
            print(f"🔍 JQL: {jql}")
            
            # Fetch tickets from Jira using the new search/jql endpoint
            url = f"{self.jira_url}/rest/api/3/search/jql"
            
            payload = {
                "jql": jql,
                "maxResults": 1000,
                "fields": ["key", "summary", "status", "priority", "issuetype", "created", "updated", "assignee", "reporter"]
            }
            
            response = requests.post(
                url,
                auth=(self.jira_user, self.jira_api_token),
                headers={"Accept": "application/json", "Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            
            print(f"🔍 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                tickets = result.get("issues", [])
                
                print(f"✅ Fetched {len(tickets)} tickets from Jira")
                
                # Debug: print first ticket if any
                if tickets:
                    print(f"🔍 First ticket: {tickets[0].get('key')}: {tickets[0].get('fields', {}).get('summary', '')[:50]}")
                
                # Process and categorize tickets
                return self._process_tickets(tickets)
            else:
                print(f"❌ Failed to fetch Jira tickets: {response.status_code} - {response.text}")
                return self._empty_result()
                
        except Exception as e:
            print(f"❌ Error fetching Jira tickets: {e}")
            return self._empty_result()
    
    def _process_tickets(self, tickets: List[Dict]) -> Dict:
        """Process and categorize tickets."""
        by_status = {}
        by_priority = {}
        by_type = {}
        processed_tickets = []
        
        for issue in tickets:
            fields = issue.get("fields", {})
            
            # Extract ticket info
            ticket_data = {
                "key": issue.get("key", ""),
                "summary": fields.get("summary", ""),
                "status": fields.get("status", {}).get("name", "Unknown"),
                "priority": fields.get("priority", {}).get("name", "Unassigned"),
                "type": fields.get("issuetype", {}).get("name", "Unknown"),
                "assignee": fields.get("assignee", {}).get("displayName", "Unassigned") if fields.get("assignee") else "Unassigned",
                "created": fields.get("created", ""),
                "updated": fields.get("updated", "")
            }
            
            processed_tickets.append(ticket_data)
            
            # Count by status
            status = ticket_data["status"]
            by_status[status] = by_status.get(status, 0) + 1
            
            # Count by priority
            priority = ticket_data["priority"]
            by_priority[priority] = by_priority.get(priority, 0) + 1
            
            # Count by type
            ticket_type = ticket_data["type"]
            by_type[ticket_type] = by_type.get(ticket_type, 0) + 1
        
        return {
            "total": len(processed_tickets),
            "by_status": by_status,
            "by_priority": by_priority,
            "by_type": by_type,
            "tickets": processed_tickets
        }
    
    def _empty_result(self) -> Dict:
        """Return empty result structure."""
        return {
            "total": 0,
            "by_status": {},
            "by_priority": {},
            "by_type": {},
            "tickets": []
        }


# Global instance
jira = JiraIntegration()
