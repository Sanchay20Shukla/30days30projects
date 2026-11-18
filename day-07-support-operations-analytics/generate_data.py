from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)


def main() -> None:
    rng = np.random.default_rng(20261119)
    n = 6000
    created = pd.Timestamp("2026-01-01") + pd.to_timedelta(rng.integers(0, 181, n), unit="D")
    priority = rng.choice(["High", "Medium", "Low"], n, p=[0.18, 0.52, 0.30])
    channel = rng.choice(["Email", "Chat", "Phone", "Web"], n, p=[0.34, 0.32, 0.17, 0.17])
    issue = rng.choice(["Billing", "Technical", "Account", "Delivery", "Product"], n, p=[0.23, 0.30, 0.18, 0.16, 0.13])
    p_index = pd.Series(priority).map({"High": 0, "Medium": 1, "Low": 2}).to_numpy()
    response_target = np.select([priority == "High", priority == "Medium"], [1.0, 4.0], default=8.0)
    resolution_target = np.select([priority == "High", priority == "Medium"], [8.0, 24.0], default=72.0)

    response_base = np.select([channel == "Chat", channel == "Phone", channel == "Email"], [0.18, 0.28, 3.8], default=2.8)
    response_hours = np.clip(rng.lognormal(np.log(response_base + 0.4), 0.55, n) * (1 + 0.20 * p_index), 0.05, 36).round(2)

    issue_effect = pd.Series(issue).map({"Billing": 0.0, "Technical": 9.0, "Account": 3.0, "Delivery": 6.0, "Product": 7.0}).to_numpy()
    resolution_base = np.select([priority == "High", priority == "Medium"], [6.8, 18.0], default=50.0) + issue_effect
    resolution_hours = np.clip(rng.lognormal(np.log(resolution_base), 0.62, n), 0.4, 240).round(2)
    is_open = rng.random(n) < 0.045
    resolution_hours[is_open] = np.nan

    csat_latent = 4.4 - 0.40 * (response_hours > response_target) - 0.55 * (np.nan_to_num(resolution_hours, nan=resolution_target * 2) > resolution_target) - 0.15 * (priority == "High") + rng.normal(0, 0.72, n)
    rating = np.clip(np.rint(csat_latent), 1, 5).astype(int).astype(float)
    rating[rng.random(n) < 0.24] = np.nan

    frame = pd.DataFrame({
        "ticket_id": [f"T{i:06d}" for i in range(1, n + 1)],
        "created_at": created,
        "channel": channel,
        "priority": priority,
        "issue_type": issue,
        "first_response_hours": response_hours,
        "resolution_hours": resolution_hours,
        "status": np.where(is_open, "Open", "Resolved"),
        "response_sla_hours": response_target,
        "resolution_sla_hours": resolution_target,
        "customer_rating": rating,
    }).sort_values("created_at")
    frame.to_csv(DATA / "support_tickets.csv", index=False)
    print(f"Generated {len(frame):,} synthetic tickets from {frame.created_at.min().date()} to {frame.created_at.max().date()}; open backlog {is_open.sum():,}")


if __name__ == "__main__":
    main()
