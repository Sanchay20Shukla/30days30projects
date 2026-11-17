"""Create three shareable charts from the forecast backtest and inventory plan."""
from __future__ import annotations
import csv
from collections import defaultdict
from datetime import date
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"


def load_csv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def style(ax) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#D9E0E8")
    ax.grid(axis="y", color="#E7ECF1", linewidth=.8)
    ax.set_axisbelow(True)
    ax.tick_params(colors="#536273", length=0)


def main() -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.titleweight": "bold"})
    rows = load_csv("forecast_backtest.csv")
    weekly: dict[str, dict[str, float]] = defaultdict(lambda: {"actual": 0.0, "forecast": 0.0})
    for row in rows:
        d = date.fromisoformat(row["date"])
        monday = d.fromordinal(d.toordinal() - d.weekday()).isoformat()
        weekly[monday]["actual"] += float(row["actual_units"])
        weekly[monday]["forecast"] += float(row["forecast_selected"])
    weeks = sorted(weekly)
    x = np.arange(len(weeks))
    fig, ax = plt.subplots(figsize=(13, 6.8), dpi=140)
    ax.plot(x, [weekly[w]["actual"] for w in weeks], color="#263F67", linewidth=2.5, marker="o", markersize=4, label="Actual demand")
    ax.plot(x, [weekly[w]["forecast"] for w in weeks], color="#E17C43", linewidth=2.5, marker="o", markersize=4, label="Validation-selected forecast")
    ax.set_xticks(x[::2], [weeks[i][5:] for i in x[::2]], rotation=35, ha="right")
    ax.set_ylabel("Units across all products")
    ax.set_xlabel("Week beginning (2025 month-day)")
    ax.set_title("Daily refreshed forecasts through the Nov–Dec holdout", loc="left", color="#17212E", fontsize=17, pad=15)
    style(ax)
    ax.legend(frameon=False, ncol=2, loc="upper left")
    fig.text(.09, .025, "Synthetic retail demand • Each product uses the baseline with lowest October validation WAPE", color="#536273", fontsize=9)
    fig.subplots_adjust(left=.09, right=.98, top=.88, bottom=.19)
    fig.savefig(OUT / "test_period_forecast.png", facecolor="white", bbox_inches="tight")
    plt.close(fig)

    metrics = load_csv("model_metrics.csv")
    names = [r["model"].replace("_", " ") for r in metrics]
    values = [float(r["wape_pct"]) for r in metrics]
    fig, ax = plt.subplots(figsize=(11, 6.5), dpi=140)
    bars = ax.barh(np.arange(len(names)), values, color=["#8DA4BF"] * (len(names) - 1) + ["#E17C43"], height=.64)
    ax.set_yticks(np.arange(len(names)), names)
    ax.invert_yaxis()
    ax.set_xlabel("Weighted absolute percentage error (%) — lower is better")
    ax.set_title("Holdout forecast error by baseline", loc="left", color="#17212E", fontsize=17, pad=15)
    style(ax)
    for bar, value in zip(bars, values):
        ax.text(value + .25, bar.get_y() + bar.get_height() / 2, f"{value:.1f}%", va="center", color="#17212E", fontsize=9)
    ax.set_xlim(0, max(values) * 1.18)
    fig.text(.10, .025, "The SKU-specific strategy chooses a baseline using October validation data; scores shown on Nov–Dec test data", color="#536273", fontsize=9)
    fig.subplots_adjust(left=.28, right=.96, top=.88, bottom=.16)
    fig.savefig(OUT / "forecast_model_comparison.png", facecolor="white", bbox_inches="tight")
    plt.close(fig)

    plan = load_csv("replenishment_plan.csv")
    plan = sorted(plan, key=lambda r: int(r["suggested_order_qty"]), reverse=True)
    plan = [r for r in plan if int(r["suggested_order_qty"]) > 0][:15]
    fig, ax = plt.subplots(figsize=(11, 7), dpi=140)
    if plan:
        labels = [r["product_id"] for r in plan]
        values = [int(r["suggested_order_qty"]) for r in plan]
        y = np.arange(len(labels))
        ax.barh(y, values, color="#3F77B7", height=.68)
        ax.set_yticks(y, labels)
        ax.invert_yaxis()
        ax.set_xlim(0, max(values) * 1.18)
        for yi, qty in zip(y, values):
            ax.text(qty + max(values) * .015, yi, f"{qty:,}", va="center", color="#17212E", fontsize=9)
    else:
        ax.text(.5, .5, "No products below the simulated reorder point", ha="center", va="center", transform=ax.transAxes)
        ax.set_yticks([])
    ax.set_xlabel("Suggested order units (rounded to minimum order quantity)")
    ax.set_title("Illustrative products below reorder point", loc="left", color="#17212E", fontsize=17, pad=15)
    style(ax)
    fig.text(.10, .025, "Synthetic stock snapshot • Lead-time demand plus 1.65× residual SD × √lead time", color="#536273", fontsize=9)
    fig.subplots_adjust(left=.18, right=.96, top=.88, bottom=.15)
    fig.savefig(OUT / "replenishment_recommendations.png", facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print(f"Created 3 shareable forecasting and inventory charts in {OUT}")


if __name__ == "__main__":
    main()
