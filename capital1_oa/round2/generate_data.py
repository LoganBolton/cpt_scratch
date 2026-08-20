"""
Generates the synthetic datasets for OA simulation round 2 (food-delivery couriers).

Run once:  python generate_data.py

Creates:
  q1/couriers.json, q1/orders_1..3.csv, q1/tests/expected_format.json
  q2/couriers.json, q2/vehicles.csv, q2/zones.csv, q2/orders_1..3.csv
  q3/data/train.csv, q3/data/test.csv
  q4/data/train.csv, q4/data/val.csv, q4/data/test.csv
  .solutions/   (ground truth used by the graders -- don't peek)
"""

import json
import os
import shutil

import numpy as np
import pandas as pd

RNG = np.random.default_rng(2025)
TODAY = pd.Timestamp("2024-06-01")
ROOT = os.path.dirname(os.path.abspath(__file__))

N_COURIERS = 2500
N_ORDERS = 70000

CITIES = ["Austin", "Boston", "Chicago", "Denver", "Seattle"]
REGIONS = {"Austin": "South", "Boston": "Northeast", "Chicago": "Midwest",
           "Denver": "West", "Seattle": "West"}
VEHICLE_TYPES = ["Bicycle", "Car", "E-bike", "Scooter", "Walking"]
STATUSES = ["Delivered", "Cancelled by customer", "Unassigned"]


def p(*parts):
    return os.path.join(ROOT, *parts)


def fresh(*parts):
    d = p(*parts)
    os.makedirs(d, exist_ok=True)
    return d


def write_csv(df, path):
    df.to_csv(path, index=False)


# --------------------------------------------------------------------------
def build_zones():
    rows = []
    zid = 1
    for city in CITIES:
        for k in range(4):
            rows.append({"zone_id": zid, "city": city, "region": REGIONS[city], "zone_name": f"{city}-{k + 1}"})
            zid += 1
    return pd.DataFrame(rows)


def build_vehicles():
    vehicle_id = np.arange(1000, 1000 + N_COURIERS)
    vtype = RNG.choice(VEHICLE_TYPES, size=N_COURIERS, p=[0.22, 0.30, 0.24, 0.16, 0.08])
    purchase_year = RNG.integers(2012, 2024, size=N_COURIERS)
    days = RNG.integers(3, 700, size=N_COURIERS)
    last_service = [(TODAY - pd.Timedelta(days=int(d))).strftime("%d/%m/%Y") for d in days]
    return pd.DataFrame(
        {
            "vehicle_id": vehicle_id,
            "vehicle_type": vtype,
            "purchase_year": purchase_year,
            "last_service_date": last_service,  # note: DD/MM/YYYY, not ISO
        }
    )


def build_couriers(vehicles, zones):
    courier_id = np.arange(5000, 5000 + N_COURIERS)
    vehicle_id = RNG.permutation(vehicles["vehicle_id"].to_numpy())
    zone_id = RNG.choice(zones["zone_id"].to_numpy(), size=N_COURIERS)
    age = RNG.integers(18, 64, size=N_COURIERS)
    tenure_days = RNG.integers(30, 1800, size=N_COURIERS)
    joined = [(TODAY - pd.Timedelta(days=int(d))).strftime("%Y-%m-%d") for d in tenure_days]

    quality = RNG.normal(0, 1, N_COURIERS) + 0.0004 * tenure_days
    rating = np.clip(4.2 + 0.32 * quality + RNG.normal(0, 0.18, N_COURIERS), 1.0, 5.0).round(2)
    earnings = np.clip(9000 + 2600 * quality + 4.0 * tenure_days + RNG.normal(0, 900, N_COURIERS), 0, None).round(2)

    couriers = pd.DataFrame(
        {
            "courier_id": courier_id,
            "vehicle_id": vehicle_id,
            "zone_id": zone_id,
            "age": age,
            "joined_date": joined,
            "rating": rating,
            "total_earnings": earnings,
        }
    )
    return couriers, quality, tenure_days


