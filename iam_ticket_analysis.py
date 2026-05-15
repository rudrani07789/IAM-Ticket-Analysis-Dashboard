"""
IAM Ticket Analysis Dashboard
==============================
Author: Rudrani Mondal
Tools: Python · SQL · pandas · Power BI · DAX

Performs data quality analysis and operational validation of IT ticket datasets.
Identifies SLA risks, recurring incidents, and KPI trends from ServiceNow data.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import random
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# 1. SYNTHETIC DATA GENERATION
# ─────────────────────────────────────────────

random.seed(42)
np.random.seed(42)

CATEGORIES = ["Access Provisioning", "Password Reset", "Role Assignment",
               "De-provisioning", "Access Review", "MFA Setup", "Audit Request"]
PRIORITIES  = ["P1", "P2", "P3", "P4"]
STATUSES    = ["Resolved", "Closed", "Open", "In Progress", "Escalated"]
ASSIGNEES   = ["Team_Alpha", "Team_Beta", "Team_Gamma", "Team_Delta"]

SLA_LIMITS  = {"P1": 4, "P2": 8, "P3": 24, "P4": 72}   # hours

def generate_tickets(n=500):
    start = datetime(2024, 1, 1)
    records = []
    for i in range(n):
        created   = start + timedelta(hours=random.randint(0, 8760))
        priority  = random.choices(PRIORITIES, weights=[5, 20, 50, 25])[0]
        sla_limit = SLA_LIMITS[priority]
        # Simulate ~18% SLA breach rate
        resolution_hours = np.random.exponential(sla_limit * 0.9)
        breach = resolution_hours > sla_limit
        resolved = created + timedelta(hours=resolution_hours)
        status   = random.choices(STATUSES, weights=[40, 30, 10, 15, 5])[0]
        records.append({
            "ticket_id"        : f"INC{100000 + i}",
            "created_at"       : created,
            "resolved_at"      : resolved if status in ["Resolved", "Closed"] else None,
            "priority"         : priority,
            "category"         : random.choice(CATEGORIES),
            "status"           : status,
            "assignee"         : random.choice(ASSIGNEES),
            "resolution_hours" : round(resolution_hours, 2),
            "sla_limit_hours"  : sla_limit,
            "sla_breached"     : breach,
            "reopen_count"     : random.choices([0, 1, 2], weights=[75, 20, 5])[0],
        })
    return pd.DataFrame(records)

# ─────────────────────────────────────────────
# 2. DATA QUALITY ANALYSIS
# ─────────────────────────────────────────────

def data_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """Profiles completeness, uniqueness, and basic stats for each column."""
    report = []
    for col in df.columns:
        null_count  = df[col].isnull().sum()
        unique_vals = df[col].nunique()
        report.append({
            "column"       : col,
            "dtype"        : str(df[col].dtype),
            "null_count"   : null_count,
            "null_pct"     : round(null_count / len(df) * 100, 2),
            "unique_values": unique_vals,
            "sample"       : str(df[col].dropna().iloc[0]) if null_count < len(df) else "N/A",
        })
    return pd.DataFrame(report)

# ─────────────────────────────────────────────
# 3. FEATURE ENGINEERING
# ─────────────────────────────────────────────

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["created_hour"]    = df["created_at"].dt.hour
    df["created_weekday"] = df["created_at"].dt.day_name()
    df["created_month"]   = df["created_at"].dt.to_period("M").astype(str)
    df["sla_utilisation"] = (df["resolution_hours"] / df["sla_limit_hours"]).round(3)
    df["is_repeat"]       = (df["reopen_count"] > 0).astype(int)
    df["risk_score"]      = (
        df["sla_utilisation"].clip(0, 2) * 50 +
        df["reopen_count"] * 15 +
        df["priority"].map({"P1": 30, "P2": 20, "P3": 10, "P4": 5})
    ).round(2)
    return df

# ─────────────────────────────────────────────
# 4. SLA & KPI METRICS
# ─────────────────────────────────────────────

def compute_kpis(df: pd.DataFrame) -> dict:
    total        = len(df)
    breached     = df["sla_breached"].sum()
    sla_rate     = round((1 - breached / total) * 100, 2)
    avg_res_hrs  = round(df["resolution_hours"].mean(), 2)
    repeat_rate  = round(df["is_repeat"].mean() * 100, 2)
    escalated    = (df["status"] == "Escalated").sum()

    print("=" * 50)
    print("  IAM TICKET DASHBOARD — KPI SUMMARY")
    print("=" * 50)
    print(f"  Total Tickets        : {total:,}")
    print(f"  SLA Compliance Rate  : {sla_rate}%")
    print(f"  Avg Resolution Time  : {avg_res_hrs} hrs")
    print(f"  SLA Breaches         : {breached:,}")
    print(f"  Repeat / Reopened    : {repeat_rate}%")
    print(f"  Escalated Tickets    : {escalated:,}")
    print("=" * 50)

    return {
        "total": total, "sla_rate": sla_rate,
        "avg_res_hrs": avg_res_hrs, "sla_breaches": breached,
        "repeat_rate": repeat_rate, "escalated": escalated,
    }

# ─────────────────────────────────────────────
# 5. VISUALISATION DASHBOARD
# ─────────────────────────────────────────────

def plot_dashboard(df: pd.DataFrame, kpis: dict):
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle("IAM Ticket Analysis Dashboard", fontsize=18, fontweight="bold", y=1.01)
    fig.patch.set_facecolor("#0F1117")
    for ax in axes.flat:
        ax.set_facecolor("#1A1D27")
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_edgecolor("#333")

    ACCENT = "#4F8EF7"
    WARN   = "#F7A94F"
    DANGER = "#F74F4F"
    TEXT   = "white"

    # ── Panel 1: Ticket Volume by Category ──
    ax = axes[0, 0]
    cat_counts = df["category"].value_counts()
    bars = ax.barh(cat_counts.index, cat_counts.values, color=ACCENT, edgecolor="none")
    ax.set_title("Tickets by Category", color=TEXT, fontsize=12)
    ax.set_xlabel("Count", color=TEXT)
    ax.tick_params(axis="y", labelcolor=TEXT, labelsize=9)
    for bar, val in zip(bars, cat_counts.values):
        ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height() / 2,
                str(val), va="center", color=TEXT, fontsize=9)

    # ── Panel 2: SLA Compliance by Priority ──
    ax = axes[0, 1]
    sla_by_priority = df.groupby("priority")["sla_breached"].agg(
        breached="sum", total="count"
    ).assign(compliance=lambda x: (1 - x["breached"] / x["total"]) * 100)
    colors = [DANGER if c < 90 else WARN if c < 95 else ACCENT
              for c in sla_by_priority["compliance"]]
    ax.bar(sla_by_priority.index, sla_by_priority["compliance"], color=colors, edgecolor="none")
    ax.axhline(95, color=WARN, linestyle="--", linewidth=1.5, label="95% target")
    ax.set_title("SLA Compliance by Priority (%)", color=TEXT, fontsize=12)
    ax.set_ylabel("Compliance %", color=TEXT)
    ax.set_ylim(0, 110)
    ax.legend(facecolor="#1A1D27", labelcolor=TEXT, fontsize=9)
    for i, (_, row) in enumerate(sla_by_priority.iterrows()):
        ax.text(i, row["compliance"] + 1, f"{row['compliance']:.1f}%",
                ha="center", color=TEXT, fontsize=9)

    # ── Panel 3: Monthly Ticket Trend ──
    ax = axes[0, 2]
    monthly = df.groupby("created_month").size().reset_index(name="count")
    ax.plot(monthly["created_month"], monthly["count"],
            color=ACCENT, marker="o", linewidth=2, markersize=4)
    ax.fill_between(monthly["created_month"], monthly["count"], alpha=0.2, color=ACCENT)
    ax.set_title("Monthly Ticket Volume", color=TEXT, fontsize=12)
    ax.set_ylabel("Tickets", color=TEXT)
    ax.tick_params(axis="x", rotation=45, labelcolor=TEXT, labelsize=8)

    # ── Panel 4: Resolution Time Distribution ──
    ax = axes[1, 0]
    ax.hist(df["resolution_hours"].clip(upper=100), bins=40,
            color=ACCENT, edgecolor="#0F1117", alpha=0.85)
    ax.axvline(df["resolution_hours"].mean(), color=WARN, linewidth=2,
               linestyle="--", label=f"Mean: {df['resolution_hours'].mean():.1f}h")
    ax.set_title("Resolution Time Distribution", color=TEXT, fontsize=12)
    ax.set_xlabel("Hours", color=TEXT)
    ax.set_ylabel("Frequency", color=TEXT)
    ax.legend(facecolor="#1A1D27", labelcolor=TEXT, fontsize=9)

    # ── Panel 5: SLA Breach Heatmap (Weekday × Priority) ──
    ax = axes[1, 1]
    heat = df.pivot_table(index="created_weekday", columns="priority",
                          values="sla_breached", aggfunc="mean")
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heat = heat.reindex([d for d in day_order if d in heat.index])
    im = ax.imshow(heat.values, aspect="auto", cmap="YlOrRd")
    ax.set_xticks(range(len(heat.columns)))
    ax.set_xticklabels(heat.columns, color=TEXT, fontsize=9)
    ax.set_yticks(range(len(heat.index)))
    ax.set_yticklabels(heat.index, color=TEXT, fontsize=9)
    ax.set_title("SLA Breach Rate (Weekday × Priority)", color=TEXT, fontsize=12)
    plt.colorbar(im, ax=ax)

    # ── Panel 6: KPI Summary Card ──
    ax = axes[1, 2]
    ax.axis("off")
    kpi_text = (
        f"{'KPI SUMMARY':^30}\n"
        f"{'─' * 30}\n"
        f"  Total Tickets       {kpis['total']:>8,}\n"
        f"  SLA Compliance      {kpis['sla_rate']:>7.1f}%\n"
        f"  Avg Resolution      {kpis['avg_res_hrs']:>6.1f} hrs\n"
        f"  SLA Breaches        {kpis['sla_breaches']:>8,}\n"
        f"  Repeat Rate         {kpis['repeat_rate']:>7.1f}%\n"
        f"  Escalations         {kpis['escalated']:>8,}\n"
    )
    ax.text(0.05, 0.95, kpi_text, transform=ax.transAxes,
            fontsize=11, color=TEXT, fontfamily="monospace",
            verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.6", facecolor="#252836", edgecolor=ACCENT))

    plt.tight_layout()
    plt.savefig("iam_dashboard.png", dpi=150, bbox_inches="tight",
                facecolor="#0F1117")
    plt.show()
    print("\n✓ Dashboard saved as 'iam_dashboard.png'")

# ─────────────────────────────────────────────
# 6. MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("\n▶ Generating synthetic IAM ticket dataset...")
    df = generate_tickets(500)

    print("\n▶ Running data quality analysis...")
    quality = data_quality_report(df)
    print(quality.to_string(index=False))

    print("\n▶ Engineering features...")
    df = engineer_features(df)

    print("\n▶ Computing KPIs...")
    kpis = compute_kpis(df)

    print("\n▶ Rendering dashboard...")
    plot_dashboard(df, kpis)

    # Export clean dataset
    df.to_csv("iam_tickets_clean.csv", index=False)
    print("✓ Clean dataset saved as 'iam_tickets_clean.csv'")
