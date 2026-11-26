from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)


def main() -> None:
    rng = np.random.default_rng(20261126)
    n = 24000
    user_id = np.array([f"U{i:06d}" for i in range(1, n + 1)])
    variant = rng.permutation(np.repeat(["Control", "Treatment"], n // 2))
    device = rng.choice(["Mobile", "Desktop"], n, p=[0.54, 0.46])
    dates = pd.Timestamp("2026-10-01") + pd.to_timedelta(rng.integers(0, 28, n), unit="D")

    control_rate = np.where(device == "Mobile", 0.080, 0.119)
    treatment_rate = np.where(device == "Mobile", 0.105, 0.121)
    probability = np.where(variant == "Treatment", treatment_rate, control_rate)
    converted = rng.binomial(1, probability)

    order_value = rng.lognormal(mean=np.log(68), sigma=0.48, size=n)
    # An 8% lower order value in the treatment arm creates a revenue-per-user guardrail tradeoff.
    order_value = np.where(variant == "Treatment", order_value * 0.92, order_value)
    revenue = np.where(converted == 1, order_value, 0).round(2)

    frame = pd.DataFrame({
        "user_id": user_id,
        "assigned_at": dates,
        "variant": variant,
        "device_type": device,
        "converted": converted,
        "revenue": revenue,
    }).sort_values("assigned_at")
    frame.to_csv(DATA / "experiment_users.csv", index=False)
    print(f"Generated {len(frame):,} randomized synthetic users; assignment split: {frame.variant.value_counts(normalize=True).round(3).to_dict()}")


if __name__ == "__main__":
    main()
