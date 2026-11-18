from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)


def main() -> None:
    rng = np.random.default_rng(20261118)
    n = 4000
    contract = rng.choice(["Month-to-month", "One year", "Two year"], n, p=[0.55, 0.30, 0.15])
    internet = rng.choice(["Fiber optic", "DSL", "No"], n, p=[0.48, 0.38, 0.14])
    tenure = np.clip(rng.gamma(shape=2.0, scale=16.0, size=n).astype(int), 1, 72)
    support = rng.choice(["Yes", "No"], n, p=[0.38, 0.62])
    payment = rng.choice(["Electronic check", "Auto-pay", "Other"], n, p=[0.38, 0.42, 0.20])
    monthly = np.clip(rng.normal(67, 18, n) + np.where(internet == "Fiber optic", 15, 0), 20, 120).round(2)
    add_on_count = rng.integers(0, 7, n)
    logit = (
        -2.0
        + 1.05 * (contract == "Month-to-month")
        - 0.65 * (contract == "Two year")
        + 0.65 * (payment == "Electronic check")
        + 0.58 * (support == "No")
        + 0.45 * (internet == "Fiber optic")
        + 0.012 * (monthly - 65)
        - 0.025 * (tenure - 24)
        - 0.11 * (add_on_count - 3)
    )
    probability = 1 / (1 + np.exp(-logit))
    churn = rng.binomial(1, probability)
    frame = pd.DataFrame(
        {
            "customer_id": [f"C{i:05d}" for i in range(1, n + 1)],
            "tenure_months": tenure,
            "contract_type": contract,
            "internet_service": internet,
            "tech_support": support,
            "payment_method": payment,
            "monthly_charges": monthly,
            "add_on_count": add_on_count,
            "churned": churn,
        }
    )
    frame.to_csv(DATA / "customers.csv", index=False)
    print(f"Generated {len(frame):,} synthetic customer records; churn rate {frame.churned.mean():.1%}")


if __name__ == "__main__":
    main()
