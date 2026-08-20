"""
Generates the synthetic datasets for the Capital One Data Science OA simulation.

Run once:  python generate_data.py

Creates:
  q1/drivers.csv, q1/rides_1..4.csv, q1/tests/data_analysis_tests_data/expected.csv
  q2/drivers.csv, q2/cars.csv, q2/rides_1..4.csv
  q3/data/train.csv, q3/data/test.csv
  q4/data/train.csv, q4/data/val.csv, q4/data/test.csv
  .solutions/*.csv   (ground truth used by the graders -- don't peek)
"""

import os
import shutil

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
TODAY = pd.Timestamp("2023-04-15")
ROOT = os.path.dirname(os.path.abspath(__file__))

N_DRIVERS = 3000
N_RIDES = 60000

CAR_MODELS = [
    "Toyota Camry",
    "Honda Accord",
    "Ford Fusion",
    "Nissan Altima",
    "Hyundai Sonata",
    "Chevrolet Malibu",
    "Kia Optima",
]
LANGUAGES = ["no", "Spanish", "Mandarin", "French", "Arabic", "Portuguese", "Russian"]
STATUSES = ["Rejected by the driver", "Cancelled by the passenger", "Success"]


def p(*parts):
    return os.path.join(ROOT, *parts)


def fresh(*parts):
    d = p(*parts)
    os.makedirs(d, exist_ok=True)
    return d


# --------------------------------------------------------------------------
# Core entities
# --------------------------------------------------------------------------
def build_cars():
    car_id = np.arange(1, N_DRIVERS + 1)
    model = RNG.choice(CAR_MODELS, size=N_DRIVERS)
    manufacture_year = RNG.integers(2005, 2023, size=N_DRIVERS)
    days_since = RNG.integers(1, 900, size=N_DRIVERS)
    last_inspection = [(TODAY - pd.Timedelta(days=int(d))).strftime("%Y-%m-%d") for d in days_since]
    return pd.DataFrame(
        {
            "car_id": car_id,
            "model": model,
            "manufacture_year": manufacture_year,
            "last_inspection_date": last_inspection,
        }
    )


def build_drivers(cars):
    driver_id = np.arange(1, N_DRIVERS + 1)
    car_id = RNG.permutation(cars["car_id"].to_numpy())
    age = RNG.integers(21, 68, size=N_DRIVERS)
    experience = np.clip(RNG.integers(0, 25, size=N_DRIVERS), 0, age - 20)
    started_driving_year = 2023 - experience

    lang = RNG.choice(LANGUAGES, size=N_DRIVERS, p=[0.55, 0.14, 0.08, 0.08, 0.06, 0.05, 0.04])

    # latent "quality" drives rating, tips, upvotes, complaints and the class label
    quality = RNG.normal(0, 1, size=N_DRIVERS) + 0.03 * experience + 0.15 * (lang != "no")
    rating = np.clip(4.3 + 0.35 * quality + RNG.normal(0, 0.15, N_DRIVERS), 1.0, 5.0).round(2)
    tips = np.clip(600 + 220 * quality + RNG.normal(0, 120, N_DRIVERS), 0, None).round(2)

    drivers = pd.DataFrame(
        {
            "driver_id": driver_id,
            "car_id": car_id,
            "age": age,
            "started_driving_year": started_driving_year,
            "second_language": lang,
            "rating": rating,
            "net_worth_of_tips": tips,
        }
    )
    return drivers, quality


