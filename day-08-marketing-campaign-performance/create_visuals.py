from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})


def main() -> None:
    channels = pd.read_csv(OUT / "channel_kpis.csv").sort_values("roas")
    monthly = pd.read_csv(OUT / "monthly_kpis.csv")
    campaigns = pd.read_csv(OUT / "campaign_kpis.csv")

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#e77845" if name == channels.iloc[-1].channel else "#6e91b4" for name in channels.channel]
    bars = ax.barh(channels.channel, channels.roas, color=colors)
    ax.bar_label(bars, fmt="%.1fx", padding=5)
    ax.set_xlabel("Revenue divided by ad spend (ROAS)")
    ax.set_title("Channel return varies across the portfolio", loc="left", fontsize=19, weight="bold", color="#1b2b3a", pad=18)
    fig.text(0.01, 0.01, "Synthetic six-month campaign data • ROAS is descriptive and does not measure incrementality", color="#65758b")
    fig.tight_layout(rect=[0, .04, 1, 1])
    fig.savefig(OUT / "roas_by_channel.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5.8))
    x = range(len(monthly))
    width = 0.38
    ax.bar([i - width / 2 for i in x], monthly.spend / 1000, width, label="Ad spend", color="#6e91b4")
    ax.bar([i + width / 2 for i in x], monthly.revenue / 1000, width, label="Attributed revenue", color="#e77845")
    ax.set_xticks(list(x), monthly.month)
    ax.set_ylabel("Thousands of synthetic currency units")
    ax.set_title("Monthly spend and attributed revenue", loc="left", fontsize=18, weight="bold", color="#1b2b3a", pad=18)
    ax.legend(frameon=False)
    fig.text(0.01, 0.01, "Simulated campaign reports • attribution credit is assigned directly in the generated data", color="#65758b")
    fig.tight_layout(rect=[0, .04, 1, 1])
    fig.savefig(OUT / "monthly_spend_revenue.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 6.2))
    scatter = ax.scatter(campaigns.spend, campaigns.roas, s=90 + campaigns.conversions / campaigns.conversions.max() * 250,
                         c=campaigns.roas, cmap="viridis", alpha=.85, edgecolor="white", linewidth=.8)
    label_offsets = {
        "Display | Awareness": (8, 7), "Social | Prospecting": (-48, 29),
        "Video | Launch": (8, 8), "Video | Demo": (12, 17),
    }
    for row in campaigns.itertuples():
        label = row.campaign.replace(" | ", "\n")
        ax.annotate(label, (row.spend, row.roas), xytext=label_offsets.get(row.campaign, (6, 6)),
                    textcoords="offset points", fontsize=7)
    ax.set_xlabel("Six-month campaign spend")
    ax.set_ylabel("ROAS")
    ax.set_title("Campaign efficiency and spend", loc="left", fontsize=18, weight="bold", color="#1b2b3a", pad=18)
    fig.colorbar(scatter, ax=ax, label="ROAS")
    fig.text(0.01, 0.01, "Bubble size reflects conversions • descriptive comparison, not causal lift", color="#65758b")
    fig.tight_layout(rect=[0, .04, 1, 1])
    fig.savefig(OUT / "campaign_efficiency.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print("Saved three charts under outputs/")


if __name__ == "__main__":
    main()
