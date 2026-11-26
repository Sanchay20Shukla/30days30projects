from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd
from scipy import stats


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "experiment_users.csv"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)


def conversion_test(control: pd.DataFrame, treatment: pd.DataFrame) -> dict:
    n0, n1 = len(control), len(treatment)
    x0, x1 = int(control.converted.sum()), int(treatment.converted.sum())
    p0, p1 = x0 / n0, x1 / n1
    diff = p1 - p0
    pooled = (x0 + x1) / (n0 + n1)
    se_null = np.sqrt(pooled * (1 - pooled) * (1 / n0 + 1 / n1))
    z = diff / se_null
    p_value = 2 * stats.norm.sf(abs(z))
    se_ci = np.sqrt(p0 * (1 - p0) / n0 + p1 * (1 - p1) / n1)
    return {
        "control_users": n0, "treatment_users": n1,
        "control_conversions": x0, "treatment_conversions": x1,
        "control_conversion_rate": p0, "treatment_conversion_rate": p1,
        "absolute_lift_pp": 100 * diff,
        "relative_lift_pct": 100 * diff / p0,
        "lift_ci_low_pp": 100 * (diff - 1.96 * se_ci),
        "lift_ci_high_pp": 100 * (diff + 1.96 * se_ci),
        "z_statistic": z, "p_value_two_sided": p_value,
    }


def revenue_guardrail(control: pd.DataFrame, treatment: pd.DataFrame) -> dict:
    a, b = control.revenue.to_numpy(), treatment.revenue.to_numpy()
    diff = b.mean() - a.mean()
    va, vb = a.var(ddof=1), b.var(ddof=1)
    se = np.sqrt(va / len(a) + vb / len(b))
    dof = (va / len(a) + vb / len(b)) ** 2 / ((va / len(a)) ** 2 / (len(a) - 1) + (vb / len(b)) ** 2 / (len(b) - 1))
    t_value = diff / se
    p_value = 2 * stats.t.sf(abs(t_value), dof)
    critical = stats.t.ppf(.975, dof)
    return {
        "control_revenue_per_user": a.mean(), "treatment_revenue_per_user": b.mean(),
        "absolute_change_per_user": diff,
        "relative_change_pct": 100 * diff / a.mean(),
        "change_ci_low": diff - critical * se, "change_ci_high": diff + critical * se,
        "welch_t_statistic": t_value, "p_value_two_sided": p_value,
    }


def main() -> None:
    frame = pd.read_csv(DATA, parse_dates=["assigned_at"])
    assert frame.user_id.is_unique
    assert not frame.isna().any().any()
    assert set(frame.variant.unique()) == {"Control", "Treatment"}
    assert frame.converted.isin([0, 1]).all()
    assert (frame.loc[frame.converted == 0, "revenue"] == 0).all()

    with sqlite3.connect(":memory:") as connection:
        frame.to_sql("experiment_users", connection, index=False, if_exists="replace")
        for sql_file, output_file in [
            ("variant_summary.sql", "variant_summary.csv"),
            ("segment_summary.sql", "segment_summary.csv"),
            ("daily_experiment_trend.sql", "daily_experiment_trend.csv"),
        ]:
            query = (ROOT / "sql" / sql_file).read_text(encoding="utf-8")
            pd.read_sql_query(query, connection).to_csv(OUT / output_file, index=False)

    control = frame[frame.variant == "Control"]
    treatment = frame[frame.variant == "Treatment"]
    observed_control, observed_treatment = len(control), len(treatment)
    expected = len(frame) / 2
    srm_chi2 = ((observed_control - expected) ** 2 + (observed_treatment - expected) ** 2) / expected
    srm_p = stats.chi2.sf(srm_chi2, df=1)
    result = conversion_test(control, treatment)
    result.update({"sample_ratio_chi2": srm_chi2, "sample_ratio_p_value": srm_p})
    pd.DataFrame([result]).to_csv(OUT / "conversion_test.csv", index=False)

    guardrail = revenue_guardrail(control, treatment)
    pd.DataFrame([guardrail]).to_csv(OUT / "revenue_per_user_guardrail.csv", index=False)

    segment_rows = []
    for device, group in frame.groupby("device_type"):
        c = group[group.variant == "Control"]
        t = group[group.variant == "Treatment"]
        row = {"device_type": device, **conversion_test(c, t)}
        segment_rows.append(row)
    pd.DataFrame(segment_rows).to_csv(OUT / "device_segment_tests.csv", index=False)

    print(f"Validated {len(frame):,} randomized users, {observed_control:,} control and {observed_treatment:,} treatment")
    print(pd.DataFrame([result]).to_string(index=False))
    print(pd.DataFrame([guardrail]).to_string(index=False))


if __name__ == "__main__":
    main()
