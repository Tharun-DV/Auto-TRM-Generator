# New Features: Custom Themes & Enhanced Metrics

**Date:** March 6, 2026  
**Status:** ✅ Implemented  
**Version:** 3.3

## What's New

### 1. ✨ Custom Theme/Vertical for Issues

You can now add **custom themes** instead of being limited to predefined ones!

#### How It Works:

When adding an issue:
1. Select from dropdown: Compute, Infrasec, Haproxy, Latency, Alerting, Logging, **or Custom**
2. If you select **"Custom"**, enter your own theme in the text field below
3. Examples: Networking, Database, Security, Monitoring, CI/CD, etc.

#### Example:

**Scenario:** You want to add issues for "Networking" and "Database"

```
Click "➕ Add Issue"
  Theme: Custom
  Custom Theme: Networking
  Description: DNS resolution issues on prod
  → Submit

Click "➕ Add Issue"
  Theme: Custom
  Custom Theme: Database
  Description: Redis connection pool exhausted
  → Submit

Click "➕ Add Issue"
  Theme: Compute  (predefined)
  Description: High CPU on servers
  → Submit
```

**Result in Report:**
```
| Theme/Vertical | Description |
|---|---|
| Compute | High CPU on servers |
| Database | Redis connection pool exhausted |
| Networking | DNS resolution issues on prod |
```

**Note:** Themes are automatically sorted alphabetically!

---

### 2. ✨ Enhanced Metrics Table

Metrics now show **week-over-week comparison** with delta/comments!

#### Old Format (Before):
```
| # | Metric | Value |
|---|---|---|
| 1 | P1 Alerts | 8 |
| 2 | Infrasec P0 | 3 |
```

#### New Format (After):
```
| Metric Name | Last Week | Current Week | Delta/Comments |
|---|---|---|---|
| P1 Alerts | 5 | 8 | +3 (↑60%), Spike due to feature rollout |
| Infrasec P0 | 2 | 3 | +1, Investigating root cause |
| API Latency (p95) | 120ms | 150ms | +30ms (↑25%), DB slow queries |
| Uptime SLA | 99.9% | 99.95% | +0.05% (↑), Improved! |
```

#### How to Add Metrics:

Click "📊 Add Metric" and fill in:
- **Metric Name**: Any metric you want to track (e.g., "P1 Alerts", "API Latency", "Error Rate")
- **Last Week Value**: Previous week's value (e.g., "5", "120ms", "99.9%")
- **Current Week Value**: This week's value (e.g., "8", "150ms", "99.95%")
- **Delta/Comments** (optional): Change and context (e.g., "+3 (↑60%), Due to new feature")

#### Examples:

**Metric 1:**
- Name: P1 Alerts
- Last Week: 5
- Current Week: 8
- Delta: +3 (↑60%), Spike from new monitoring

**Metric 2:**
- Name: API Response Time (p95)
- Last Week: 120ms
- Current Week: 95ms
- Delta: -25ms (↓21%), Optimized queries

**Metric 3:**
- Name: Deployment Frequency
- Last Week: 12
- Current Week: 18
- Delta: +6 (↑50%), Increased velocity

**Metric 4:**
- Name: Infrastructure Cost
- Last Week: $45,000
- Current Week: $42,000
- Delta: -$3,000 (↓7%), Cost optimization

---

## Benefits

### Custom Themes
✅ **Flexibility** - Add any theme/category you need  
✅ **Organization** - Group issues by your team's structure  
✅ **Clarity** - Use terminology familiar to your team  
✅ **Scalability** - Not limited to 6 predefined themes

### Enhanced Metrics
✅ **Context** - See trends, not just current values  
✅ **Comparison** - Week-over-week changes at a glance  
✅ **Insights** - Add comments explaining the delta  
✅ **Flexibility** - Track any metric (not just P0 metrics)

---

## Complete Example

### Adding Entries:

**Issues:**
1. Compute: High CPU on prod servers
2. Compute: Memory leak in service-x
3. Custom theme "Networking": DNS timeouts
4. Custom theme "Database": Slow queries
5. Latency: API response time spike

**Metrics:**
1. P1 Alerts: 5 → 8 (+3, New monitors added)
2. API Latency: 120ms → 95ms (-25ms, Optimized)
3. Error Rate: 0.5% → 0.3% (-0.2%, Improved)

**Alerts:**
1. API Gateway / High Error Rate / 10/hour / 5xx errors

### Generated Report:

```
📋 ProdEngg TRM — Week 10 | Mar 2 to Mar 8
DevOps Oncall: Alice
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 Issues
| Theme/Vertical | Description |
|---|---|
| Compute | High CPU on prod servers; Memory leak in service-x |
| Database | Slow queries |
| Latency | API response time spike |
| Networking | DNS timeouts |

📊 Metrics
| Metric Name | Last Week | Current Week | Delta/Comments |
|---|---|---|---|
| P1 Alerts | 5 | 8 | +3, New monitors added |
| API Latency | 120ms | 95ms | -25ms, Optimized |
| Error Rate | 0.5% | 0.3% | -0.2%, Improved |

🚨 Alerts Summary
| Component | Alert | Frequency | Description |
|---|---|---|---|
| API Gateway | High Error Rate | 10/hour | 5xx errors |

[... rest of report ...]
```

---

## Migration from Old Format

### If you used the old format:

**Before (Old):**
- Fixed themes: Compute, Infrasec, Haproxy, Latency, Alerting, Logging
- Metrics: P1 Alerts, Infrasec P0, S1 RCAs, S2/S3 RCAs

**After (New):**
- All old themes still available in dropdown
- Just add them as before (they're still there!)
- For P0 metrics, add each as a separate metric:
  - Add Metric: "P1 Alerts" with values
  - Add Metric: "Infrasec P0" with values
  - Add Metric: "S1 RCAs" with values
  - Add Metric: "S2/S3 RCAs" with values

**No breaking changes!** Old themes work exactly as before, just with more options now.

---

## Tips & Best Practices

### For Custom Themes:
- Use consistent naming (e.g., always "Database" not sometimes "DB")
- Be specific (e.g., "Networking - DNS" vs just "Network")
- Keep it short (1-3 words max)
- Use title case for consistency

### For Metrics:
- **Be consistent with units** (always "ms" for latency, not sometimes "milliseconds")
- **Calculate delta manually** (the field doesn't auto-calculate)
- **Add context** in Delta/Comments (explain WHY it changed)
- **Use symbols** for clarity: ↑ for increase, ↓ for decrease
- **Track what matters** - not just counts, but latency, error rates, SLAs, etc.

### Example Good Metrics:
```
✅ API Latency (p95): 120ms → 95ms | -25ms (↓21%), Query optimization
✅ Error Rate: 0.5% → 0.3% | -0.2pp (↓40%), Fixed memory leaks
✅ Deployment Success Rate: 92% → 98% | +6pp (↑7%), Better testing
```

### Example Bad Metrics:
```
❌ Metric Name: stuff  (too vague)
❌ Last Week: 5, Current Week: 8  (no context in delta)
❌ Delta: more  (not quantified)
```

---

## Summary

| Feature | Old | New |
|---------|-----|-----|
| **Issue Themes** | 6 fixed themes | 6 predefined + unlimited custom |
| **Metrics Format** | Single value | Last Week → Current Week + Delta |
| **Metrics Count** | 4 fixed metrics | Unlimited custom metrics |
| **Flexibility** | Limited | High |

**Both features are live and ready to use!** 🚀

---

**Last Updated:** March 6, 2026  
**Tested:** ✅ Syntax validated  
**Ready for:** Production use
