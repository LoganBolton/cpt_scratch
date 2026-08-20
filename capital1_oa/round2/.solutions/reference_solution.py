"""Reference solution for round 2 -- used to verify the graders. Don't read until you're done."""

import json
import os
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import f1_score

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import grader  # noqa: E402

TODAY = pd.Timestamp("2024-06-01")


def r(*parts):
    return os.path.join(ROOT, *parts)


# ------------------------------------------------------------------ Q1
couriers = pd.read_json(r("q1", "couriers.json"))
orders = pd.concat([pd.read_csv(r("q1", f"orders_{i}.csv")) for i in range(1, 4)], ignore_index=True)
result = {
    "average_courier_tenure_days": float((TODAY - pd.to_datetime(couriers["joined_date"])).dt.days.mean()),
    "percentage_couriers_with_ebike": float((couriers["vehicle_type"] == "E-bike").mean() * 100),
    "median_order_value": float(orders["order_value"].median()),
    "order_cancellation_rate": float((orders["status"] == "Cancelled by customer").mean() * 100),
}
with open(r("q1", "analysis_results.json"), "w") as f:
    json.dump(result, f, indent=2)

# ------------------------------------------------------------------ Q2
couriers = pd.read_json(r("q2", "couriers.json"))
vehicles = pd.read_csv(r("q2", "vehicles.csv"))
zones = pd.read_csv(r("q2", "zones.csv"))
orders = pd.concat([pd.read_csv(r("q2", f"orders_{i}.csv")) for i in range(1, 4)], ignore_index=True)

delivered = orders[orders["status"] == "Delivered"]
agg = pd.DataFrame({"number_of_orders": orders.groupby("courier_id").size()})
agg["number_of_five_star_orders"] = delivered[delivered["rating_given"] == 5].groupby("courier_id").size()
agg["on_time_rate"] = delivered.groupby("courier_id")["on_time"].mean()
agg = agg.reset_index()

c = (
    couriers.merge(vehicles, on="vehicle_id", how="left")
    .merge(zones[["zone_id", "city"]], on="zone_id", how="left")
    .merge(agg, on="courier_id", how="left")
)
c["vehicle_age_years"] = 2024 - c["purchase_year"]
c["days_since_service"] = (TODAY - pd.to_datetime(c["last_service_date"], format="%d/%m/%Y")).dt.days
c["tenure_days"] = (TODAY - pd.to_datetime(c["joined_date"])).dt.days
c["number_of_orders"] = c["number_of_orders"].fillna(0).astype(int)
c["number_of_five_star_orders"] = c["number_of_five_star_orders"].fillna(0).astype(int)
c["on_time_rate"] = c["on_time_rate"].fillna(0.0).round(4)

cols = ["courier_id", "city", "vehicle_type", "vehicle_age_years", "days_since_service", "age",
        "tenure_days", "rating", "total_earnings", "number_of_orders",
        "number_of_five_star_orders", "on_time_rate", "courier_tier"]
c[cols].to_csv(r("q2", "collected.csv"), index=False)

# ------------------------------------------------------------------ Q3
train = pd.read_csv(r("q3", "data", "train.csv"))
test = pd.read_csv(r("q3", "data", "test.csv"))

med = round(float(train["avg_delivery_minutes"].median()), 2)
city_map = {v: i for i, v in enumerate(sorted(train["city"].unique()))}
vtypes = sorted(train["vehicle_type"].unique())
lo, hi = train["total_earnings"].min(), train["total_earnings"].max()


def process(df):
    df = df.copy()
    df["avg_delivery_minutes"] = df["avg_delivery_minutes"].fillna(med)
    df["city"] = df["city"].map(city_map).astype(int)
    for v in vtypes:
        df[f"vehicle_type_{v}"] = (df["vehicle_type"] == v).astype(int)
    df = df.drop(columns=["vehicle_type"])
    df["total_earnings"] = ((df["total_earnings"] - lo) / (hi - lo)).map(lambda x: f"{x:.4f}")
    df["courier_tier"] = (df["courier_tier"] == "Gold").astype(int)
    return df


process(train).to_csv(r("q3", "processed_train.csv"), index=False)
process(test).to_csv(r("q3", "processed_test.csv"), index=False)

# ------------------------------------------------------------------ Q4
train, val, test = (pd.read_csv(r("q4", "data", f)) for f in ("train.csv", "val.csv", "test.csv"))
FEATURES = [c for c in test.columns if c != "courier_id"]
CATS = ["city", "vehicle_type"]
maps = {c: {v: i for i, v in enumerate(sorted(train[c].astype(str).unique()))} for c in CATS}
fill = train["avg_delivery_minutes"].median()


def X(df):
    out = df[FEATURES].copy()
    for col in CATS:
        out[col] = out[col].astype(str).map(maps[col]).fillna(-1).astype(int)
    out["avg_delivery_minutes"] = out["avg_delivery_minutes"].fillna(fill)
    return out


y_tr = (train["courier_tier"] == "Gold").astype(int)
y_va = (val["courier_tier"] == "Gold").astype(int)

model = HistGradientBoostingClassifier(max_iter=400, learning_rate=0.08, random_state=0)
model.fit(X(train), y_tr)

p_va = model.predict_proba(X(val))[:, 1]
best_t, best_f1 = 0.5, -1
for t in np.linspace(0.05, 0.95, 91):
    f1 = f1_score(y_va, (p_va >= t).astype(int), zero_division=0)
    if f1 > best_f1:
        best_t, best_f1 = t, f1
print(f"chosen threshold {best_t:.2f} (val F1 {best_f1:.4f})")

pred = (model.predict_proba(X(test))[:, 1] >= best_t).astype(int)
pd.DataFrame({"courier_tier": pred}).to_csv(r("q4", "predictions.csv"), index=False)

# ------------------------------------------------------------------ verify
for fn in (grader.grade_q1, grader.grade_q2, grader.grade_q3, grader.grade_q4):
    fn()
    print()
