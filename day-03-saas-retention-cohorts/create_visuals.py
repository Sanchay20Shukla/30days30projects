"""Create shareable cohort heatmap and retention curve from analysis output."""
from __future__ import annotations
import csv
from collections import defaultdict
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"

def main() -> None:
    with (OUT / "cohort_retention.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    cohorts = sorted({r["cohort_month"] for r in rows})
    max_age = max(int(r["month_age"]) for r in rows)
    grid = np.full((len(cohorts), max_age + 1), np.nan)
    for r in rows:
        grid[cohorts.index(r["cohort_month"]), int(r["month_age"])] = float(r["retention_pct"])
    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.titleweight": "bold"})
    fig, ax = plt.subplots(figsize=(13.5, 9.0), dpi=120)
    masked = np.ma.masked_invalid(grid)
    cmap = plt.get_cmap("Blues").copy()
    cmap.set_bad("#F0F3F7")
    im = ax.imshow(masked, aspect="auto", cmap=cmap, vmin=0, vmax=100)
    ax.set_xticks(range(max_age + 1), [f"M{i}" for i in range(max_age + 1)])
    ax.set_yticks(range(len(cohorts)), [c[:7] for c in cohorts])
    ax.set_xlabel("Months since signup", color="#536273", labelpad=12)
    ax.set_ylabel("Signup cohort", color="#536273", labelpad=12)
    ax.set_title("Monthly active-account retention by signup cohort", loc="left", color="#17212E", fontsize=19, pad=18)
    ax.tick_params(length=0, colors="#536273")
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            if not np.isnan(grid[i, j]):
                ax.text(j, i, f"{grid[i,j]:.0f}%", ha="center", va="center",
                        fontsize=7 if max_age > 18 else 8,
                        color="white" if grid[i,j] > 57 else "#17212E")
    cb = fig.colorbar(im, ax=ax, pad=0.02)
    cb.set_label("Active accounts (%)", color="#536273")
    fig.text(0.08, 0.025, "Synthetic SaaS activity • Only fully observed cohort ages are shown", color="#536273", fontsize=9)
    fig.subplots_adjust(left=0.12, right=0.91, top=0.91, bottom=0.12)
    fig.savefig(OUT / "cohort_retention_heatmap.png", facecolor="white", bbox_inches="tight")
    plt.close(fig)

    curves: dict[int, list[float]] = defaultdict(list)
    for r in rows:
        curves[int(r["month_age"])].append(float(r["retention_pct"]))
    ages = sorted(curves)
    means = [sum(curves[a]) / len(curves[a]) for a in ages]
    fig, ax = plt.subplots(figsize=(12.5, 7.5), dpi=120)
    ax.plot(ages, means, color="#2357A6", linewidth=3, marker="o", markersize=5)
    ax.fill_between(ages, means, color="#2357A6", alpha=0.10)
    ax.set_ylim(0, 105); ax.set_xlim(0, max(ages))
    ax.set_xticks(range(0, max(ages) + 1, 2))
    ax.set_ylabel("Average active accounts (%)", color="#536273")
    ax.set_xlabel("Months since signup", color="#536273", labelpad=12)
    ax.set_title("Retention declines as accounts age", loc="left", color="#17212E", fontsize=20, pad=18)
    ax.grid(axis="y", color="#DCE3EC"); ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#DCE3EC"); ax.tick_params(colors="#536273")
    ax.text(0.99, 0.03, "Unweighted average across cohorts with observed data at each age", transform=ax.transAxes,
            ha="right", color="#536273", fontsize=9)
    fig.subplots_adjust(left=0.11, right=0.97, top=0.88, bottom=0.15)
    fig.savefig(OUT / "retention_curve.png", facecolor="white", bbox_inches="tight")
    plt.close(fig)

    with (OUT / "monthly_metrics.csv").open(newline="", encoding="utf-8") as f:
        monthly = list(csv.DictReader(f))
    months = [r["calendar_month"][:7] for r in monthly]
    churn = [float(r["monthly_churn_pct"]) if r["monthly_churn_pct"] else np.nan for r in monthly]
    mrr = [float(r["active_mrr"]) for r in monthly]
    fig, (ax_churn, ax_mrr) = plt.subplots(2, 1, figsize=(13.5, 9.0), dpi=120, sharex=True)
    x = np.arange(len(months))
    ax_churn.bar(x, churn, color="#E27A3F", width=0.7)
    ax_churn.set_ylabel("Monthly logo churn (%)", color="#536273")
    ax_churn.set_ylim(0, max(churn[1:]) * 1.3)
    ax_churn.grid(axis="y", color="#DCE3EC")
    ax_churn.spines[["top", "right"]].set_visible(False)
    ax_churn.spines[["left", "bottom"]].set_color("#DCE3EC")
    ax_churn.tick_params(colors="#536273")
    ax_churn.set_title("Monthly subscription churn and ending MRR", loc="left",
                       color="#17212E", fontsize=19, pad=15)
    ax_mrr.plot(x, mrr, color="#2357A6", linewidth=3, marker="o", markersize=4)
    ax_mrr.fill_between(x, mrr, color="#2357A6", alpha=0.10)
    ax_mrr.set_ylabel("Ending active MRR ($)", color="#536273")
    ax_mrr.set_xticks(x, months, rotation=50, ha="right")
    ax_mrr.grid(axis="y", color="#DCE3EC")
    ax_mrr.spines[["top", "right"]].set_visible(False)
    ax_mrr.spines[["left", "bottom"]].set_color("#DCE3EC")
    ax_mrr.tick_params(colors="#536273")
    fig.text(0.08, 0.025, "Synthetic account subscriptions • Cancellation removes recurring revenue from its cancellation month",
             color="#536273", fontsize=9)
    fig.subplots_adjust(left=0.12, right=0.98, top=0.90, bottom=0.20, hspace=0.28)
    fig.savefig(OUT / "monthly_churn_mrr.png", facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print(f"Created cohort, retention, and churn/MRR charts in {OUT}")

if __name__ == "__main__":
    main()
