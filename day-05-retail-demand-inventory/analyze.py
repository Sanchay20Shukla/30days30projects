"""Backtest simple retail demand baselines and create a replenishment recommendation."""
from __future__ import annotations
import csv
import math
import sqlite3
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from statistics import mean, stdev

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT / "outputs"
SQL = ROOT / "sql"
VALIDATION_START = date(2025, 10, 1)
TEST_START = date(2025, 11, 1)
TEST_END = date(2025, 12, 31)
FORECAST_MODELS = ("seasonal_naive_7d", "trailing_mean_28d", "weekday_mean_8w")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise SystemExit(f"No rows to write: {path.name}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def wape(actual: list[float], forecast: list[float]) -> float:
    denom = sum(actual)
    return 100 * sum(abs(a - f) for a, f in zip(actual, forecast)) / denom if denom else 0.0


def forecast_one(model: str, history: list[tuple[date, float]], target: date) -> float:
    if not history:
        return 0.0
    if model == "seasonal_naive_7d":
        lookup = {d: y for d, y in history}
        return lookup.get(target - timedelta(days=7), mean(y for _, y in history[-7:]))
    if model == "trailing_mean_28d":
        return mean(y for _, y in history[-28:])
    same_weekday = [y for d, y in history if d.weekday() == target.weekday()][-8:]
    return mean(same_weekday) if same_weekday else mean(y for _, y in history[-28:])


def score_window(series: list[tuple[date, float]], start: date, end: date) -> dict[str, list[float]]:
    history: list[tuple[date, float]] = []
    forecasts: dict[str, list[float]] = {m: [] for m in FORECAST_MODELS}
    for current, actual in series:
        if start <= current <= end:
            for model in FORECAST_MODELS:
                forecasts[model].append(max(0.0, forecast_one(model, history, current)))
        history.append((current, actual))
    return forecasts


def main() -> None:
    product_rows = read_csv(DATA / "products.csv")
    sales_rows = read_csv(DATA / "daily_sales.csv")
    if not product_rows or not sales_rows:
        raise SystemExit("Run generate_data.py first.")

    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE products(
            product_id TEXT PRIMARY KEY, category TEXT NOT NULL, abc_tier TEXT NOT NULL,
            unit_cost REAL NOT NULL CHECK(unit_cost > 0), avg_daily_demand REAL NOT NULL CHECK(avg_daily_demand > 0),
            lead_time_days INTEGER NOT NULL CHECK(lead_time_days > 0), on_hand_units INTEGER NOT NULL CHECK(on_hand_units >= 0),
            on_order_units INTEGER NOT NULL CHECK(on_order_units >= 0), minimum_order_qty INTEGER NOT NULL CHECK(minimum_order_qty > 0)
        );
        CREATE TABLE daily_sales(
            date TEXT NOT NULL, product_id TEXT NOT NULL REFERENCES products(product_id),
            units_sold INTEGER NOT NULL CHECK(units_sold >= 0), promo_flag INTEGER NOT NULL CHECK(promo_flag IN (0,1)),
            PRIMARY KEY(date, product_id)
        );
    """)
    db.executemany("INSERT INTO products VALUES (:product_id,:category,:abc_tier,:unit_cost,:avg_daily_demand,:lead_time_days,:on_hand_units,:on_order_units,:minimum_order_qty)",
                   [{**r, "unit_cost": float(r["unit_cost"]), "avg_daily_demand": float(r["avg_daily_demand"]),
                     "lead_time_days": int(r["lead_time_days"]), "on_hand_units": int(r["on_hand_units"]),
                     "on_order_units": int(r["on_order_units"]), "minimum_order_qty": int(r["minimum_order_qty"])} for r in product_rows])
    db.executemany("INSERT INTO daily_sales VALUES (:date,:product_id,:units_sold,:promo_flag)",
                   [{**r, "units_sold": int(r["units_sold"]), "promo_flag": int(r["promo_flag"])} for r in sales_rows])
    checks = {
        "unique_product_ids": db.execute("SELECT COUNT(*)=COUNT(DISTINCT product_id) FROM products").fetchone()[0],
        "unique_product_days": db.execute("SELECT COUNT(*)=COUNT(DISTINCT date || product_id) FROM daily_sales").fetchone()[0],
        "every_sales_row_has_product": db.execute("SELECT COUNT(*)=0 FROM daily_sales s LEFT JOIN products p USING(product_id) WHERE p.product_id IS NULL").fetchone()[0],
        "complete_daily_panel": db.execute("SELECT COUNT(*)=(SELECT COUNT(*) FROM products)*365 FROM daily_sales").fetchone()[0],
        "valid_sales_domain": db.execute("SELECT COUNT(*)=0 FROM daily_sales WHERE units_sold<0 OR promo_flag NOT IN (0,1)").fetchone()[0],
    }
    if not all(checks.values()):
        raise SystemExit(f"Input checks failed: {checks}")

    monthly = [dict(r) for r in db.execute((SQL / "monthly_sales.sql").read_text(encoding="utf-8"))]
    promos = [dict(r) for r in db.execute((SQL / "promotion_summary.sql").read_text(encoding="utf-8"))]
    series_by_sku: dict[str, list[tuple[date, float]]] = defaultdict(list)
    promo_lookup: dict[tuple[str, date], int] = {}
    for row in sorted(sales_rows, key=lambda r: (r["product_id"], r["date"])):
        d = date.fromisoformat(row["date"])
        series_by_sku[row["product_id"]].append((d, float(row["units_sold"])))
        promo_lookup[(row["product_id"], d)] = int(row["promo_flag"])

    product_by_id = {r["product_id"]: r for r in product_rows}
    validation_forecasts: dict[str, dict[str, list[float]]] = {}
    test_forecasts: dict[str, dict[str, list[float]]] = {}
    test_actuals: dict[str, list[float]] = {}
    selected_by_sku: dict[str, str] = {}
    validation_errors: dict[str, float] = {}
    backtest_rows: list[dict[str, object]] = []
    for sku, series in series_by_sku.items():
        val_fc = score_window(series, VALIDATION_START, TEST_START - timedelta(days=1))
        val_actual = [y for d, y in series if VALIDATION_START <= d < TEST_START]
        val_scores = {m: wape(val_actual, val_fc[m]) for m in FORECAST_MODELS}
        selected = min(FORECAST_MODELS, key=lambda m: (val_scores[m], FORECAST_MODELS.index(m)))
        selected_by_sku[sku] = selected
        validation_errors[sku] = stdev([a - f for a, f in zip(val_actual, val_fc[selected])]) if len(val_actual) > 1 else 0.0
        test_fc = score_window(series, TEST_START, TEST_END)
        test_actual = [y for d, y in series if TEST_START <= d <= TEST_END]
        test_forecasts[sku] = test_fc
        test_actuals[sku] = test_actual
        test_days = [d for d, _ in series if TEST_START <= d <= TEST_END]
        for i, d in enumerate(test_days):
            backtest_rows.append({"date": d.isoformat(), "product_id": sku, "actual_units": test_actual[i],
                                  "selected_model": selected, "forecast_selected": round(test_fc[selected][i], 2),
                                  **{f"forecast_{m}": round(test_fc[m][i], 2) for m in FORECAST_MODELS},
                                  "promo_flag": promo_lookup[(sku, d)]})

    metric_rows: list[dict[str, object]] = []
    actual_all = [v for vals in test_actuals.values() for v in vals]
    for model in (*FORECAST_MODELS, "validation_selected_by_sku"):
        forecast_all = []
        for sku, values in test_forecasts.items():
            chosen = selected_by_sku[sku] if model == "validation_selected_by_sku" else model
            forecast_all.extend(values[chosen])
        error_sum = sum(abs(a - f) for a, f in zip(actual_all, forecast_all))
        bias = sum(f - a for a, f in zip(actual_all, forecast_all))
        metric_rows.append({"model": model, "test_days": len(actual_all),
                            "mae_units_per_product_day": round(error_sum / len(actual_all), 3),
                            "wape_pct": round(wape(actual_all, forecast_all), 2),
                            "bias_pct": round(100 * bias / sum(actual_all), 2) if sum(actual_all) else 0})

    next14_rows: list[dict[str, object]] = []
    plan_rows: list[dict[str, object]] = []
    for sku, series in series_by_sku.items():
        model = selected_by_sku[sku]
        history = list(series)
        next_forecasts: list[float] = []
        for offset in range(1, 15):
            target = TEST_END + timedelta(days=offset)
            predicted = max(0.0, forecast_one(model, history, target))
            next_forecasts.append(predicted)
            next14_rows.append({"date": target.isoformat(), "product_id": sku, "forecast_units": round(predicted, 2), "model": model})
            history.append((target, predicted))
        product = product_by_id[sku]
        lead_time = int(product["lead_time_days"])
        lead_demand = sum(next_forecasts[:lead_time])
        safety = math.ceil(1.65 * validation_errors[sku] * math.sqrt(lead_time))
        reorder_point = math.ceil(lead_demand + safety)
        inventory_position = int(product["on_hand_units"]) + int(product["on_order_units"])
        gap = max(0, reorder_point - inventory_position)
        moq = int(product["minimum_order_qty"])
        order_qty = int(math.ceil(gap / moq) * moq) if gap else 0
        plan_rows.append({"product_id": sku, "category": product["category"], "abc_tier": product["abc_tier"],
                          "selected_model": model, "lead_time_days": lead_time,
                          "forecast_demand_during_lead_time": round(lead_demand, 2),
                          "safety_stock_units": safety, "reorder_point_units": reorder_point,
                          "on_hand_units": int(product["on_hand_units"]), "on_order_units": int(product["on_order_units"]),
                          "inventory_position_units": inventory_position, "minimum_order_qty": moq,
                          "suggested_order_qty": order_qty})

    OUT.mkdir(exist_ok=True)
    write_csv(OUT / "monthly_sales.csv", monthly)
    write_csv(OUT / "promotion_summary.csv", promos)
    write_csv(OUT / "forecast_backtest.csv", backtest_rows)
    write_csv(OUT / "model_metrics.csv", metric_rows)
    write_csv(OUT / "next_14_day_forecast.csv", next14_rows)
    write_csv(OUT / "replenishment_plan.csv", plan_rows)
    selected_metrics = next(r for r in metric_rows if r["model"] == "validation_selected_by_sku")
    total_order = sum(int(r["suggested_order_qty"]) for r in plan_rows)
    reorder_skus = sum(int(r["suggested_order_qty"]) > 0 for r in plan_rows)
    print(f"Products: {len(product_rows)} | daily product records: {len(sales_rows):,} | test product-days: {len(actual_all):,}")
    print("Test WAPE by model: " + ", ".join(f"{r['model']}={r['wape_pct']:.2f}%" for r in metric_rows))
    print(f"Validation-selected-per-SKU strategy: WAPE {selected_metrics['wape_pct']:.2f}% | MAE {selected_metrics['mae_units_per_product_day']:.2f} units/product-day | bias {selected_metrics['bias_pct']:.2f}%")
    print(f"Illustrative reorder plan: {reorder_skus} SKUs to order | {total_order:,} units total")
    print("Data checks passed: " + ", ".join(checks))
    db.close()


if __name__ == "__main__":
    main()
