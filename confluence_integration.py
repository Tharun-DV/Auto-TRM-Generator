"""
Confluence Integration Module for TRM Reports

This module handles creating Confluence pages with TRM report data.
"""

import os
import requests
import json
from typing import Dict, List, Optional


class ConfluenceIntegration:
    """Handle Confluence page creation for TRM reports."""
    
    def __init__(self):
        """Initialize Confluence client with credentials from environment."""
        self.confluence_url = os.environ.get("CONFLUENCE_URL")
        self.confluence_user = os.environ.get("CONFLUENCE_USER")  # Email
        self.confluence_api_token = os.environ.get("CONFLUENCE_API_TOKEN")
        self.confluence_space_key = os.environ.get("CONFLUENCE_SPACE_KEY", "DEVOPS")
        self.confluence_parent_id = os.environ.get("CONFLUENCE_PARENT_ID")  # Optional
        
        self.enabled = all([self.confluence_url, self.confluence_user, self.confluence_api_token])
        
        if not self.enabled:
            print("⚠️  Confluence integration not configured. Set CONFLUENCE_URL, CONFLUENCE_USER, and CONFLUENCE_API_TOKEN to enable.")
    
    def create_trm_page(self, metadata: Dict, data: Dict) -> Optional[str]:
        """
        Create a Confluence page with TRM report data.
        
        Args:
            metadata: Week number, date range, oncall name
            data: Issues, alerts, outages, etc.
        
        Returns:
            str: URL of created page, or None if failed
        """
        if not self.enabled:
            print("❌ Confluence not configured. Skipping page creation.")
            return None
        
        try:
            # Build page content
            page_title = f"TRM Report - Week {metadata['week_number']} ({metadata['date_range']})"
            page_content = self._build_confluence_content(metadata, data)
            
            # Create page via Confluence REST API
            url = f"{self.confluence_url}/rest/api/content"
            
            payload = {
                "type": "page",
                "title": page_title,
                "space": {"key": self.confluence_space_key},
                "body": {
                    "storage": {
                        "value": page_content,
                        "representation": "storage"
                    }
                }
            }
            
            # Add parent if specified
            if self.confluence_parent_id:
                payload["ancestors"] = [{"id": self.confluence_parent_id}]
            
            response = requests.post(
                url,
                auth=(self.confluence_user, self.confluence_api_token),
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                page_url = f"{self.confluence_url}{result['_links']['webui']}"
                print(f"✅ Confluence page created: {page_url}")
                return page_url
            else:
                print(f"❌ Failed to create Confluence page: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating Confluence page: {e}")
            return None
    
    def _build_confluence_content(self, metadata: Dict, data: Dict) -> str:
        """Build Confluence HTML content from TRM data."""
        
        # Build issues table
        issues_rows = ""
        themes = {"Compute": [], "Infrasec": [], "Haproxy": [], "Latency": [], "Alerting": [], "Logging": []}
        
        for issue in data["issues"]:
            theme = issue["theme"]
            if theme in themes:
                themes[theme].append(issue["description"])
        
        for theme, descriptions in themes.items():
            if descriptions:
                issues_rows += f"<tr><td><strong>{theme}</strong></td><td>{'; '.join(descriptions)}</td></tr>"
            else:
                issues_rows += f"<tr><td><strong>{theme}</strong></td><td>None</td></tr>"
        
        # Build metrics table
        metrics_rows = ""
        if data["metrics"]:
            metrics = data["metrics"][0]
            metrics_rows = f"""
            <tr><td>1</td><td>P1 Alerts</td><td>{metrics['p1_alerts']}</td></tr>
            <tr><td>2</td><td>Infra sec P0</td><td>{metrics['infrasec_p0']}</td></tr>
            <tr><td>3</td><td>S1 RCAs</td><td>{metrics['s1_rcas']}</td></tr>
            <tr><td>4</td><td>S2/S3 RCAs</td><td>{metrics['s23_rcas']}</td></tr>
            """
        else:
            metrics_rows = """
            <tr><td>1</td><td>P1 Alerts</td><td>0</td></tr>
            <tr><td>2</td><td>Infra sec P0</td><td>0</td></tr>
            <tr><td>3</td><td>S1 RCAs</td><td>0</td></tr>
            <tr><td>4</td><td>S2/S3 RCAs</td><td>0</td></tr>
            """
        
        # Build alerts table
        alerts_rows = ""
        if data["alerts"]:
            for alert in data["alerts"]:
                alerts_rows += f"<tr><td>{alert['component']}</td><td>{alert['alert_name']}</td><td>{alert['frequency']}</td><td>{alert['description']}</td></tr>"
        else:
            alerts_rows = "<tr><td colspan='4'><em>No alerts reported</em></td></tr>"
        
        # Build cost table
        cost_rows = ""
        if data["cost"]:
            for cost in data["cost"]:
                cost_rows += f"<tr><td>{cost['resource']}</td><td>{cost['last_week_cost']}</td><td>{cost['this_week_cost']}</td></tr>"
        else:
            cost_rows = "<tr><td colspan='3'><em>No cost data mentioned</em></td></tr>"
        
        # Build outages table
        outages_rows = ""
        if data["outages"]:
            for outage in data["outages"]:
                outages_rows += f"<tr><td>{outage['outage_name']}</td><td>{outage['severity']}</td><td>{outage['reason']}</td><td>{outage['owner']}</td><td>{outage['date']}</td></tr>"
        else:
            outages_rows = "<tr><td colspan='5'><em>No outages reported</em></td></tr>"
        
        # Build action items table
        action_items_rows = ""
        if data["action_items"]:
            for ai in data["action_items"]:
                action_items_rows += f"<tr><td>{ai['description']}</td><td>{ai['owner']}</td><td>{ai['eta']}</td></tr>"
        else:
            action_items_rows = "<tr><td colspan='3'><em>No action items</em></td></tr>"
        
        # Complete HTML content
        html_content = f"""
<h1>📋 ProdEngg TRM — Week {metadata['week_number']} | {metadata['date_range']}</h1>
<p><strong>DevOps Oncall:</strong> {metadata['oncall']}</p>
<hr/>

<h2>🔴 Issues</h2>
<table>
<tbody>
<tr><th>Theme/Vertical</th><th>Description</th></tr>
{issues_rows}
</tbody>
</table>

<h2>📊 P0 Metrics</h2>
<table>
<tbody>
<tr><th>#</th><th>Metric</th><th>Value</th></tr>
{metrics_rows}
</tbody>
</table>

<h2>🚨 Alerts Summary</h2>
<table>
<tbody>
<tr><th>Component</th><th>Alert</th><th>Frequency</th><th>Description</th></tr>
{alerts_rows}
</tbody>
</table>

<h2>💰 Cost Highlights</h2>
<table>
<tbody>
<tr><th>Resource</th><th>Last Week</th><th>This Week</th></tr>
{cost_rows}
</tbody>
</table>

<h2>🔥 Outages Summary</h2>
<table>
<tbody>
<tr><th>Outage/RCA</th><th>Severity</th><th>Reason</th><th>Owner</th><th>Date</th></tr>
{outages_rows}
</tbody>
</table>

<h2>🎫 Ticket Data</h2>
<ul>
<li>Total Tickets: Not specified</li>
<li>Date Range: {metadata['date_range']}</li>
<li>Status: Closed: 0 | Blocked: 0 | Open: 0</li>
</ul>

<h2>✅ Action Items (TRM AIs)</h2>
<table>
<tbody>
<tr><th>Description</th><th>Owner</th><th>ETA</th></tr>
{action_items_rows}
</tbody>
</table>
"""
        
        return html_content


# Global instance
confluence = ConfluenceIntegration()