def build_rides(drivers, quality):
    ride_id = np.arange(1, N_RIDES + 1)
    d_idx = RNG.integers(0, N_DRIVERS, size=N_RIDES)
    d_id = drivers["driver_id"].to_numpy()[d_idx]
    q = quality[d_idx]

    passenger_id = RNG.integers(1, 40000, size=N_RIDES)
    day_offset = RNG.integers(0, 400, size=N_RIDES)
    date = pd.to_datetime(TODAY) - pd.to_timedelta(day_offset, unit="D")

    # status probabilities shift with driver quality
    p_success = np.clip(0.72 + 0.06 * q, 0.35, 0.95)
    p_reject = np.clip(0.16 - 0.04 * q, 0.02, 0.45)
    p_cancel = np.clip(1 - p_success - p_reject, 0.01, None)
    probs = np.stack([p_reject, p_cancel, p_success], axis=1)
    probs = probs / probs.sum(axis=1, keepdims=True)
    u = RNG.random(N_RIDES)[:, None]
    status_idx = (u > probs.cumsum(axis=1)).sum(axis=1)
    status = np.array(STATUSES)[status_idx]

    success = status == "Success"
    p_up = np.clip(0.45 + 0.12 * q, 0.02, 0.97)

    def upvote():
        return success & (RNG.random(N_RIDES) < p_up)

    complaint = success & (RNG.random(N_RIDES) < np.clip(0.10 - 0.03 * q, 0.005, 0.5))
    incident = RNG.random(N_RIDES) < np.clip(0.03 - 0.01 * q, 0.001, 0.3)

    rides = pd.DataFrame(
        {
            "ride_id": ride_id,
            "driver_id": d_id,
            "passenger_id": passenger_id,
            "date": date.strftime("%Y-%m-%d"),
            "status": status,
            "car_clearness_upvote_given": upvote(),
            "politeness_upvote_given": upvote(),
            "communication_upvote_given": upvote(),
            "punctuality_upvote_given": upvote(),
            "complaint_given": complaint,
            "incident_given": incident,
        }
    )
    return rides


def split_rides(rides, outdir, columns):
    parts = np.array_split(rides.sample(frac=1, random_state=1).reset_index(drop=True), 4)
    for i, part in enumerate(parts, start=1):
        part[columns].to_csv(p(outdir, f"rides_{i}.csv"), index=False)


