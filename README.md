# 📊 IAM Ticket Analysis Dashboard

**Stack:** Python · SQL · pandas · Power BI · DAX · Matplotlib

## Overview
End-to-end data quality analysis and operational validation of IT service desk (ServiceNow-style) ticket datasets. Surfaces SLA risks, recurring incident patterns, and operational KPIs — mirroring real-world IAM support analytics.

## Features
| Feature | Detail |
|---|---|
| Data Quality Report | Completeness, uniqueness, null profiling per column |
| Feature Engineering | SLA utilisation score, risk score, repeat-ticket flag |
| KPI Computation | SLA compliance %, avg resolution time, escalation count |
| 6-Panel Dashboard | Category volume, SLA by priority, monthly trend, resolution distribution, heatmap, KPI card |
| CSV Export | Clean, enriched dataset ready for Power BI ingestion |

## How to Run
```bash
pip install pandas numpy matplotlib
python iam_ticket_analysis.py
```

## Output
- `iam_dashboard.png` — 6-panel visual dashboard
- `iam_tickets_clean.csv` — enriched dataset (for Power BI)

## Power BI Integration
Import `iam_tickets_clean.csv` into Power BI. Suggested DAX measures:
```dax
SLA Compliance % = 
DIVIDE(
    COUNTROWS(FILTER(Tickets, Tickets[sla_breached] = FALSE)),
    COUNTROWS(Tickets)
) * 100

Avg Resolution Hours = AVERAGE(Tickets[resolution_hours])
```

## Sample Output KPIs
```
Total Tickets        : 500
SLA Compliance Rate  : 82.2%
Avg Resolution Time  : 8.1 hrs
SLA Breaches         : 89
Repeat / Reopened    : 25.0%
Escalated Tickets    : 25
```

## Skills Demonstrated
- Data profiling & quality validation
- Feature engineering for ML pipelines
- Operational KPI design
- Dashboard storytelling with Matplotlib
- DAX measure writing for Power BI
