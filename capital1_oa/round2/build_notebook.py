"""Builds round2/capital_one_oa_round2.ipynb."""

import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip("\n").splitlines(keepends=True)}


def code(text):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text.strip("\n").splitlines(keepends=True),
    }


cells = [
    md("""
# Capital One — Data Science Assessment (Simulation, Round 2)

Same four-question shape as round 1, different domain (**food-delivery couriers**) and deliberately
different formats: JSON and CSV inputs, a JSON output for Q1, an extra lookup table to join, and a
non-ISO date format.

Suggested budget: **~70 minutes** (Q1 10m, Q2 20m, Q3 20m, Q4 20m). Try it closed-book this time.

Regenerate fresh data with `python generate_data.py`.
"""),
    code("""
%load_ext autoreload
%autoreload 2

import json, os, time
import numpy as np
import pandas as pd

import grader

pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 60)
print("ready")
"""),
    # ------------------------------------------------------------------ Q1
    md("""
---
## Question 1 of 4 — Basic data analysis

You are provided with data about food-delivery couriers and their orders. Perform basic analysis and save
the results to a JSON file. Treat **June 1st, 2024 as today**.

Data (in `q1/`):

**`couriers.json`** — a JSON array of records:
- `courier_id` (int), `age` (int)
- `joined_date` (str, `YYYY-MM-DD`) — the day the courier joined the platform
- `rating` (float)
- `vehicle_type` (str) — one of `["Bicycle", "Car", "E-bike", "Scooter", "Walking"]`

**`orders_{i}.csv`** — split into 3 files, `orders_1.csv` … `orders_3.csv`:
- `order_id` (int), `courier_id` (int), `customer_id` (int), `order_date` (str)
- `status` (str) — one of `["Delivered", "Cancelled by customer", "Unassigned"]`
- `order_value` (float)

**Tasks**
1. **`average_courier_tenure_days`** — mean number of days between each courier's `joined_date` and today.
2. **`percentage_couriers_with_ebike`** — percentage of couriers whose `vehicle_type` is `"E-bike"`.
3. **`median_order_value`** — median `order_value` across **all** orders (combine all three files).
4. **`order_cancellation_rate`** — percentage of all orders with `status == "Cancelled by customer"`.

**Output:** save `q1/analysis_results.json` as a single JSON object mapping each of the four names above to
its numeric value, e.g.

```json
{"average_courier_tenure_days": 0.0, "percentage_couriers_with_ebike": 0.0,
 "median_order_value": 0.0, "order_cancellation_rate": 0.0}
```

Values are correct if they match to two decimal places. `q1/tests/expected_format.json` shows the expected
format and the true value of `average_courier_tenure_days`; the other three are zero placeholders.
"""),
    code("""
# YOUR SOLUTION — Question 1
_t0 = time.time()

# couriers = pd.read_json("q1/couriers.json")
# orders = pd.concat([pd.read_csv(f"q1/orders_{i}.csv") for i in range(1, 4)], ignore_index=True)
# TODAY = pd.Timestamp("2024-06-01")


# ... write q1/analysis_results.json

print(f"runtime: {time.time() - _t0:.2f}s")
"""),
    code("""
grader.grade_q1()
"""),
    # ------------------------------------------------------------------ Q2
    md("""
---
## Question 2 of 4 — Feature collection

Data about couriers and their orders, created by **June 1st, 2024**. When calculating any time features,
treat **June 1st, 2024 as today**.

Data (in `q2/`), across 6 files:

**`couriers.json`** (JSON array) — `courier_id` (int), `vehicle_id` (int), `zone_id` (int), `age` (int),
`joined_date` (str, `YYYY-MM-DD`), `rating` (float), `total_earnings` (float),
`courier_tier` (str: `"Gold"` / `"Standard"`)

**`vehicles.csv`** — `vehicle_id` (int), `vehicle_type` (str), `purchase_year` (int),
`last_service_date` (str — ⚠️ formatted **`DD/MM/YYYY`**)

**`zones.csv`** — `zone_id` (int), `city` (str), `region` (str), `zone_name` (str)

**`orders_{i}.csv`** (3 files) — `order_id`, `courier_id`, `customer_id`, `order_date`,
`status`, `order_value`, `delivery_minutes` (float, empty unless delivered), `rating_given`
(float 1–5, empty unless delivered), `on_time` (bool), `complaint_filed` (bool)

**Task:** collect per-courier information into **`q2/collected.csv`** with columns:

| column | type | notes |
|---|---|---|
| `courier_id` | int | |
| `city` | str | from `zones.csv` |
| `vehicle_type` | str | |
| `vehicle_age_years` | int | `2024 - purchase_year` |
| `days_since_service` | int | days since `last_service_date` |
| `age` | int | |
| `tenure_days` | int | days since `joined_date` |
| `rating` | float | |
| `total_earnings` | float | |
| `number_of_orders` | int | all orders assigned to the courier, any status |
| `number_of_five_star_orders` | int | delivered orders with `rating_given == 5` |
| `on_time_rate` | float | share of the courier's **delivered** orders with `on_time == True`, rounded to 4 decimals; use `0.0` if the courier has no delivered orders |
| `courier_tier` | str | |

Rows and columns may be in any order — the tests are order-agnostic.
"""),
    code("""
# YOUR SOLUTION — Question 2
_t0 = time.time()

# couriers = pd.read_json("q2/couriers.json")
# vehicles = pd.read_csv("q2/vehicles.csv")
# zones = pd.read_csv("q2/zones.csv")
# orders = pd.concat([pd.read_csv(f"q2/orders_{i}.csv") for i in range(1, 4)], ignore_index=True)
# TODAY = pd.Timestamp("2024-06-01")


# ... write q2/collected.csv

print(f"runtime: {time.time() - _t0:.2f}s")
"""),
    code("""
grader.grade_q2()
"""),
    # ------------------------------------------------------------------ Q3
    md("""
---
## Question 3 of 4 — Data preparation

A dataset of couriers and their performance metrics, with columns:

`courier_id` (int), `city` (str), `vehicle_type` (str), `vehicle_age_years` (int),
`days_since_service` (int), `age` (int), `tenure_days` (int), `rating` (float), `total_earnings` (float),
`number_of_orders` (int), `number_of_five_star_orders` (int), `on_time_rate` (float),
`number_of_cancellations` (int), `number_of_complaints` (int), `avg_delivery_minutes` (float),
`courier_tier` (str)

Split: **train 75%** at `q3/data/train.csv`, **test 25%** at `q3/data/test.csv`.

**Steps**
- **a.** Fill missing values in `avg_delivery_minutes` with the **median**, rounded to 2 decimal places.
- **b.** Encode `city` with **ordinal encoding in alphabetical order**, starting at 0 and consecutive
  (`Austin` → 0, `Boston` → 1, …).
- **c.** Encode `vehicle_type` with **one-hot encoding**: add one column per type named
  `vehicle_type_<value>` (e.g. `vehicle_type_Car`) holding 0/1, and drop the original `vehicle_type`
  column. Both output files must have the same one-hot columns.
- **d.** Normalize `total_earnings` with **Min-Max scaling** to the range [0, 1].
- **e.** Convert `courier_tier`: `"Standard"` → 0, `"Gold"` → 1.

⚠️ **No leakage** — every statistic (median, category list, min/max) is fit on **train only**.

**Output:** `q3/processed_train.csv` and `q3/processed_test.csv`.
Values in `total_earnings` must be written with **exactly 4 digits after the decimal point**.

**Constraints:** 8 s, 4 GB.
"""),
    code("""
# YOUR SOLUTION — Question 3
_t0 = time.time()

# train = pd.read_csv("q3/data/train.csv")
# test = pd.read_csv("q3/data/test.csv")


# ... write q3/processed_train.csv and q3/processed_test.csv

print(f"runtime: {time.time() - _t0:.2f}s  (limit 8s)")
"""),
    code("""
grader.grade_q3()
"""),
    # ------------------------------------------------------------------ Q4
    md("""
---
## Question 4 of 4 — Classifier

Train a classifier that predicts whether a courier is **Gold tier (1)** or **Standard tier (0)**.

Free-form — any model, any libraries.

**Data (in `q4/`)**
- Training set 70% — `q4/data/train.csv`
- Validation set 15% — `q4/data/val.csv`
- Test set 15% — `q4/data/test.csv` (no `courier_tier` column)

**Metrics:** precision and recall with **Gold as the positive class**.
**Goal:** maximize **F1** — balance precision and recall rather than pushing one to the extreme.
Roughly 40% of couriers are Gold.

**Output:** `q4/predictions.csv` — one column named `courier_tier`, one row per test row, in test-set order:

```
courier_tier
0
1
0
...
```

The grader prints a first-10-row preview score, then the full precision / recall / F1.

**Constraints:** 8 s, 4 GB.
"""),
    code("""
# YOUR SOLUTION — Question 4
_t0 = time.time()

# train = pd.read_csv("q4/data/train.csv")
# val = pd.read_csv("q4/data/val.csv")
# test = pd.read_csv("q4/data/test.csv")


# ... write q4/predictions.csv

print(f"runtime: {time.time() - _t0:.2f}s  (limit 8s)")
"""),
    code("""
grader.grade_q4()
"""),
    md("""
---
### Run everything
"""),
    code("""
for fn in (grader.grade_q1, grader.grade_q2, grader.grade_q3, grader.grade_q4):
    fn()
    print()
"""),
]

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

with open(os.path.join(ROOT, "capital_one_oa_round2.ipynb"), "w") as f:
    json.dump(nb, f, indent=1)
print("wrote capital_one_oa_round2.ipynb")