# --------------------------------------------------------------------------
# Build everything
# --------------------------------------------------------------------------
def main():
    for d in ["q1", "q2", "q3", "q4"]:
        shutil.rmtree(p(d), ignore_errors=True)

    cars = build_cars()
    drivers, quality = build_drivers(cars)
    rides = build_rides(drivers, quality)

    fresh(".solutions")

    # ---------------- Question 1 ----------------
    fresh("q1")
    fresh("q1", "tests", "data_analysis_tests_data")
    q1_drivers = drivers[["driver_id", "age", "second_language", "rating"]]
    q1_drivers.to_csv(p("q1", "drivers.csv"), index=False)
    split_rides(rides, "q1", ["ride_id", "driver_id", "passenger_id", "date", "status"])

    avg_rating = q1_drivers["rating"].mean()
    pct_lang = (q1_drivers["second_language"] != "no").mean() * 100
    success_rate = (rides["status"] == "Success").mean() * 100

    pd.DataFrame(
        {
            "insight_type": [
                "average_driver_rating",
                "percentage_drivers_with_second_language",
                "ride_success_rate",
            ],
            "value": [round(avg_rating, 5), 0, 0],
        }
    ).to_csv(p("q1", "tests", "data_analysis_tests_data", "expected.csv"), index=False)

    pd.DataFrame(
        {
            "insight_type": [
                "average_driver_rating",
                "percentage_drivers_with_second_language",
                "ride_success_rate",
            ],
            "value": [avg_rating, pct_lang, success_rate],
        }
    ).to_csv(p(".solutions", "q1_expected.csv"), index=False)

    # ---------------- Question 2 ----------------
    fresh("q2")
    drivers_q2 = drivers.copy()
    drivers_q2["driver_class"] = np.where(quality > np.median(quality), "A class", "B class")
    drivers_q2.to_csv(p("q2", "drivers.csv"), index=False)
    cars.to_csv(p("q2", "cars.csv"), index=False)
    split_rides(
        rides,
        "q2",
        [
            "ride_id",
            "driver_id",
            "passenger_id",
            "date",
            "status",
            "car_clearness_upvote_given",
            "politeness_upvote_given",
            "communication_upvote_given",
            "punctuality_upvote_given",
            "complaint_given",
        ],
    )

    upvote_cols = [
        "car_clearness_upvote_given",
        "politeness_upvote_given",
        "communication_upvote_given",
        "punctuality_upvote_given",
    ]
    agg = rides.groupby("driver_id").agg(
        number_of_upvotes=("ride_id", "size"),
    )
    agg["number_of_upvotes"] = rides.groupby("driver_id")[upvote_cols].sum().sum(axis=1)
    agg["number_of_rejected_rides"] = (
        rides.assign(r=rides["status"] == "Rejected by the driver").groupby("driver_id")["r"].sum()
    )
    agg["number_of_complaints"] = rides.groupby("driver_id")["complaint_given"].sum()
    agg["number_of_incidents"] = rides.groupby("driver_id")["incident_given"].sum()
    agg = agg.reset_index()

    collected = (
        drivers_q2.merge(cars, on="car_id", how="left")
        .merge(agg, on="driver_id", how="left")
        .rename(columns={"model": "car_model", "manufacture_year": "car_manufacture_year"})
    )
    collected["days_since_inspection"] = (
        TODAY - pd.to_datetime(collected["last_inspection_date"])
    ).dt.days
    collected["experience"] = 2023 - collected["started_driving_year"]
    for c in ["number_of_upvotes", "number_of_rejected_rides", "number_of_complaints", "number_of_incidents"]:
        collected[c] = collected[c].fillna(0).astype(int)

    q2_cols = [
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
    collected[q2_cols].to_csv(p(".solutions", "q2_collected.csv"), index=False)

    # ---------------- Question 3 ----------------
    fresh("q3")
    fresh("q3", "data")
    q3_cols = [
        "driver_id",
        "car_model",
        "car_manufacture_year",
        "days_since_inspection",
        "age",
        "experience",
        "second_language",
        "rating",
        "net_worth_of_tips",
        "number_of_rejected_rides",
        "number_of_upvotes",
        "number_of_complaints",
        "number_of_incidents",
        "driver_class",
    ]
    full = collected[q3_cols].sample(frac=1, random_state=7).reset_index(drop=True)

    # inject missing ages
    full = full.copy()
    miss = RNG.random(len(full)) < 0.07
    full.loc[miss, "age"] = np.nan

    cut = int(0.7 * len(full))
    train, test = full.iloc[:cut].copy(), full.iloc[cut:].copy()
    train.to_csv(p("q3", "data", "train.csv"), index=False)
    test.to_csv(p("q3", "data", "test.csv"), index=False)

    # ---------------- Question 4 ----------------
    fresh("q4")
    fresh("q4", "data")
    n = len(full)
    a, b = int(0.7 * n), int(0.85 * n)
    tr, va, te = full.iloc[:a].copy(), full.iloc[a:b].copy(), full.iloc[b:].copy()

    te_labels = (te["driver_class"] == "B class").astype(int)
    te_features = te.drop(columns=["driver_class"])

    tr.to_csv(p("q4", "data", "train.csv"), index=False)
    va.to_csv(p("q4", "data", "val.csv"), index=False)
    te_features.to_csv(p("q4", "data", "test.csv"), index=False)
    pd.DataFrame({"driver_class": te_labels.to_numpy()}).to_csv(
        p(".solutions", "q4_test_labels.csv"), index=False
    )

    print("Data generated.")
    print(f"  drivers: {N_DRIVERS}   rides: {N_RIDES}")
    print(f"  q3 train/test: {len(train)}/{len(test)}")
    print(f"  q4 train/val/test: {len(tr)}/{len(va)}/{len(te)}")


if __name__ == "__main__":
    main()
