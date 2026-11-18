from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, average_precision_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "customers.csv"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)
TARGET = "churned"
NUMERIC = ["tenure_months", "monthly_charges", "add_on_count"]
CATEGORICAL = ["contract_type", "internet_service", "tech_support", "payment_method"]


def main() -> None:
    df = pd.read_csv(DATA)
    assert df.customer_id.is_unique
    assert not df.isna().any().any()
    assert set(df[TARGET].unique()) <= {0, 1}
    with sqlite3.connect(":memory:") as connection:
        df.to_sql("customers", connection, index=False, if_exists="replace")
        for query_file, output_file in [
            ("churn_by_contract.sql", "churn_by_contract.csv"),
            ("churn_by_tenure_band.sql", "churn_by_tenure_band.csv"),
        ]:
            query = (ROOT / "sql" / query_file).read_text(encoding="utf-8")
            pd.read_sql_query(query, connection).to_csv(OUT / output_file, index=False)
    train, test = train_test_split(df, test_size=0.25, random_state=42, stratify=df[TARGET])
    prep = ColumnTransformer(
        [("numeric", StandardScaler(), NUMERIC), ("category", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL)]
    )
    model = Pipeline([("features", prep), ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42))])
    model.fit(train[NUMERIC + CATEGORICAL], train[TARGET])
    probabilities = model.predict_proba(test[NUMERIC + CATEGORICAL])[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(test[TARGET], predictions, labels=[0, 1]).ravel()
    metrics = pd.DataFrame(
        [
            {"holdout_customers": len(test), "holdout_churn_rate": test[TARGET].mean(), "threshold": 0.5,
             "roc_auc": roc_auc_score(test[TARGET], probabilities), "average_precision": average_precision_score(test[TARGET], probabilities),
             "precision": precision_score(test[TARGET], predictions, zero_division=0), "recall": recall_score(test[TARGET], predictions),
             "f1": f1_score(test[TARGET], predictions), "accuracy": accuracy_score(test[TARGET], predictions),
             "true_positives": tp, "false_positives": fp, "true_negatives": tn, "false_negatives": fn}
        ]
    )
    metrics.to_csv(OUT / "holdout_metrics.csv", index=False)

    scored = test[["customer_id", TARGET, "contract_type", "tenure_months", "monthly_charges", "tech_support"]].copy()
    scored["churn_probability"] = probabilities
    scored["risk_band"] = pd.cut(probabilities, bins=[-0.001, 0.35, 0.65, 1.001], labels=["Low", "Medium", "High"])
    scored.sort_values("churn_probability", ascending=False).to_csv(OUT / "holdout_customer_scores.csv", index=False)

    deciles = scored.assign(risk_decile=pd.qcut(scored.churn_probability.rank(method="first"), 10, labels=False) + 1)
    lift = deciles.groupby("risk_decile", as_index=False, observed=True).agg(
        customers=(TARGET, "size"), churners=(TARGET, "sum"), observed_churn_rate=(TARGET, "mean"),
        mean_predicted_risk=("churn_probability", "mean")
    ).sort_values("risk_decile", ascending=False)
    lift["cumulative_churn_capture"] = lift.churners.cumsum() / lift.churners.sum()
    lift.to_csv(OUT / "risk_decile_lift.csv", index=False)

    names = model.named_steps["features"].get_feature_names_out()
    weights = model.named_steps["classifier"].coef_[0]
    coefficients = pd.DataFrame({"feature": names, "coefficient": weights})
    coefficients["odds_ratio_per_unit"] = np.exp(coefficients.coefficient)
    coefficients.sort_values("coefficient", ascending=False).to_csv(OUT / "model_coefficients.csv", index=False)

    print(f"Validated {len(df):,} records; training={len(train):,}, holdout={len(test):,}")
    print(metrics.to_string(index=False))
    print(f"Top-decile observed churn rate: {lift.iloc[0].observed_churn_rate:.1%}; churn captured: {lift.iloc[0].cumulative_churn_capture:.1%}")


if __name__ == "__main__":
    main()
