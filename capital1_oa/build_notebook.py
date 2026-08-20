"""Builds capital_one_oa.ipynb from the cell definitions below."""

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
# Capital One — Data Science Assessment (Simulation)

4 questions, CodeSignal-style. Suggested budget: **~70 minutes total** (Q1 10m, Q2 20m, Q3 20m, Q4 20m).

**Rules of the sim**
- Write your solution in the `# YOUR SOLUTION` cell for each question, then run the grader cell below it.
- Each question has its own folder (`q1/`, `q2/`, ...) and you write your output file into that folder.
- Q3 and Q4 have an 8-second execution limit in the real OA — the grader prints your runtime.
- Don't open `.solutions/` — that's the answer key the graders read.

Regenerate fresh data any time with `python generate_data.py`.
"""),
    code("""
%load_ext autoreload
%autoreload 2

import os, time
import numpy as np
import pandas as pd

import grader  # graders resolve paths relative to this folder, so cwd doesn't matter

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 50)
print("ready")
"""),
    # ------------------------------------------------------------------ Q1
    md("""
---
## Question 1 of 4 — Basic data analysis

You are provided with datasets containing information about taxi drivers and their rides. Perform basic
data analysis and save the results to a CSV file.

Data (in `q1/`):

**`drivers.csv`**
- `driver_id` (int) — unique driver identifier
- `age` (int)
- `second_language` (str) — `"no"` if the driver has none
- `rating` (float) — driver's average rating

**`rides_{i}.csv`** — split into 4 files, `rides_1.csv` … `rides_4.csv`
- `ride_id` (int), `driver_id` (int), `passenger_id` (int), `date` (str)
- `status` (str) — one of `["Rejected by the driver", "Cancelled by the passenger", "Success"]`

**Tasks**
1. **Average driver rating** — mean of the `rating` column. Store as `insight_type: "average_driver_rating"`.
2. **Percentage of drivers with a second language** — share of drivers where `second_language != "no"`, as a
   percentage. Store as `insight_type: "percentage_drivers_with_second_language"`.
3. **Ride success rate** — combine all four `rides_{i}.csv` files, then compute the percentage of rides with
   `status == "Success"`. Store as `insight_type: "ride_success_rate"`.

**Output:** save `q1/analysis_results.csv` with two columns, `insight_type` and `value`, one row per task.
Numeric values are correct if they match to two decimal places.

`q1/tests/data_analysis_tests_data/expected.csv` shows the expected output format and the expected value of
`average_driver_rating`. The other two values there are zero placeholders, not the real answers.
"""),
    code("""
# YOUR SOLUTION — Question 1
_t0 = time.time()

# drivers = pd.read_csv("q1/drivers.csv")
# rides = pd.concat([pd.read_csv(f"q1/rides_{i}.csv") for i in range(1, 5)], ignore_index=True)


# ... write q1/analysis_results.csv

print(f"runtime: {time.time() - _t0:.2f}s")
"""),
    code("""
grader.grade_q1()
"""),
    # ------------------------------------------------------------------ Q2
    md("""
---
## Question 2 of 4 — Feature collection

Data about taxi drivers and their rides, created by **April 15th, 2023**. When calculating any time
features, treat **April 15th, 2023 as today**.

Data (in `q2/`), across 6 files:

**`drivers.csv`** — `driver_id` (int), `car_id` (int), `age` (int), `started_driving_year` (int),
`second_language` (str, `"no"` if none), `rating` (float), `net_worth_of_tips` (float),
`driver_class` (str: `"A class"` / `"B class"`)

**`rides_{i}.csv`** (4 files) — `ride_id`, `driver_id`, `passenger_id`, `date`, `status`,
`car_clearness_upvote_given` (bool), `politeness_upvote_given` (bool), `communication_upvote_given` (bool),
`punctuality_upvote_given` (bool), `complaint_given` (bool)

**`cars.csv`** — `car_id` (int), `model` (str), `manufacture_year` (int), `last_inspection_date` (str)

**Task:** retrieve the needed information about each driver and store it in **`q2/collected.csv`** with columns:

| column | type | notes |
|---|---|---|
| `driver_id` | int | |
| `car_model` | str | |
| `car_manufacture_year` | int | |
| `days_since_inspection` | int | days passed since the last inspection |
| `age` | int | |
| `experience` | int | `2023 - started_driving_year` |
| `second_language` | str | |
| `rating` | float | |
| `net_worth_of_tips` | float | |
| `number_of_upvotes` | int | total upvotes across all four upvote flags, over all of the driver's rides |
| `driver_class` | str | |

Rows and columns may be in any order — the tests are order-agnostic.
"""),
    code("""
# YOUR SOLUTION — Question 2
_t0 = time.time()

# drivers = pd.read_csv("q2/drivers.csv")
# cars = pd.read_csv("q2/cars.csv")
# rides = pd.concat([pd.read_csv(f"q2/rides_{i}.csv") for i in range(1, 5)], ignore_index=True)
# TODAY = pd.Timestamp("2023-04-15")


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

A dataset of taxi drivers and their performance metrics, with columns:

`driver_id` (int), `car_model` (str), `car_manufacture_year` (int), `days_since_inspection` (int),
`age` (int), `experience` (int), `second_language` (str), `rating` (float), `net_worth_of_tips` (float),
`number_of_rejected_rides` (int), `number_of_upvotes` (int), `number_of_complaints` (int),
`number_of_incidents` (int), `driver_class` (str)

Split: **train 70%** at `q3/data/train.csv`, **test 30%** at `q3/data/test.csv`.

**Steps**
- **a.** Fill missing values in `age` with the mean age of the drivers, rounded to the nearest integer.
- **b.** Convert `second_language` and `car_model` to numbers with **ordinal encoding** — codes must start at
  0 and be consecutive integers.
  ✅ `{"Honda Accord": 0, "Ford Fusion": 1, "Hyundai Sonata": 2, "Nissan Altima": 3}`
  ❌ `{"Hyundai Sonata": 1, "Honda Accord": 2, "Ford Fusion": 4, "Nissan Altima": 5}`
- **c.** Normalize `net_worth_of_tips` with **Standard Scaling**.
- **d.** Convert `driver_class`: `"A class"` → 0, `"B class"` → 1.

⚠️ **Do not leak information from the test set into the train set** — fit every statistic (mean age, encoder,
scaler) on train only.

**Output:** `q3/processed_train.csv` and `q3/processed_test.csv`.
Values in `net_worth_of_tips` must be written with **exactly 5 digits after the decimal point**.

**Constraints:** 8 s, 4 GB.
"""),
    code("""
# YOUR SOLUTION — Question 3
_t0 = time.time()

# train = pd.read_csv("q3/data/train.csv")
# test = pd.read_csv("q3/data/test.csv")


# ... write q3/processed_train.csv and q3/processed_test.csv
# hint: df.to_csv(path, index=False, float_format=...) formats every float column --
#       you probably want to format only net_worth_of_tips.

print(f"runtime: {time.time() - _t0:.2f}s  (limit 8s)")
"""),
    code("""
grader.grade_q3()
"""),
    # ------------------------------------------------------------------ Q4
    md("""
---
## Question 4 of 4 — Classifier

Using the dataset from the prior question, train a classifier that predicts whether a driver is
**A class (0)** or **B class (1)**.

Free-form task — any model, any libraries.

**Data (in `q4/`)**
- Training set 70% — `q4/data/train.csv`
- Validation set 15% — `q4/data/val.csv`
- Test set 15% — `q4/data/test.csv` (no `driver_class` column)

**Metrics:** precision and recall, with **B class as the positive class**.
**Goal:** maximize recall while keeping precision relatively high.

**Output:** `q4/predictions.csv`, one column named `driver_class`, one row per test row, in test-set order:

```
driver_class
0
1
0
...
```

Scoring in the real OA shows only the first 10 rows immediately; you submit to see the full score. The
grader below mimics that: it prints the first-10 preview and then the full precision/recall.

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

Re-runs all four graders for a final tally.
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

with open(os.path.join(ROOT, "capital_one_oa.ipynb"), "w") as f:
    json.dump(nb, f, indent=1)
print("wrote capital_one_oa.ipynb")
