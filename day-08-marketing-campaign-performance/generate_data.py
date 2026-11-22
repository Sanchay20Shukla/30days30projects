from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)

CAMPAIGNS = [
    ("Search | Brand", "Search", 0.110, 0.078, 72, 8.0, 0.58),
    ("Search | Generic", "Search", 0.052, 0.052, 86, 8.0, 0.58),
    ("Social | Prospecting", "Social", 0.020, 0.019, 68, 7.0, 0.48),
    ("Social | Retargeting", "Social", 0.041, 0.049, 78, 7.0, 0.48),
    ("Email | Newsletter", "Email", 0.125, 0.043, 64, 4.0, 0.14),
    ("Email | Winback", "Email", 0.092, 0.055, 82, 4.0, 0.14),
    ("Display | Awareness", "Display", 0.009, 0.009, 80, 4.0, 0.15),
    ("Display | Retargeting", "Display", 0.018, 0.032, 88, 4.0, 0.15),
    ("Affiliate | Partners", "Affiliate", 0.031, 0.039, 94, 1.5, 0.17),
    ("Affiliate | Content", "Affiliate", 0.024, 0.031, 102, 1.5, 0.17),
    ("Video | Launch", "Video", 0.012, 0.012, 76, 12.0, 0.30),
    ("Video | Demo", "Video", 0.016, 0.018, 92, 12.0, 0.30),
]


def main() -> None:
    rng = np.random.default_rng(20261122)
    dates = pd.date_range("2026-01-01", periods=181, freq="D")
    rows = []
    for campaign, channel, ctr, cvr, aov, cpm, cpc in CAMPAIGNS:
        campaign_factor = rng.lognormal(0, 0.09)
        for day in dates:
            seasonal = 1 + 0.12 * np.sin(2 * np.pi * day.dayofyear / 30.5)
            weekend = 1.10 if day.dayofweek >= 5 else 1.0
            impressions = int(rng.lognormal(np.log(18000 * seasonal * weekend), 0.22))
            clicks = int(rng.binomial(impressions, min(ctr * campaign_factor, 0.9)))
            conversions = int(rng.binomial(clicks, min(cvr * campaign_factor, 0.9)))
            revenue = round(float(rng.gamma(shape=max(1, conversions), scale=aov)) if conversions else 0.0, 2)
            spend = round(impressions * cpm / 1000 + clicks * cpc, 2)
            rows.append((day, campaign, channel, impressions, clicks, conversions, spend, revenue))
    frame = pd.DataFrame(rows, columns=["date", "campaign", "channel", "impressions", "clicks", "conversions", "spend", "revenue"])
    frame.to_csv(DATA / "daily_campaign_performance.csv", index=False)
    print(f"Generated {len(frame):,} synthetic campaign-day records across {frame.campaign.nunique()} campaigns")


if __name__ == "__main__":
    main()
