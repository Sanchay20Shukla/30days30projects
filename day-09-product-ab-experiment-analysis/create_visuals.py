from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})


def main() -> None:
    variants = pd.read_csv(OUT / "variant_summary.csv").set_index("variant")
    test = pd.read_csv(OUT / "conversion_test.csv").iloc[0]
    control = variants.loc["Control"]
    treatment = variants.loc["Treatment"]

    rates = [control.conversions / control.users, treatment.conversions / treatment.users]
    ses = [np.sqrt(p * (1 - p) / n) for p, n in zip(rates, [control.users, treatment.users])]
    fig, ax = plt.subplots(figsize=(9.5, 5.7))
    bars = ax.bar(["Control", "Treatment"], np.array(rates) * 100, yerr=np.array(ses) * 196,
                  capsize=7, color=["#6e91b4", "#e77845"], width=.58)
    ax.bar_label(bars, labels=[f"{r:.2%}" for r in rates], padding=10, fontsize=12)
    ax.set_ylabel("Users who converted (%)")
    ax.set_ylim(0, max(np.array(rates) * 100) * 1.35)
    ax.set_title("Treatment conversion lift", loc="left", fontsize=19, weight="bold", color="#1b2b3a", pad=18)
    fig.text(0.01, 0.01, f"95% arm-level Wald intervals • absolute lift {test.absolute_lift_pp:+.2f} pp • synthetic randomized sample", color="#65758b")
    fig.tight_layout(rect=[0, .04, 1, 1])
    fig.savefig(OUT / "conversion_rate_comparison.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    segments = pd.read_csv(OUT / "device_segment_tests.csv").sort_values("absolute_lift_pp")
    fig, ax = plt.subplots(figsize=(9.5, 5.4))
    y = np.arange(len(segments))
    left = segments.absolute_lift_pp - segments.lift_ci_low_pp
    right = segments.lift_ci_high_pp - segments.absolute_lift_pp
    ax.errorbar(segments.absolute_lift_pp, y, xerr=[left, right], fmt="o", color="#335b89", ecolor="#6e91b4", capsize=6, markersize=9)
    ax.axvline(0, color="#e77845", linestyle="--", linewidth=1.5, label="No difference")
    ax.set_yticks(y, segments.device_type)
    ax.set_xlabel("Treatment minus control conversion rate (percentage points)")
    ax.set_title("Conversion lift by device", loc="left", fontsize=18, weight="bold", color="#1b2b3a", pad=18)
    ax.legend(frameon=False)
    fig.text(0.01, 0.01, "95% unpooled Wald intervals • exploratory subgroups; interaction testing not included", color="#65758b")
    fig.tight_layout(rect=[0, .04, 1, 1])
    fig.savefig(OUT / "device_segment_lift.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    guardrail = pd.read_csv(OUT / "revenue_per_user_guardrail.csv").iloc[0]
    fig, ax = plt.subplots(figsize=(9.5, 5.7))
    means = [guardrail.control_revenue_per_user, guardrail.treatment_revenue_per_user]
    ax.bar(["Control", "Treatment"], means, color=["#6e91b4", "#e77845"], width=.58)
    ax.bar_label(ax.containers[0], fmt="$%.2f", padding=7, fontsize=12)
    ax.set_ylabel("Revenue per assigned user (synthetic units)")
    ax.set_title("Revenue per user guardrail", loc="left", fontsize=18, weight="bold", color="#1b2b3a", pad=18)
    fig.text(0.01, 0.01, f"Treatment change {guardrail.relative_change_pct:+.1f}% • 95% CI for difference [{guardrail.change_ci_low:.2f}, {guardrail.change_ci_high:.2f}] • synthetic", color="#65758b")
    fig.tight_layout(rect=[0, .04, 1, 1])
    fig.savefig(OUT / "revenue_per_user_guardrail.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print("Saved three charts under outputs/")


if __name__ == "__main__":
    main()