def build_orders(couriers, quality):
    order_id = np.arange(1, N_ORDERS + 1)
    idx = RNG.integers(0, N_COURIERS, size=N_ORDERS)
    courier_id = couriers["courier_id"].to_numpy()[idx]
    q = quality[idx]

    customer_id = RNG.integers(100000, 180000, size=N_ORDERS)
    day_offset = RNG.integers(0, 365, size=N_ORDERS)
    order_date = (TODAY - pd.to_timedelta(day_offset, unit="D")).strftime("%Y-%m-%d")

    p_delivered = np.clip(0.80 + 0.05 * q, 0.4, 0.97)
    p_cancel = np.clip(0.12 - 0.03 * q, 0.02, 0.4)
    probs = np.stack([p_delivered, p_cancel, np.clip(1 - p_delivered - p_cancel, 0.01, None)], axis=1)
    probs /= probs.sum(axis=1, keepdims=True)
    u = RNG.random(N_ORDERS)[:, None]
    status = np.array(["Delivered", "Cancelled by customer", "Unassigned"])[(u > probs.cumsum(axis=1)).sum(axis=1)]

    delivered = status == "Delivered"
    order_value = np.clip(RNG.gamma(4.0, 7.5, N_ORDERS), 4, None).round(2)
    delivery_minutes = np.where(delivered, np.clip(34 - 3.0 * q + RNG.normal(0, 7, N_ORDERS), 5, None).round(1), np.nan)
    on_time = delivered & (RNG.random(N_ORDERS) < np.clip(0.78 + 0.09 * q, 0.05, 0.99))
    rating_given = np.where(
        delivered,
        np.clip(np.round(4.1 + 0.5 * q + RNG.normal(0, 0.8, N_ORDERS)), 1, 5),
        np.nan,
    )
    complaint = delivered & (RNG.random(N_ORDERS) < np.clip(0.09 - 0.03 * q, 0.005, 0.5))

    return pd.DataFrame(
        {
            "order_id": order_id,
            "courier_id": courier_id,
            "customer_id": customer_id,
            "order_date": order_date,
            "status": status,
            "order_value": order_value,
            "delivery_minutes": delivery_minutes,
            "rating_given": rating_given,
            "on_time": on_time,
            "complaint_filed": complaint,
        }
    )


def split_orders(orders, outdir, columns, n_parts=3):
    shuffled = orders.sample(frac=1, random_state=3).reset_index(drop=True)
    for i, part in enumerate(np.array_split(shuffled, n_parts), start=1):
        write_csv(part[columns], p(outdir, f"orders_{i}.csv"))


