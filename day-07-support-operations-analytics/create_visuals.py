from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})


def main() -> None:
    priority = pd.read_csv(OUT / "sla_by_priority.csv")
    monthly = pd.read_csv(OUT / "monthly_support_trend.csv")
    channel = pd.read_csv(OUT / "channel_performance.csv")

    fig, ax = plt.subplots(figsize=(9.5, 5.6))
    bars = ax.bar(priority.priority, priority.resolution_sla_met_pct, color=["#df7446", "#4d83ad", "#4d83ad"])
    ax.bar_label(bars, fmt="%.1f%%", padding=5)
    ax.set_ylim(0, 110)
    ax.set_ylabel("Resolved tickets within target (%)")
    ax.set_title("Resolution SLA attainment by priority", loc="left", fontsize=19, weight="bold", color="#1b2b3a", pad=18)
    fig.text(0.01, 0.01, "Synthetic support ticket data • SLA is evaluated only for resolved tickets", color="#65758b")
    fig.tight_layout(rect=[0, .04, 1, 1])
    fig.savefig(OUT / "sla_by_priority.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.plot(monthly.month, monthly.tickets_created, marker="o", linewidth=2.5, color="#335b89", label="Tickets created")
    ax.bar(monthly.month, monthly.open_tickets, color="#e77845", alpha=.78, label="Still open")
    ax.set_ylabel("Tickets")
    ax.tick_params(axis="x", rotation=35)
    ax.set_title("Support volume and open tickets by month", loc="left", fontsize=18, weight="bold", color="#1b2b3a", pad=18)
    ax.legend(frameon=False)
    fig.text(0.01, 0.01, "Open counts represent ticket status in the generated snapshot, not a historical daily backlog", color="#65758b")
    fig.tight_layout(rect=[0, .04, 1, 1])
    fig.savefig(OUT / "monthly_volume_backlog.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.5, 5.6))
    ch = channel.sort_values("response_sla_met_pct")
    bars = ax.barh(ch.channel, ch.response_sla_met_pct, color="#5685b5")
    ax.bar_label(bars, fmt="%.1f%%", padding=5)
    ax.set_xlim(0, 110)
    ax.set_xlabel("First response within target (%)")
    ax.set_title("First-response SLA attainment by channel", loc="left", fontsize=18, weight="bold", color="#1b2b3a", pad=18)
    fig.text(0.01, 0.01, "Channel patterns in synthetic data are illustrative, not benchmarks", color="#65758b")
    fig.tight_layout(rect=[0, .04, 1, 1])
    fig.savefig(OUT / "response_sla_by_channel.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print("Saved three charts under outputs/")


if __name__ == "__main__":
    main()
