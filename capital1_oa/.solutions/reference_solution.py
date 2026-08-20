"""Reference solution -- used to verify the graders. Don't read this until you've done the OA."""

import os
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import precision_score, recall_score

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import grader  # noqa: E402

TODAY = pd.Timestamp("2023-04-15")


def r(*parts):
    return os.path.join(ROOT, *parts)


# ------------------------------------------------------------------ Q1
drivers = pd.read_csv(r("q1", "drivers.csv"))
rides = pd.concat([pd.read_csv(r("q1", f"rides_{i}.csv")) for i in range(1, 5)], ignore_index=True)
pd.DataFrame(
    {
        "insight_type": [
            "average_driver_rating",
            "percentage_drivers_with_second_language",
            "ride_success_rate",
        ],
        "value": [
            drivers["rating"].mean(),
            (drivers["second_language"] != "no").mean() * 100,
            (rides["status"] == "Success").mean() * 100,
        ],
    }
).to_csv(r("q1", "analysis_results.csv"), index=False)

# ------------------------------------------------------------------ Q2
drivers = pd.read_csv(r("q2", "drivers.csv"))
cars = pd.read_csv(r("q2", "cars.csv"))
rides = pd.concat([pd.read_csv(r("q2", f"rides_{i}.csv")) for i in range(1, 5)], ignore_index=True)

upvote_cols = [
    "car_clearness_upvote_given",
    "politeness_upvote_given",
    "communication_upvote_given",
    "punctuality_upvote_given",
]
upvotes = rides.groupby("driver_id")[upvote_cols].sum().sum(axis=1).rename("number_of_upvotes")

collected = drivers.merge(cars, on="car_id", how="left").merge(upvotes, on="driver_id", how="left")
collected["number_of_upvotes"] = collected["number_of_upvotes"].fillna(0).astype(int)
collected["days_since_inspection"] = (TODAY - pd.to_datetime(collected["last_inspection_date"])).dt.days
collected["experience"] = 2023 - collected["started_driving_year"]
collected = collected.rename(columns={"model": "car_model", "manufacture_year": "car_manufacture_year"})
collected[
    [
        "driver_id",
        "car_model",
        "car_manufacture_year",
        "days_since_inspection",
        "age",
        "experience",
        "second_language",
        "rating",
        "net_worth_of_tips",
        "number_of_upvotes",
        "driver_class",
    ]
].to_csv(r("q2", "collected.csv"), index=False)

# ------------------------------------------------------------------ Q3
train = pd.read_csv(r("q3", "data", "train.csv"))
test = pd.read_csv(r("q3", "data", "test.csv"))

fill_age = int(round(train["age"].mean()))
mu, sigma = train["net_worth_of_tips"].mean(), train["net_worth_of_tips"].std(ddof=0)
maps = {c: {v: i for i, v in enumerate(sorted(train[c].unique()))} for c in ["second_language", "car_model"]}


def process(df):
    df = df.copy()
    df["age"] = df["age"].fillna(fill_age).astype(int)
    for c, m in maps.items():
        df[c] = df[c].map(m).astype(int)
    df["net_worth_of_tips"] = ((df["net_worth_of_tips"] - mu) / sigma).map(lambda x: f"{x:.5f}")
    df["driver_class"] = (df["driver_class"] == "B class").astype(int)
    return df


process(train).to_csv(r("q3", "processed_train.csv"), index=False)
process(test).to_csv(r("q3", "processed_test.csv"), index=False)

# ------------------------------------------------------------------ Q4
train = pd.read_csv(r("q4", "data", "train.csv"))
val = pd.read_csv(r("q4", "data", "val.csv"))
test = pd.read_csv(r("q4", "data", "test.csv"))

FEATURES = [c for c in test.columns if c not in ("driver_id",)]
CATS = ["car_model", "second_language"]
cat_maps = {c: {v: i for i, v in enumerate(sorted(train[c].astype(str).unique()))} for c in CATS}


def X(df):
    out = df[FEATURES].copy()
    for c in CATS:
        out[c] = out[c].astype(str).map(cat_maps[c]).fillna(-1).astype(int)
    out["age"] = out["age"].fillna(train["age"].mean())
    return out


y_tr = (train["driver_class"] == "B class").astype(int)
y_va = (val["driver_class"] == "B class").astype(int)

model = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.1, random_state=0)
model.fit(X(train), y_tr)

# pick the threshold that maximizes recall subject to precision >= 0.85 on validation
p_va = model.predict_proba(X(val))[:, 1]
best_t, best_r = 0.5, -1
for t in np.linspace(0.05, 0.95, 91):
    pred = (p_va >= t).astype(int)
    if pred.sum() == 0:
        continue
    pr = precision_score(y_va, pred, zero_division=0)
    rc = recall_score(y_va, pred)
    if pr >= 0.85 and rc > best_r:
        best_t, best_r = t, rc
print(f"chosen threshold {best_t:.2f} (val recall {best_r:.4f})")

pred = (model.predict_proba(X(test))[:, 1] >= best_t).astype(int)
pd.DataFrame({"driver_class": pred}).to_csv(r("q4", "predictions.csv"), index=False)

# ------------------------------------------------------------------ verify
for fn in (grader.grade_q1, grader.grade_q2, grader.grade_q3, grader.grade_q4):
    fn()
    print()
