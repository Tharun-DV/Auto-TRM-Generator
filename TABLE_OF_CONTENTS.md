# Table of Contents Feature

**Added:** March 6, 2026  
**Status:** ✅ Implemented  
**Feature:** Automatic Table of Contents in Confluence pages

## What Was Added

The Confluence TRM pages now include an **automatic Table of Contents (TOC)** at the top of the page, right after the header and before the sections.

## Page Structure

```
📋 ProdEngg TRM — Week 10 | Mar 2 to Mar 8
DevOps Oncall: Alice
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────┐
│   TABLE OF CONTENTS         │
│                             │
│   • Issues                  │
│   • Metrics                 │
│   • Alerts Summary          │
│   • Cost Highlights         │
│   • Outages Summary         │
│   • Ticket Data             │
│   • Action Items            │
└─────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 Issues
[Table with issues...]

📊 Metrics
[Table with metrics...]

... etc ...
```

## TOC Features

The Table of Contents includes:

✅ **Automatic generation** - Updates when sections change  
✅ **Clickable links** - Jump to any section instantly  
✅ **Hierarchical structure** - Shows up to 2 levels deep  
✅ **List style** - Clean bullet-point format  
✅ **Printable** - Included when printing the page

## How It Works

The TOC uses Confluence's built-in `toc` macro with these settings:

| Parameter | Value | Description |
|-----------|-------|-------------|
| **printable** | true | Include TOC when printing |
| **style** | disc | Bullet-point style |
| **maxLevel** | 2 | Show H1 and H2 headings |
| **minLevel** | 1 | Start from H1 headings |
| **type** | list | Display as a list |
| **outline** | false | Don't use outline numbering |

## What's Included in TOC

The following sections appear in the Table of Contents:

1. **🔴 Issues** - All issues grouped by theme/vertical
2. **📊 Metrics** - Week-over-week metrics with deltas
3. **🚨 Alerts Summary** - Alerts by component
4. **💰 Cost Highlights** - Cost comparisons
5. **🔥 Outages Summary** - Incident details
6. **🎫 Ticket Data** - Ticket statistics
7. **✅ Action Items** - Action items with owners and ETAs

## Benefits

### ✅ Easy Navigation
Users can quickly jump to the section they need without scrolling

### ✅ Overview at a Glance
See all available sections before diving into details

### ✅ Professional Look
Gives the TRM report a polished, documentation-style appearance

### ✅ Accessibility
Makes the page more accessible for screen readers and navigation tools

## Example Confluence Page

When you create a TRM report, the Confluence page will look like this:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 📋 ProdEngg TRM — Week 10 | Mar 2 to Mar 8
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DevOps Oncall: Alice

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📑 Table of Contents:
   • Issues
   • Metrics  
   • Alerts Summary
   • Cost Highlights
   • Outages Summary
   • Ticket Data
   • Action Items

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 Issues
┌─────────────┬──────────────────────────┐
│ Theme       │ Description              │
├─────────────┼──────────────────────────┤
│ Compute     │ High CPU on servers      │
│ Database    │ Slow queries             │
│ Networking  │ DNS timeouts             │
└─────────────┴──────────────────────────┘

📊 Metrics
┌───────────────┬───────────┬──────────────┬─────────────────┐
│ Metric Name   │ Last Week │ Current Week │ Delta/Comments  │
├───────────────┼───────────┼──────────────┼─────────────────┤
│ P1 Alerts     │ 5         │ 8            │ +3, Rollout     │
│ API Latency   │ 120ms     │ 95ms         │ -25ms, Better   │
└───────────────┴───────────┴──────────────┴─────────────────┘

[... rest of report ...]
```

## User Experience

### Before TOC:
- Users had to scroll through entire page to find sections
- No overview of what's included
- Difficult to navigate long reports

### After TOC:
- Click on section name to jump directly
- See all sections at a glance
- Quick navigation for busy readers
- Professional documentation feel

## Customization Options

If you want to customize the TOC in the future, you can modify these parameters in `confluence_integration.py`:

```python
# Current settings:
<ac:parameter ac:name="maxLevel">2</ac:parameter>  # Show H1 and H2
<ac:parameter ac:name="type">list</ac:parameter>   # List style
<ac:parameter ac:name="outline">false</ac:parameter> # No numbering

# Other options you could use:
maxLevel: 3           # Include H3 headings
type: flat            # Flat list (no hierarchy)
outline: true         # Use outline numbering (1. 1.1 1.2)
style: none           # No bullets
style: square         # Square bullets
style: circle         # Circle bullets
```

## Technical Details

### Confluence Macro Used
```xml
<ac:structured-macro ac:name="toc" ac:schema-version="1">
  <ac:parameter ac:name="printable">true</ac:parameter>
  <ac:parameter ac:name="style">disc</ac:parameter>
  <ac:parameter ac:name="maxLevel">2</ac:parameter>
  <ac:parameter ac:name="minLevel">1</ac:parameter>
  <ac:parameter ac:name="class">bigpink</ac:parameter>
  <ac:parameter ac:name="exclude"></ac:parameter>
  <ac:parameter ac:name="type">list</ac:parameter>
  <ac:parameter ac:name="outline">false</ac:parameter>
  <ac:parameter ac:name="include"></ac:parameter>
</ac:structured-macro>
```

### How Confluence Renders It
1. Confluence scans the page for all `<h1>` and `<h2>` tags
2. Creates clickable links for each heading
3. Displays them in a formatted TOC box
4. Updates automatically if headings change

### Compatibility
- ✅ Confluence Cloud
- ✅ Confluence Server/Data Center
- ✅ Mobile view
- ✅ Print view
- ✅ PDF export

## Summary

| Feature | Status |
|---------|--------|
| **Table of Contents** | ✅ Added |
| **Auto-generated** | ✅ Yes |
| **Clickable links** | ✅ Yes |
| **Printable** | ✅ Yes |
| **Customizable** | ✅ Yes |
| **Location** | Top of page, after header |
| **Style** | List with bullets |

**The Table of Contents is now automatically included in all TRM reports created via Confluence!** 🎉

---

**Next Steps:**
1. Test by creating a TRM report via `/trm-manual`
2. Open the Confluence page link
3. Verify TOC appears and links work
4. Click on sections to navigate

**Last Updated:** March 6, 2026  
**Version:** 3.4 (with TOC)
