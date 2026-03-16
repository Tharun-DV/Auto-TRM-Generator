"""
Confluence Integration Module for TRM Reports

This module handles creating Confluence pages with TRM report data.
"""

import os
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime


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
    
    def create_trm_page(self, metadata: Dict, data: Dict, ticket_data: Optional[Dict] = None) -> Optional[str]:
        """
        Create a Confluence page with TRM report data.
        
        Args:
            metadata: Week number, date range, oncall name
            data: Issues, alerts, outages, etc.
            ticket_data: Jira ticket data (optional)
        
        Returns:
            str: URL of created page, or None if failed
        """
        if not self.enabled:
            print("❌ Confluence not configured. Skipping page creation.")
            return None
        
        try:
            # Build page content
            page_title = f"TRM Report - Week {metadata['week_number']} ({metadata['date_range']})"
            page_content = self._build_confluence_content(metadata, data, ticket_data)
            
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
    
    def _build_confluence_content(self, metadata: Dict, data: Dict, ticket_data: Optional[Dict] = None) -> str:
        """Build Confluence HTML content from TRM data."""
        
        # Build issues table - support dynamic themes
        issues_rows = ""
        themes_dict = {}
        
        for issue in data["issues"]:
            theme = issue["theme"]
            if theme not in themes_dict:
                themes_dict[theme] = []
            themes_dict[theme].append(issue["description"])
        
        for theme, descriptions in sorted(themes_dict.items()):
            issues_rows += f"<tr><td style='padding: 12px; background: #fff2f0; border-bottom: 1px solid #ffebe6;'><strong style='color: #de350b;'>{theme}</strong></td><td style='padding: 12px; border-bottom: 1px solid #ffebe6;'>{'; '.join(descriptions)}</td></tr>"
        
        if not issues_rows:
            issues_rows = "<tr><td colspan='2' style='padding: 15px; text-align: center; font-style: italic; color: #6b778c; background: #f4f5f7;'>No issues reported</td></tr>"
        
        # Build metrics table - new format with Last Week, Current Week, Delta
        metrics_rows = ""
        if data["metrics"]:
            for metric in data["metrics"]:
                delta_text = metric.get('delta', '') or '-'
                metrics_rows += f"<tr><td style='padding: 12px; background: #f0f5ff; border-bottom: 1px solid #deecff;'><strong style='color: #0052cc;'>{metric['metric_name']}</strong></td><td style='padding: 12px; text-align: center; border-bottom: 1px solid #deecff;'>{metric['last_week']}</td><td style='padding: 12px; text-align: center; border-bottom: 1px solid #deecff;'>{metric['current_week']}</td><td style='padding: 12px; border-bottom: 1px solid #deecff;'>{delta_text}</td></tr>"
        else:
            metrics_rows = "<tr><td colspan='4' style='padding: 15px; text-align: center; font-style: italic; color: #6b778c; background: #f4f5f7;'>No metrics added</td></tr>"
        
        # Build alerts table
        alerts_rows = ""
        if data["alerts"]:
            for alert in data["alerts"]:
                alerts_rows += f"<tr><td style='padding: 12px; background: #fff7e6; border-bottom: 1px solid #ffecc2;'>{alert['component']}</td><td style='padding: 12px; border-bottom: 1px solid #ffecc2;'>{alert['alert_name']}</td><td style='padding: 12px; text-align: center; border-bottom: 1px solid #ffecc2;'>{alert['frequency']}</td><td style='padding: 12px; border-bottom: 1px solid #ffecc2;'>{alert['description']}</td></tr>"
        else:
            alerts_rows = "<tr><td colspan='4' style='padding: 15px; text-align: center; font-style: italic; color: #6b778c; background: #f4f5f7;'>No alerts reported</td></tr>"
        
        # Build cost table
        cost_rows = ""
        if data["cost"]:
            for cost in data["cost"]:
                cost_rows += f"<tr><td style='padding: 12px; background: #e3fcef; border-bottom: 1px solid #abf5d1;'>{cost['resource']}</td><td style='padding: 12px; text-align: center; border-bottom: 1px solid #abf5d1;'>{cost['last_week_cost']}</td><td style='padding: 12px; text-align: center; border-bottom: 1px solid #abf5d1;'>{cost['this_week_cost']}</td></tr>"
        else:
            cost_rows = "<tr><td colspan='3' style='padding: 15px; text-align: center; font-style: italic; color: #6b778c; background: #f4f5f7;'>No cost data mentioned</td></tr>"
        
        # Build outages table
        outages_rows = ""
        if data["outages"]:
            for outage in data["outages"]:
                # Use owner_names for Confluence, fall back to owner if not available
                owner_display = outage.get('owner_names', outage.get('owner', ''))
                outages_rows += f"<tr><td style='padding: 12px; background: #eae6ff; border-bottom: 1px solid #c0b6f2;'>{outage['outage_name']}</td><td style='padding: 12px; text-align: center; border-bottom: 1px solid #c0b6f2;'>{outage['severity']}</td><td style='padding: 12px; border-bottom: 1px solid #c0b6f2;'>{outage['reason']}</td><td style='padding: 12px; border-bottom: 1px solid #c0b6f2;'>{owner_display}</td><td style='padding: 12px; text-align: center; border-bottom: 1px solid #c0b6f2;'>{outage['date']}</td></tr>"
        else:
            outages_rows = "<tr><td colspan='5' style='padding: 15px; text-align: center; font-style: italic; color: #6b778c; background: #f4f5f7;'>No outages reported</td></tr>"
        
        # Build action items table
        action_items_rows = ""
        if data["action_items"]:
            for ai in data["action_items"]:
                # Use owner_names for Confluence, fall back to owner if not available
                owner_display = ai.get('owner_names', ai.get('owner', ''))
                action_items_rows += f"<tr><td style='padding: 12px; background: #f4f1ff; border-bottom: 1px solid #ddd6fe;'>{ai['description']}</td><td style='padding: 12px; border-bottom: 1px solid #ddd6fe;'>{owner_display}</td><td style='padding: 12px; text-align: center; border-bottom: 1px solid #ddd6fe;'>{ai['eta']}</td></tr>"
        else:
            action_items_rows = "<tr><td colspan='3' style='padding: 15px; text-align: center; font-style: italic; color: #6b778c; background: #f4f5f7;'>No action items</td></tr>"
        
        # Build ticket data section
        ticket_section = self._build_ticket_section(ticket_data, metadata['date_range'])
        
        # Complete HTML content
        # Use oncall_names for Confluence display, fall back to oncall if not available
        oncall_display = metadata.get('oncall_names', metadata.get('oncall', ''))
        print(f"🔍 DEBUG Confluence: metadata keys = {metadata.keys()}")
        print(f"🔍 DEBUG Confluence: oncall = {metadata.get('oncall')}")
        print(f"🔍 DEBUG Confluence: oncall_names = {metadata.get('oncall_names')}")
        print(f"🔍 DEBUG Confluence: oncall_display = {oncall_display}")
        
        html_content = f"""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 12px; margin-bottom: 30px;">
<h1 style="margin: 0; font-size: 2.2em; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">🔧 ProdEngg TRM — Week {metadata['week_number']}</h1>
<p style="font-size: 1.2em; margin: 10px 0 0 0; opacity: 0.95;">{metadata['date_range']} | <strong>DevOps Oncall:</strong> {oncall_display}</p>
</div>

<ac:structured-macro ac:name="info" ac:schema-version="1">
<ac:parameter ac:name="icon">true</ac:parameter>
<ac:parameter ac:name="title">📋 Table of Contents</ac:parameter>
<ac:rich-text-body>
<ac:structured-macro ac:name="toc" ac:schema-version="1">
  <ac:parameter ac:name="printable">true</ac:parameter>
  <ac:parameter ac:name="style">disc</ac:parameter>
  <ac:parameter ac:name="maxLevel">2</ac:parameter>
  <ac:parameter ac:name="minLevel">1</ac:parameter>
  <ac:parameter ac:name="outline">false</ac:parameter>
</ac:structured-macro>
</ac:rich-text-body>
</ac:structured-macro>

<h2 style="color: #de350b; border-left: 4px solid #de350b; padding-left: 12px;">🔴 Issues</h2>
<table style="width: 100%; border-collapse: collapse; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden;">
<tbody>
<tr><th style="background: linear-gradient(135deg, #de350b, #ff5630); color: white; padding: 15px; text-align: left;">Theme/Vertical</th><th style="background: linear-gradient(135deg, #de350b, #ff5630); color: white; padding: 15px; text-align: left;">Description</th></tr>
{issues_rows}
</tbody>
</table>

<h2 style="color: #0052cc; border-left: 4px solid #0052cc; padding-left: 12px;">📊 Metrics</h2>
<table style="width: 100%; border-collapse: collapse; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden;">
<tbody>
<tr><th style="background: linear-gradient(135deg, #0052cc, #2684ff); color: white; padding: 15px; text-align: left;">Metric Name</th><th style="background: linear-gradient(135deg, #0052cc, #2684ff); color: white; padding: 15px; text-align: center;">Last Week</th><th style="background: linear-gradient(135deg, #0052cc, #2684ff); color: white; padding: 15px; text-align: center;">Current Week</th><th style="background: linear-gradient(135deg, #0052cc, #2684ff); color: white; padding: 15px; text-align: left;">Delta/Comments</th></tr>
{metrics_rows}
</tbody>
</table>

<h2 style="color: #ff8b00; border-left: 4px solid #ff8b00; padding-left: 12px;">🚨 Alerts Summary</h2>
<table style="width: 100%; border-collapse: collapse; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden;">
<tbody>
<tr><th style="background: linear-gradient(135deg, #ff8b00, #ffab00); color: white; padding: 15px; text-align: left;">Component</th><th style="background: linear-gradient(135deg, #ff8b00, #ffab00); color: white; padding: 15px; text-align: left;">Alert</th><th style="background: linear-gradient(135deg, #ff8b00, #ffab00); color: white; padding: 15px; text-align: center;">Frequency</th><th style="background: linear-gradient(135deg, #ff8b00, #ffab00); color: white; padding: 15px; text-align: left;">Description</th></tr>
{alerts_rows}
</tbody>
</table>

<h2 style="color: #006644; border-left: 4px solid #006644; padding-left: 12px;">💰 Cost Highlights</h2>
<table style="width: 100%; border-collapse: collapse; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden;">
<tbody>
<tr><th style="background: linear-gradient(135deg, #006644, #36b37e); color: white; padding: 15px; text-align: left;">Resource</th><th style="background: linear-gradient(135deg, #006644, #36b37e); color: white; padding: 15px; text-align: center;">Last Week</th><th style="background: linear-gradient(135deg, #006644, #36b37e); color: white; padding: 15px; text-align: center;">This Week</th></tr>
{cost_rows}
</tbody>
</table>

<h2 style="color: #403294; border-left: 4px solid #403294; padding-left: 12px;">🔥 Outages Summary</h2>
<table style="width: 100%; border-collapse: collapse; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden;">
<tbody>
<tr><th style="background: linear-gradient(135deg, #403294, #6554c0); color: white; padding: 15px; text-align: left;">Outage/RCA</th><th style="background: linear-gradient(135deg, #403294, #6554c0); color: white; padding: 15px; text-align: center;">Severity</th><th style="background: linear-gradient(135deg, #403294, #6554c0); color: white; padding: 15px; text-align: left;">Reason</th><th style="background: linear-gradient(135deg, #403294, #6554c0); color: white; padding: 15px; text-align: left;">Owner</th><th style="background: linear-gradient(135deg, #403294, #6554c0); color: white; padding: 15px; text-align: center;">Date</th></tr>
{outages_rows}
</tbody>
</table>

{ticket_section}

<h2 style="color: #5e4db2; border-left: 4px solid #5e4db2; padding-left: 12px;">✅ Action Items (TRM AIs)</h2>
<table style="width: 100%; border-collapse: collapse; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden;">
<tbody>
<tr><th style="background: linear-gradient(135deg, #5e4db2, #8777d9); color: white; padding: 15px; text-align: left;">Description</th><th style="background: linear-gradient(135deg, #5e4db2, #8777d9); color: white; padding: 15px; text-align: left;">Owner</th><th style="background: linear-gradient(135deg, #5e4db2, #8777d9); color: white; padding: 15px; text-align: center;">ETA</th></tr>
{action_items_rows}
</tbody>
</table>

<div style="background: #f4f5f7; padding: 20px; border-radius: 8px; margin-top: 30px; text-align: center;">
<p style="margin: 0; color: #6b778c;">
<em>📅 Report generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")} | 🤖 Auto-TRM-Generator</em>
</p>
</div>
"""
        
        return html_content
    
    def _build_ticket_section(self, ticket_data: Optional[Dict], date_range: str) -> str:
        if not ticket_data or ticket_data.get("total", 0) == 0:
            return ""
        
        total = ticket_data.get("total", 0)
        by_status = ticket_data.get("by_status", {})
        by_priority = ticket_data.get("by_priority", {})
        by_tech = ticket_data.get("by_tech", {})
        
        # Use real Jira data, not AI analysis for distributions
        status_dist = by_status
        priority_dist = by_priority
        tech_dist = by_tech
        
        sla_expired = ticket_data.get("sla_expired", [])
        automation = ticket_data.get("automation", [])
        vertical_metrics = ticket_data.get("vertical_metrics", [])
        cost_vertical = ticket_data.get("cost_vertical", [])
        quality_tasks = ticket_data.get("quality_tasks", [])
        
        status_rows = "".join([f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in status_dist.items()])
        
        chart_data = []
        for status, count in status_dist.items():
            chart_data.append(f"{status},{count}")
        chart_data_string = "|".join(chart_data)
        
        total_for_chart = sum(status_dist.values()) if status_dist else 1
        major_status = max(status_dist.items(), key=lambda x: x[1]) if status_dist else ("None", 0)
        major_percentage = round((major_status[1] / total_for_chart) * 100, 1)
        
        priority_rows = "".join([f"<tr style='border-bottom: 1px solid #dfe1e6;'><td style='padding: 10px; background: #f4f5f7;'>{k}</td><td style='padding: 10px; text-align: center; font-weight: bold; color: #0052cc;'>{v}</td></tr>" for k, v in priority_dist.items()])
        tech_rows = "".join([f"<tr style='border-bottom: 1px solid #dfe1e6;'><td style='padding: 10px; background: #f4f5f7;'>{k}</td><td style='padding: 10px; text-align: center; font-weight: bold; color: #0052cc;'>{v}</td></tr>" for k, v in tech_dist.items()])
        
        sla_rows = "".join([f"<tr><td style='padding: 8px; border-bottom: 1px solid #ffbdad;'>{s.get('ticket', '')}</td><td style='padding: 8px; border-bottom: 1px solid #ffbdad;'>{s.get('reason', '')}</td></tr>" for s in sla_expired]) if sla_expired else "<tr><td colspan='2' style='padding: 12px; text-align: center; font-style: italic; color: #6b778c;'>No SLA expired</td></tr>"
        
        auto_rows = "".join([f"<tr><td style='padding: 8px; border-bottom: 1px solid #abf5d1;'>{a.get('title', '')}</td><td style='padding: 8px; border-bottom: 1px solid #abf5d1;'>{a.get('status', '')}</td></tr>" for a in automation]) if automation else "<tr><td colspan='2' style='padding: 12px; text-align: center; font-style: italic; color: #6b778c;'>No automation tasks</td></tr>"
        
        vert_rows = "".join([f"<tr><td style='padding: 8px; border-bottom: 1px solid #c0b6f2;'>{v.get('vertical', '')}</td><td style='padding: 8px; border-bottom: 1px solid #c0b6f2;'>{v.get('metric', '')}</td><td style='padding: 8px; border-bottom: 1px solid #c0b6f2; text-align: center;'>{v.get('value', '')}</td></tr>" for v in vertical_metrics]) if vertical_metrics else "<tr><td colspan='3' style='padding: 12px; text-align: center; font-style: italic; color: #6b778c;'>No vertical metrics</td></tr>"
        
        cost_rows = "".join([f"<tr><td style='padding: 8px; border-bottom: 1px solid #fedec8;'>{c.get('vertical', '')}</td><td style='padding: 8px; border-bottom: 1px solid #fedec8; text-align: center;'>{c.get('cost', '')}</td></tr>" for c in cost_vertical]) if cost_vertical else "<tr><td colspan='2' style='padding: 12px; text-align: center; font-style: italic; color: #6b778c;'>No cost data</td></tr>"
        
        quality_rows = "".join([f"<tr><td style='padding: 8px; border-bottom: 1px solid #ddd6fe;'>{q.get('task', '')}</td><td style='padding: 8px; border-bottom: 1px solid #ddd6fe;'>{q.get('status', '')}</td></tr>" for q in quality_tasks]) if quality_tasks else "<tr><td colspan='2' style='padding: 12px; text-align: center; font-style: italic; color: #6b778c;'>No quality tasks</td></tr>"
        
        pie_chart = ""
        if status_dist:
            pie_chart = f"""
<ac:structured-macro ac:name="chart" ac:schema-version="1">
  <ac:parameter ac:name="type">pie</ac:parameter>
  <ac:parameter ac:name="dataDisplay">false</ac:parameter>
  <ac:parameter ac:name="title">Ticket Status Distribution</ac:parameter>
  <ac:parameter ac:name="width">400</ac:parameter>
  <ac:parameter ac:name="height">300</ac:parameter>
  <ac:rich-text-body>
    <table>
      <tbody>
        <tr><th>Status</th><th>Count</th></tr>
        {"".join([f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in status_dist.items()])}
      </tbody>
    </table>
  </ac:rich-text-body>
</ac:structured-macro>
"""
        
        return f"""
<h2>Ticket Data</h2>
<div style="background: #f4f5f7; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
<h3 style="margin-top: 0; color: #172b4d;">Overview</h3>
<p><strong>Total tickets:</strong> <span style="color: #0052cc; font-size: 1.2em;">{total}</span></p>
<p><strong>Date range:</strong> {date_range}</p>
</div>

<h3 style="color: #172b4d;">Status Distribution</h3>
<div style="text-align: center; margin-bottom: 30px;">
{pie_chart}
<p style="margin-top: 10px;"><strong>Dominant Status:</strong> {major_status[0]} ({major_percentage}%)</p>
</div>

<div style="display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 30px;">
<div style="flex: 1; min-width: 300px;">
<h3 style="color: #172b4d;">Priority Distribution</h3>
<table style="width: 100%; border-collapse: collapse; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
<tbody>
<tr><th style="background-color: #0052cc; color: white; padding: 12px; text-align: left;">Priority</th><th style="background-color: #0052cc; color: white; padding: 12px; text-align: center;">COUNT</th></tr>
{priority_rows}
</tbody>
</table>
</div>

<div style="flex: 1; min-width: 300px;">
<h3 style="color: #172b4d;">Tech wise count</h3>
<table style="width: 100%; border-collapse: collapse; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
<tbody>
<tr><th style="background-color: #0052cc; color: white; padding: 12px; text-align: left;">SYSENGG-Tech</th><th style="background-color: #0052cc; color: white; padding: 12px; text-align: center;">COUNT</th></tr>
{tech_rows}
</tbody>
</table>
</div>
</div>

<ac:structured-macro ac:name="expand" ac:schema-version="1">
<ac:parameter ac:name="title">📊 Additional Metrics</ac:parameter>
<ac:rich-text-body>

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0;">

<div>
<h4 style="color: #de350b;">SLA Expired</h4>
<table style="width: 100%; border-collapse: collapse;">
<tbody>
<tr><th style="background-color: #ffebe6; color: #de350b; padding: 8px; text-align: left;">Ticket</th><th style="background-color: #ffebe6; color: #de350b; padding: 8px; text-align: left;">Reason</th></tr>
{sla_rows}
</tbody>
</table>
</div>

<div>
<h4 style="color: #006644;">Automation</h4>
<table style="width: 100%; border-collapse: collapse;">
<tbody>
<tr><th style="background-color: #e3fcef; color: #006644; padding: 8px; text-align: left;">Task</th><th style="background-color: #e3fcef; color: #006644; padding: 8px; text-align: left;">Status</th></tr>
{auto_rows}
</tbody>
</table>
</div>

<div>
<h4 style="color: #403294;">Vertical level data</h4>
<table style="width: 100%; border-collapse: collapse;">
<tbody>
<tr><th style="background-color: #eae6ff; color: #403294; padding: 8px; text-align: left;">Vertical</th><th style="background-color: #eae6ff; color: #403294; padding: 8px; text-align: left;">Metric</th><th style="background-color: #eae6ff; color: #403294; padding: 8px; text-align: center;">Value</th></tr>
{vert_rows}
</tbody>
</table>
</div>

<div>
<h4 style="color: #974f0c;">Cost at the vertical level</h4>
<table style="width: 100%; border-collapse: collapse;">
<tbody>
<tr><th style="background-color: #fff4e6; color: #974f0c; padding: 8px; text-align: left;">Vertical</th><th style="background-color: #fff4e6; color: #974f0c; padding: 8px; text-align: center;">Cost</th></tr>
{cost_rows}
</tbody>
</table>
</div>

<div>
<h4 style="color: #5e4db2;">Quality improvement tasks</h4>
<table style="width: 100%; border-collapse: collapse;">
<tbody>
<tr><th style="background-color: #f4f1ff; color: #5e4db2; padding: 8px; text-align: left;">Task</th><th style="background-color: #f4f1ff; color: #5e4db2; padding: 8px; text-align: left;">Status</th></tr>
{quality_rows}
</tbody>
</table>
</div>

</div>

</ac:rich-text-body>
</ac:structured-macro>
"""


# Global instance
confluence = ConfluenceIntegration()
