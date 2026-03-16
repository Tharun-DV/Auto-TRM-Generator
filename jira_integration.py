"""
Jira Integration Module for TRM Reports

This module handles fetching tickets from Jira for inclusion in TRM reports.
Uses the jira Python library for reliable API access.
"""

import os
from jira import JIRA
from datetime import datetime, timedelta
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
        self._jira_client = None
        
        if not self.enabled:
            print("⚠️  Jira integration not configured. Set JIRA_URL, JIRA_USER, JIRA_API_TOKEN, and JIRA_PROJECT_KEYS to enable.")
    
    def _get_jira_client(self):
        """Get or create Jira client."""
        if self._jira_client is None:
            self._jira_client = JIRA(
                server=self.jira_url,
                basic_auth=(self.jira_user, self.jira_api_token),
                options={'verify': False}
            )
        return self._jira_client
    
    def fetch_tickets_for_metrics(self, start_date: str, end_date: str) -> Dict:
        """
        Fetch tickets for metrics calculation (lighter data, counts only).
        
        Args:
            start_date: Start date in format "YYYY-MM-DD"
            end_date: End date in format "YYYY-MM-DD"
        
        Returns:
            dict: {"total": int, "by_status": {}, "by_priority": {}, "p1_count": int, "s1_rcas": int}
        """
        if not self.enabled:
            print("❌ Jira not configured. Skipping metrics fetch.")
            return {"total": 0, "by_status": {}, "by_priority": {}, "p1_count": 0, "s1_rcas": 0}
        
        try:
            print(f"📊 Fetching metrics data from {start_date} to {end_date}")
            
            jira_client = self._get_jira_client()
            project_filter = " OR ".join([f'project = "{key}"' for key in self.jira_project_keys])
            
            jql = f'({project_filter}) AND (created >= "{start_date}" OR updated >= "{start_date}") AND (created <= "{end_date} 23:59" OR updated <= "{end_date} 23:59")'
            
            # Fetch minimal data for metrics
            issues = jira_client.search_issues(jql, maxResults=1000, fields="priority,status,issuetype,summary,labels")
            
            by_status = {}
            by_priority = {}
            p1_count = 0
            s1_rcas = 0
            
            for issue in issues:
                status = issue.fields.status.name
                priority = issue.fields.priority.name if issue.fields.priority else "Unassigned"
                issue_type = issue.fields.issuetype.name.lower()
                summary = issue.fields.summary.lower()
                labels = [label.lower() for label in issue.fields.labels] if issue.fields.labels else []
                
                by_status[status] = by_status.get(status, 0) + 1
                by_priority[priority] = by_priority.get(priority, 0) + 1
                
                # Count P1 tickets
                if priority in ["P1", "Highest", "Critical"]:
                    p1_count += 1
                
                # Count S1 RCAs (Root Cause Analysis)
                if ("rca" in summary or "root cause" in summary or "postmortem" in summary or 
                    "s1" in labels or "rca" in labels or any("rca" in label for label in labels)):
                    s1_rcas += 1
            
            return {
                "total": len(issues),
                "by_status": by_status,
                "by_priority": by_priority,
                "p1_count": p1_count,
                "s1_rcas": s1_rcas
            }
            
        except Exception as e:
            print(f"❌ Error fetching metrics data: {e}")
            return {"total": 0, "by_status": {}, "by_priority": {}, "p1_count": 0, "s1_rcas": 0}

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
            
            jira_client = self._get_jira_client()
            
            project_filter = " OR ".join([f'project = "{key}"' for key in self.jira_project_keys])
            
            jql = f'({project_filter}) AND (created >= "{start_date}" OR updated >= "{start_date}") AND (created <= "{end_date} 23:59" OR updated <= "{end_date} 23:59")'
            
            print(f"🔍 JQL Query: {jql}")
            print(f"🔍 Date Range: {start_date} to {end_date}")
            print(f"🔍 Projects: {self.jira_project_keys}")
            
            # Test the query first to understand what Jira sees
            print(f"🧪 Testing query without pagination...")
            test_result = jira_client.search_issues(jql, maxResults=1)
            print(f"🔍 Jira reports total available: {test_result.total}")
            
            if test_result.total <= 100:
                print(f"⚠️  WARNING: Only {test_result.total} tickets found!")
                print(f"🔍 Debugging query components...")
                
                # Test individual components
                created_only_jql = f'({project_filter}) AND created >= "{start_date}" AND created <= "{end_date} 23:59"'
                updated_only_jql = f'({project_filter}) AND updated >= "{start_date}" AND updated <= "{end_date} 23:59"'
                
                created_result = jira_client.search_issues(created_only_jql, maxResults=1)
                updated_result = jira_client.search_issues(updated_only_jql, maxResults=1)
                
                print(f"   📊 Created only: {created_result.total} tickets")
                print(f"   📊 Updated only: {updated_result.total} tickets")
                print(f"   📊 Combined (OR): {test_result.total} tickets")
                
                # Test without date filter
                no_date_jql = f'({project_filter})'
                no_date_result = jira_client.search_issues(no_date_jql, maxResults=1)
                print(f"   📊 All project tickets: {no_date_result.total}")
            
            all_tickets = []
            start_at = 0
            max_results = 100
            total_available = None
            max_pages = 50  # Safety limit: 5000 tickets max
            current_page = 0
            
            while current_page < max_pages:
                current_page += 1
                print(f"🔄 Fetching page {current_page}: startAt={start_at}, maxResults={max_results}")
                issues = jira_client.search_issues(jql, startAt=start_at, maxResults=max_results)
                
                if start_at == 0:
                    total_available = issues.total
                    print(f"🔍 Total issues available: {total_available}")
                
                current_batch_size = len(issues)
                print(f"📦 Received {current_batch_size} issues in this batch")
                
                if current_batch_size == 0:
                    print("🛑 No more issues to fetch")
                    break
                
                all_tickets.extend(issues)
                start_at += max_results
                
                print(f"📊 Progress: {len(all_tickets)}/{total_available} tickets fetched")
                
                if len(issues) < max_results or (total_available and start_at >= total_available):
                    print(f"✅ Reached end of results (batch size: {len(issues)}, expected: {max_results})")
                    break
            
            if current_page >= max_pages:
                print(f"⚠️ Reached maximum page limit ({max_pages}). Fetched {len(all_tickets)} tickets.")
            
            # Auto-retry with broader query if we got very few tickets
            if total_available and total_available <= 50 and len(all_tickets) == total_available:
                print(f"🔄 Too few tickets ({total_available}), trying broader query...")
                
                from datetime import datetime, timedelta
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                
                # Extend range by 3 days on each side
                broader_start = (start_date_obj - timedelta(days=3)).strftime("%Y-%m-%d")
                broader_end = (end_date_obj + timedelta(days=3)).strftime("%Y-%m-%d")
                
                broader_jql = f'({project_filter}) AND (created >= "{broader_start}" OR updated >= "{broader_start}") AND (created <= "{broader_end} 23:59" OR updated <= "{broader_end} 23:59")'
                print(f"🔍 Broader JQL: {broader_jql}")
                
                broader_test = jira_client.search_issues(broader_jql, maxResults=1)
                print(f"📊 Broader range found: {broader_test.total} tickets")
                
                if broader_test.total > total_available * 2:  # Significant increase
                    print(f"💡 RECOMMENDATION: Your date range might be too narrow.")
                    print(f"   Original range: {start_date} to {end_date} = {total_available} tickets")
                    print(f"   Broader range: {broader_start} to {broader_end} = {broader_test.total} tickets")
                    print(f"   Consider using: {broader_start} to {broader_end} for more comprehensive TRM data")
            
            print(f"✅ Fetched {len(all_tickets)} tickets from Jira (Expected: {total_available})")
            
            if total_available and total_available <= 100:
                print(f"🤔 ANALYSIS: Only {total_available} tickets found - this seems low for a week's activity.")
                print(f"💡 SUGGESTIONS:")
                print(f"   1. Check if date range '{start_date}' to '{end_date}' is correct")
                print(f"   2. Verify JIRA_PROJECT_KEYS='{','.join(self.jira_project_keys)}' includes active projects")
                print(f"   3. Consider if this is a holiday/low-activity week")
                print(f"   4. Check if there are permission restrictions on ticket visibility")
            
            if total_available and len(all_tickets) < total_available:
                print(f"⚠️ WARNING: Fetched fewer tickets than expected!")
                print(f"   Expected: {total_available}")
                print(f"   Actually fetched: {len(all_tickets)}")
                print(f"   Missing: {total_available - len(all_tickets)} tickets")
            elif total_available and len(all_tickets) == total_available:
                print(f"✅ Successfully fetched ALL {len(all_tickets)} tickets!")
            
            if all_tickets:
                first = all_tickets[0]
                print(f"🔍 First ticket: {first.key}: {first.fields.summary[:50]}")
            
            return self._process_tickets(all_tickets)
            
        except Exception as e:
            print(f"❌ Error fetching Jira tickets: {e}")
            return self._empty_result()
    
    def _process_tickets(self, tickets: List) -> Dict:
        """Process and categorize tickets."""
        by_status = {}
        by_priority = {}
        by_type = {}
        by_tech = {}
        processed_tickets = []
        
        for issue in tickets:
            custom_field_value = getattr(issue.fields, "customfield_14604", None)
            if custom_field_value:
                tech_value = custom_field_value.value if hasattr(custom_field_value, "value") else str(custom_field_value)
            else:
                tech_value = ""
            
            ticket_data = {
                "key": issue.key,
                "summary": issue.fields.summary,
                "status": issue.fields.status.name,
                "priority": issue.fields.priority.name if issue.fields.priority else "Unassigned",
                "type": issue.fields.issuetype.name,
                "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
                "created": issue.fields.created,
                "updated": issue.fields.updated,
                "tech": tech_value
            }
            
            processed_tickets.append(ticket_data)
            
            by_status[ticket_data["status"]] = by_status.get(ticket_data["status"], 0) + 1
            by_priority[ticket_data["priority"]] = by_priority.get(ticket_data["priority"], 0) + 1
            by_type[ticket_data["type"]] = by_type.get(ticket_data["type"], 0) + 1
            
            if tech_value:
                by_tech[tech_value] = by_tech.get(tech_value, 0) + 1
        
        return {
            "total": len(processed_tickets),
            "by_status": by_status,
            "by_priority": by_priority,
            "by_type": by_type,
            "by_tech": by_tech,
            "tickets": processed_tickets
        }
    
    def _empty_result(self) -> Dict:
        """Return empty result structure."""
        return {
            "total": 0,
            "by_status": {},
            "by_priority": {},
            "by_type": {},
            "by_tech": {},
            "tickets": []
        }


jira = JiraIntegration()