# --------------------------------------------------------------------------
def main():
    for d in ["q1", "q2", "q3", "q4"]:
        shutil.rmtree(p(d), ignore_errors=True)
    fresh(".solutions")

    zones = build_zones()
    vehicles = build_vehicles()
    couriers, quality, tenure_days = build_couriers(vehicles, zones)
    orders = build_orders(couriers, quality)

    # ---------------- Question 1 ----------------
    fresh("q1")
    fresh("q1", "tests")
    q1_couriers = couriers[["courier_id", "age", "joined_date", "rating"]].copy()
    q1_couriers["vehicle_type"] = vehicles.set_index("vehicle_id").loc[
        couriers["vehicle_id"], "vehicle_type"
    ].to_numpy()
    q1_couriers.to_json(p("q1", "couriers.json"), orient="records", indent=1)
    split_orders(orders, "q1", ["order_id", "courier_id", "customer_id", "order_date", "status", "order_value"])

    tenure = (TODAY - pd.to_datetime(q1_couriers["joined_date"])).dt.days
    truth_q1 = {
        "average_courier_tenure_days": float(tenure.mean()),
        "percentage_couriers_with_ebike": float((q1_couriers["vehicle_type"] == "E-bike").mean() * 100),
        "median_order_value": float(orders["order_value"].median()),
        "order_cancellation_rate": float((orders["status"] == "Cancelled by customer").mean() * 100),
    }
    with open(p("q1", "tests", "expected_format.json"), "w") as f:
        json.dump(
            {
                "average_courier_tenure_days": round(truth_q1["average_courier_tenure_days"], 5),
                "percentage_couriers_with_ebike": 0,
                "median_order_value": 0,
                "order_cancellation_rate": 0,
            },
            f,
            indent=2,
        )
    with open(p(".solutions", "q1_truth.json"), "w") as f:
        json.dump(truth_q1, f, indent=2)

    # ---------------- Question 2 ----------------
    fresh("q2")
    couriers_q2 = couriers.copy()
    couriers_q2["courier_tier"] = np.where(quality > np.quantile(quality, 0.6), "Gold", "Standard")
    couriers_q2.to_json(p("q2", "couriers.json"), orient="records", indent=1)
    vehicles.to_csv(p("q2", "vehicles.csv"), index=False)
    zones.to_csv(p("q2", "zones.csv"), index=False)
    split_orders(
        orders,
        "q2",
        ["order_id", "courier_id", "customer_id", "order_date", "status", "order_value",
         "delivery_minutes", "rating_given", "on_time", "complaint_filed"],
    )

    delivered = orders[orders["status"] == "Delivered"]
    agg = pd.DataFrame({"number_of_orders": orders.groupby("courier_id").size()})
    agg["number_of_five_star_orders"] = delivered[delivered["rating_given"] == 5].groupby("courier_id").size()
    agg["on_time_rate"] = delivered.groupby("courier_id")["on_time"].mean()
    agg["number_of_cancellations"] = (
        orders.assign(c=orders["status"] == "Cancelled by customer").groupby("courier_id")["c"].sum()
    )
    agg["number_of_complaints"] = orders.groupby("courier_id")["complaint_filed"].sum()
    agg["avg_delivery_minutes"] = delivered.groupby("courier_id")["delivery_minutes"].mean()
    agg = agg.reset_index()

    collected = (
        couriers_q2.merge(vehicles, on="vehicle_id", how="left")
        .merge(zones[["zone_id", "city"]], on="zone_id", how="left")
        .merge(agg, on="courier_id", how="left")
    )
    collected["tenure_days"] = (TODAY - pd.to_datetime(collected["joined_date"])).dt.days
    collected["days_since_service"] = (
        TODAY - pd.to_datetime(collected["last_service_date"], format="%d/%m/%Y")
    ).dt.days
    collected["vehicle_age_years"] = 2024 - collected["purchase_year"]
    for c in ["number_of_orders", "number_of_five_star_orders", "number_of_cancellations", "number_of_complaints"]:
        collected[c] = collected[c].fillna(0).astype(int)
    collected["on_time_rate"] = collected["on_time_rate"].fillna(0.0).round(4)
    collected["avg_delivery_minutes"] = collected["avg_delivery_minutes"].round(2)

    q2_cols = [
        "courier_id",
        "city",
        "vehicle_type",
        "vehicle_age_years",
        "days_since_service",
        "age",
        "tenure_days",
        "rating",
        "total_earnings",
        "number_of_orders",
        "number_of_five_star_orders",
        "on_time_rate",
        "courier_tier",
    ]
    write_csv(collected[q2_cols], p(".solutions", "q2_collected.csv"))

    # ---------------- Question 3 ----------------
    fresh("q3", "data")
    q3_cols = q2_cols[:-1] + [
        "number_of_cancellations",
        "number_of_complaints",
        "avg_delivery_minutes",
        "courier_tier",
    ]
    full = collected[q3_cols].sample(frac=1, random_state=11).reset_index(drop=True)
    miss = RNG.random(len(full)) < 0.08
    full.loc[miss, "avg_delivery_minutes"] = np.nan

    cut = int(0.75 * len(full))
    write_csv(full.iloc[:cut], p("q3", "data", "train.csv"))
    write_csv(full.iloc[cut:], p("q3", "data", "test.csv"))

    # ---------------- Question 4 ----------------
    fresh("q4", "data")
    n = len(full)
    a, b = int(0.7 * n), int(0.85 * n)
    tr, va, te = full.iloc[:a].copy(), full.iloc[a:b].copy(), full.iloc[b:].copy()
    labels = (te["courier_tier"] == "Gold").astype(int)

    write_csv(tr, p("q4", "data", "train.csv"))
    write_csv(va, p("q4", "data", "val.csv"))
    write_csv(te.drop(columns=["courier_tier"]), p("q4", "data", "test.csv"))
    write_csv(pd.DataFrame({"courier_tier": labels.to_numpy()}), p(".solutions", "q4_test_labels.csv"))

    print("Round 2 data generated.")
    print(f"  couriers: {N_COURIERS}   orders: {N_ORDERS}")
    print(f"  q3 train/test: {cut}/{n - cut}")
    print(f"  q4 train/val/test: {len(tr)}/{len(va)}/{len(te)}")
    print(f"  Gold rate: {(full['courier_tier'] == 'Gold').mean():.3f}")


if __name__ == "__main__":
    main()
