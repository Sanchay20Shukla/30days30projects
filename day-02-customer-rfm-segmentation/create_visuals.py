"""Create LinkedIn-ready PNG charts from the generated RFM outputs."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"
REFERENCE_DATE = "2026-11-01"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    customers = read_csv(OUTPUTS / "customer_rfm.csv")
    segments = read_csv(OUTPUTS / "segment_summary.csv")
    if not customers or not segments:
        raise SystemExit("Run analyze.py first to create the RFM CSV outputs.")

    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.titleweight": "bold"})
    blue = "#2357A6"
    orange = "#E27A3F"
    muted = "#536273"
    grid = "#DCE3EC"
    source = "Synthetic transaction data • 180 customers • Reference date: 2026-11-01"

    # Revenue by behavior segment, sorted high to low for quick comparison.
    segments.sort(key=lambda row: float(row["revenue"]), reverse=True)
    labels = [row["segment"] for row in segments]
    revenues = [float(row["revenue"]) for row in segments]
    shares = [float(row["revenue_share_pct"]) for row in segments]
    counts = [int(row["customers"]) for row in segments]

    fig, ax = plt.subplots(figsize=(13.5, 9.5), dpi=120)
    y = list(range(len(labels)))
    ax.barh(y, revenues, color=[blue if i < 2 else "#8FA9CA" for i in y], height=0.66)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, max(revenues) * 1.52)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"${v/1000:.0f}k" if v >= 1000 else f"${v:.0f}"))
    ax.xaxis.grid(True, color=grid, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(grid)
    ax.tick_params(axis="y", length=0, labelsize=13, colors="#17212E")
    ax.tick_params(axis="x", labelsize=11, colors=muted)
    ax.set_xlabel("Gross revenue", color=muted, labelpad=12)
    for i, (revenue, share, count) in enumerate(zip(revenues, shares, counts)):
        ax.text(revenue + max(revenues) * 0.018, i,
                f"${revenue:,.0f}  •  {share:.1f}%  •  {count} customers",
                va="center", ha="left", fontsize=11, color="#17212E")
    fig.suptitle("Loyal and champion customers lead sample revenue", x=0.08, y=0.98,
                 ha="left", fontsize=23, color="#17212E", fontweight="bold")
    ax.set_title("Gross revenue by RFM segment", loc="left", fontsize=13, color=muted, pad=15)
    fig.text(0.08, 0.035, source + "  |  All amounts are simulated, not real customer results.",
             ha="left", fontsize=10, color=muted)
    fig.subplots_adjust(left=0.29, right=0.98, top=0.87, bottom=0.12)
    fig.savefig(OUTPUTS / "segment_revenue.png", facecolor="white", bbox_inches="tight")
    plt.close(fig)

    # Pareto curve with the actual revenue share of the top fifth of customers.
    customers.sort(key=lambda row: int(row["revenue_rank"]))
    customer_pct = [100 * i / len(customers) for i in range(1, len(customers) + 1)]
    cumulative_pct = [100 * float(row["cumulative_revenue_share"]) for row in customers]
    top_count = round(len(customers) * 0.20)
    top_share = cumulative_pct[top_count - 1]

    fig, ax = plt.subplots(figsize=(13.5, 9.5), dpi=120)
    ax.plot(customer_pct, cumulative_pct, color=blue, linewidth=3)
    ax.fill_between(customer_pct, cumulative_pct, color=blue, alpha=0.10)
    ax.axvline(20, color=orange, linewidth=1.8, linestyle=(0, (4, 3)))
    ax.axhline(top_share, color=orange, linewidth=1.4, linestyle=(0, (4, 3)))
    ax.scatter([20], [top_share], color=orange, s=95, zorder=4)
    ax.annotate(f"Top 20% ({top_count} customers)\ncontribute {top_share:.1f}% of revenue",
                xy=(20, top_share), xytext=(28, max(8, top_share - 18)),
                fontsize=12, color="#17212E", ha="left",
                arrowprops={"arrowstyle": "-", "color": orange, "lw": 1.5})
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 102)
    ax.xaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.grid(True, color=grid, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines["left"].set_color(grid)
    ax.spines["bottom"].set_color(grid)
    ax.tick_params(labelsize=11, colors=muted)
    ax.set_xlabel("Share of customers, ranked from highest to lowest revenue", color=muted, labelpad=12)
    ax.set_ylabel("Cumulative share of gross revenue", color=muted, labelpad=12)
    fig.suptitle("Revenue is concentrated, but not dominated by a tiny group", x=0.08, y=0.98,
                 ha="left", fontsize=22, color="#17212E", fontweight="bold")
    ax.set_title("Customer-level Pareto curve", loc="left", fontsize=13, color=muted, pad=15)
    fig.text(0.08, 0.035, source + "  |  The 80/20 rule is not assumed.",
             ha="left", fontsize=10, color=muted)
    fig.subplots_adjust(left=0.12, right=0.97, top=0.87, bottom=0.15)
    fig.savefig(OUTPUTS / "revenue_concentration.png", facecolor="white", bbox_inches="tight")
    plt.close(fig)

    print(f"Created charts in {OUTPUTS}")
    print(f"Customers: {len(customers)} | top {top_count} customer share: {top_share:.2f}%")


if __name__ == "__main__":
    main()
