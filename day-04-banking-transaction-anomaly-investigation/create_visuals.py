"""Create shareable investigation charts from the SQLite outputs."""
from __future__ import annotations
import csv
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"


def load(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def style(ax) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#D9E0E8")
    ax.grid(axis="y", color="#E7ECF1", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(colors="#536273", length=0)


def main() -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.titleweight": "bold"})
    rules = load("rule_performance.csv")
    labels = [r["rule_name"] for r in rules]
    flagged = [int(r["flagged_transactions"]) for r in rules]
    caught = [int(r["injected_anomalies_caught"]) for r in rules]
    fig, ax = plt.subplots(figsize=(12, 7), dpi=140)
    y = np.arange(len(labels))
    ax.barh(y + 0.18, flagged, height=0.34, color="#3D6FB4", label="Transactions flagged")
    ax.barh(y - 0.18, caught, height=0.34, color="#E08A48", label="Injected scenarios among flags")
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlabel("Transaction count")
    ax.set_title("What each screening rule surfaced", loc="left", color="#17212E", fontsize=18, pad=16)
    style(ax)
    ax.legend(frameon=False, ncol=2, loc="lower right")
    fig.text(.10, .025, "Synthetic sample • Rules are review signals, not fraud determinations", color="#536273", fontsize=9)
    fig.subplots_adjust(left=.23, right=.97, top=.88, bottom=.14)
    fig.savefig(OUT / "rule_flag_counts.png", facecolor="white", bbox_inches="tight")
    plt.close(fig)

    daily = load("daily_alerts.csv")
    dates = [r["transaction_date"] for r in daily]
    alerts = [int(r["alert_count"]) for r in daily]
    injected = [int(r["injected_anomaly_count"]) for r in daily]
    x = np.arange(len(dates))
    fig, ax = plt.subplots(figsize=(14, 7), dpi=140)
    ax.plot(x, alerts, color="#D65A4A", linewidth=2.6, label="Rule-based alerts")
    ax.scatter(x, injected, color="#3D6FB4", s=14, label="Injected scenario records", zorder=3)
    ax.set_xticks(x[::7], [dates[i][5:] for i in x[::7]])
    ax.set_xlabel("2026 date (month-day)")
    ax.set_ylabel("Records per day")
    ax.set_title("Daily review alerts and injected scenarios", loc="left", color="#17212E", fontsize=18, pad=16)
    style(ax)
    ax.legend(frameon=False, ncol=3, loc="upper right")
    fig.text(.09, .025, "Synthetic records across a 90-day observation window", color="#536273", fontsize=9)
    fig.subplots_adjust(left=.09, right=.98, top=.88, bottom=.15)
    fig.savefig(OUT / "daily_alert_trend.png", facecolor="white", bbox_inches="tight")
    plt.close(fig)

    rows = load("transaction_risk_scores.csv")
    normal = [int(r["risk_score"]) for r in rows if r["scenario_label"] == "normal"]
    anomaly = [int(r["risk_score"]) for r in rows if r["scenario_label"] != "normal"]
    max_score = max(max(normal), max(anomaly))
    bins = np.arange(-0.5, max_score + 1.5, 1)
    fig, ax = plt.subplots(figsize=(11, 6.5), dpi=140)
    ax.hist(normal, bins=bins, weights=np.full(len(normal), 100 / len(normal)),
            color="#3D6FB4", alpha=.75, label="Normal synthetic records")
    ax.hist(anomaly, bins=bins, weights=np.full(len(anomaly), 100 / len(anomaly)),
            color="#E08A48", alpha=.8, label="Injected scenario records")
    ax.axvline(2, color="#17212E", linestyle="--", linewidth=1.5, label="Alert threshold (score ≥ 2)")
    ax.set_xlabel("Explainable rule score (points)")
    ax.set_ylabel("Share within group (%)")
    ax.set_title("Risk score distribution by synthetic scenario label", loc="left", color="#17212E", fontsize=17, pad=16)
    style(ax)
    ax.legend(frameon=False)
    fig.text(.10, .025, "Illustrative synthetic labels; score overlap and false positives require human review", color="#536273", fontsize=9)
    fig.subplots_adjust(left=.10, right=.97, top=.87, bottom=.15)
    fig.savefig(OUT / "risk_score_distribution.png", facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print(f"Created 3 investigation charts in {OUT}")


if __name__ == "__main__":
    main()
