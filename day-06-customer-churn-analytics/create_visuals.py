from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})


def main() -> None:
    df = pd.read_csv(ROOT / "data" / "customers.csv")
    metrics = pd.read_csv(OUT / "holdout_metrics.csv").iloc[0]
    lift = pd.read_csv(OUT / "risk_decile_lift.csv").sort_values("risk_decile", ascending=False)
    fig, ax = plt.subplots(figsize=(10, 5.8))
    rates = df.groupby("contract_type").churned.mean().sort_values(ascending=False)
    bars = ax.bar(rates.index, rates.values * 100, color=["#e77845", "#5685b5", "#5685b5"])
    ax.bar_label(bars, fmt="%.1f%%", padding=5, color="#26364a")
    ax.set_title("Churn differs across contract types", loc="left", fontsize=19, weight="bold", color="#1c2b3a", pad=18)
    ax.set_ylabel("Customers who churned (%)")
    ax.set_ylim(0, max(rates.values * 100) * 1.2)
    fig.text(0.01, 0.01, "Synthetic customer data • descriptive rates, not causal effects", color="#65758b")
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(OUT / "churn_by_contract.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5.8))
    x = range(len(lift))
    ax.bar(x, lift.observed_churn_rate * 100, color=["#e77845"] + ["#91a9c1"] * (len(lift) - 1))
    ax.axhline(metrics.holdout_churn_rate * 100, color="#1c3658", linestyle="--", linewidth=1.5, label=f"Holdout average {metrics.holdout_churn_rate:.1%}")
    ax.set_xticks(list(x), [f"{int(d)}" for d in lift.risk_decile])
    ax.set_xlabel("Risk decile (10 = highest predicted risk)")
    ax.set_ylabel("Observed churn rate (%)")
    ax.set_title("Risk ranking concentrates churn in the top decile", loc="left", fontsize=18, weight="bold", color="#1c2b3a", pad=18)
    ax.legend(frameon=False)
    fig.text(0.01, 0.01, f"Synthetic stratified holdout • logistic model ROC-AUC {metrics.roc_auc:.2f} • ranking aid, not a causal explanation", color="#65758b")
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(OUT / "risk_decile_lift.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    coef = pd.read_csv(OUT / "model_coefficients.csv")
    top = pd.concat([coef.nsmallest(6, "coefficient"), coef.nlargest(6, "coefficient")]).sort_values("coefficient")
    fig, ax = plt.subplots(figsize=(10, 6.5))
    colors = ["#5685b5" if v < 0 else "#e77845" for v in top.coefficient]
    ax.barh(top.feature.str.replace("numeric__", "", regex=False).str.replace("category__", "", regex=False).str.replace("_", " "), top.coefficient, color=colors)
    ax.axvline(0, color="#46566b", linewidth=0.9)
    ax.set_title("Logistic regression coefficients", loc="left", fontsize=19, weight="bold", color="#1c2b3a", pad=18)
    ax.set_xlabel("Coefficient (positive raises model score, holding encoded features fixed)")
    fig.text(0.01, 0.01, "Standardized numeric inputs and one-hot categories • association in this synthetic model, not causation", color="#65758b")
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(OUT / "model_coefficients.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print("Saved three charts under outputs/")


if __name__ == "__main__":
    main()
