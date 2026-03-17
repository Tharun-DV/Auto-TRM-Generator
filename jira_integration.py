"""
Jira Integration Module for TRM Reports

This module handles fetching tickets from Jira for inclusion in TRM reports.
Uses the jira Python library for reliable API access.
"""

import os
import requests
from jira import JIRA
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Disable SSL warnings for self-signed certs
requests.packages.urllib3.disable_warnings()


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
    
    def _fetch_tickets_raw_api(self, jql: str, max_results: int = 1000) -> tuple:
        """
        Fetch tickets using raw REST API to bypass library limitations.
        Returns (total_count, list_of_issues).
        """
        url = f"{self.jira_url}/rest/api/2/search"
        
        all_issues = []
        start_at = 0
        
        while True:
            params = {
                "jql": jql,
                "startAt": start_at,
                "maxResults": max_results,
                "fields": "summary,status,priority,issuetype,created,updated,assignee,labels"
            }
            
            response = requests.get(
                url,
                params=params,
                auth=(self.jira_user, self.jira_api_token),
                verify=False
            )
            
            if response.status_code != 200:
                print(f"❌ API error: {response.status_code} - {response.text[:200]}")
                break
            
            data = response.json()
            total = data.get("total", 0)
            issues = data.get("issues", [])
            
            if start_at == 0:
                print(f"🔍 Raw API reports total: {total} tickets")
            
            all_issues.extend(issues)
            
            if len(issues) < max_results or start_at + len(issues) >= total:
                break
            
            start_at += max_results
            print(f"📊 Progress: {len(all_issues)}/{total} fetched via raw API")
        
        return len(all_issues), all_issues
    
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
            
            # Fetch all data for metrics using maxResults=False for automatic pagination
            issues = jira_client.search_issues(jql, maxResults=False, fields="priority,status,issuetype,summary,labels")
            print(f"📊 Fetched {len(issues)} tickets for metrics")
            
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
            
            # Use maxResults=False to automatically fetch ALL tickets
            # This is the magic fix - library handles pagination internally
            print(f"🚀 Using maxResults=False for automatic full fetch...")
            print(f"🔄 Fetching all tickets (this may take a moment for large datasets)...")
            
            all_tickets = jira_client.search_issues(jql, maxResults=False)
            
            print(f"✅ Successfully fetched {len(all_tickets)} tickets!")
            
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
